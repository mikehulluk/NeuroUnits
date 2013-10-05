#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------


import re
from string import Template

from .neuroml_xml_data import NeuroUnitsImportNeuroMLNotImplementedException
from .neuroml_xml_data import ChannelMLInfo
from neurounits.misc import SeqUtils
from neurounits import NeuroUnitParser,NeuroUnitParserOptions


class NeuroMLUnitsMode:
    SI ="SI"
    Physiological="PHYSIO"

class Name:
    Voltage = "__V__"
    ReversalPotential = "VREV"
    OpenConductance = "GMAX"
    MembraneCurrent = "I"
    PropGatesOpen = "GATEPROP"
    Conductance = "g"
    Temperature = "celsius"




def build_gate_q10_settings_dict(chlmlinfo):
    eqns = []
    # Add the Q10 settings:
    q10gateadjustments = {None: 'temp_adj'}
    if not chlmlinfo.q10settings:
        eqns.append('%s  = 1.0' % q10gateadjustments[None])
    else:

        for setting in chlmlinfo.q10settings:

            var_name = 'temp_adj'
            if setting.gate:
                var_name += '_' + setting.gate

            q10gateadjustments[setting.gate] = var_name
            if setting.mode == "q10_factor":
                eqns.append("%s = pow( base={%f},exp=((celsius - %f )/ 10 ))"%( var_name, float(setting.q10factor), float(setting.experimental_temp) ) )

            elif setting.mode == "fixed_q10":
                eqns.append("%s = %f"%( var_name, float(setting.q10factor) ) )
            else:
                assert False

    # Hack to allow direct access to q10 ssettings in eqns:
    for g in chlmlinfo.gates:
        if not g.name in q10gateadjustments:
            q10gateadjustments[g.name] = "temp_adj_%s" % g.name
            eqns.append(" %s = %s"%(q10gateadjustments[g.name], q10gateadjustments[None]) )
    return q10gateadjustments, eqns







def _build_gate_inftau(g, q10tempadjustmentName, neuroml_dt):

            assert len(g.time_courses) == 1 and len(g.steady_states) == 1

            eqns = []
            initial_conditions = []
            state_name = g.name
            term_name_inf = "%s_%s"%(state_name, 'inf' )
            term_name_tau = "%s_%s"%(state_name, 'tau' )

            def remap_gate_eqnI(s):
                s = re.sub(r"""\bV\b""", '__VGate__',s)
                s = re.sub(r"""\bv\b""", '__VGate__',s)
                return s

            tc = SeqUtils.expect_single(g.time_courses)
            ss = SeqUtils.expect_single(g.steady_states)
            tc_eqn = '%s =  ( %s) * (%s)' % ( term_name_tau, remap_gate_eqnI(tc.getEqn()), neuroml_dt )
            ss_eqn = '%s =  %s' % ( term_name_inf, remap_gate_eqnI( ss.getEqn())  )
            state_eqn = "%s' = (%s-%s)/(%s) " % ( state_name, term_name_inf,state_name,term_name_tau)

            # Add the equations
            eqns.extend([tc_eqn, ss_eqn,state_eqn, ])

            # Add the steddy-state
            initial_conditions.append( (state_name,term_name_inf) )
            return eqns, initial_conditions


def _build_gate_alphabetainftau(g, q10tempadjustmentName, neuroml_dt):

        if len( g.openstates) != 1 or len( g.closedstates) != 1 or len(g.transitions) != 2:
            raise NeuroUnitsImportNeuroMLNotImplementedException('Non-Standard Gate/Transtions setup')


        state_name = g.name
        alphaTr = SeqUtils.filter_expect_single(g.transitions, lambda s: s.name=="alpha")
        betaTr = SeqUtils.filter_expect_single(g.transitions, lambda s: s.name=="beta")
        term_name_alpha = "%s_%s"%(state_name, 'alpha' )
        term_name_beta = "%s_%s"%(state_name, 'beta' )
        term_name_inf = "%s_%s"%(state_name, 'inf' )
        term_name_tau = "%s_%s"%(state_name, 'tau' )

        def remap_gate_eqn(s):

            # Remap Alpha/Beta terms into the appropriate Units
            # when they are used in inf/tau equations:
            alpha_repl = "((%s) * (%s)  )"%(term_name_alpha, neuroml_dt)
            beta_repl =  "((%s) * (%s)  )"%(term_name_beta, neuroml_dt)
            s = s.replace('alpha',alpha_repl).replace('beta',beta_repl)

            # Remap voltage terms to __VGATE__ (since they might be subject
            # to offset later on:
            s = re.sub(r"""\bV\b""", '__VGate__',s)
            s = re.sub(r"""\bv\b""", '__VGate__',s)
            return s



        # Write the alpha/beta terms:
        e1 = '%s =  (%s) * (1/%s)' % ( term_name_alpha, remap_gate_eqn( alphaTr.getEqn() ), neuroml_dt )
        e2 = '%s =  (%s) * (1/%s)' % ( term_name_beta,  remap_gate_eqn( betaTr.getEqn() ), neuroml_dt )


        # Time courses should always be divided by rate_adjustment term!
        if len(g.time_courses) != 0:
            tc = SeqUtils.expect_single(g.time_courses)
            tc_eqn = '%s =  %s * (1/%s) *(%s)' % ( term_name_tau, remap_gate_eqn(tc.getEqn() ),q10tempadjustmentName,neuroml_dt )
        else:
            tc_eqn = '%s =  1/(%s* (%s+%s))' % ( term_name_tau, q10tempadjustmentName, term_name_alpha,term_name_beta )

        if len(g.steady_states) != 0:
            ss = SeqUtils.expect_single(g.steady_states)
            ss_eqn = '%s =  %s' % ( term_name_inf, remap_gate_eqn( ss.getEqn() )  )
        else:
            ss_eqn = '%s =  %s/(%s+%s)' % ( term_name_inf, term_name_alpha,term_name_alpha,term_name_beta )

        # The state-equations
        state_eqn = "%s' = (%s-%s)/(%s) " % ( state_name, term_name_inf,state_name,term_name_tau)


        # Set the initial value of the state-variable to be the same
        # as the steady-state value:
        #initial_cond = "<=> INITIAL %s:%s" % (state_name,term_name_inf)

        return [ e1,e2,tc_eqn,ss_eqn, state_eqn], [(state_name,term_name_inf), ]
        #initial_cond]

















def build_component( chlmlinfo, componentname=None ):

    assert type(chlmlinfo) == ChannelMLInfo

    if not componentname:
        componentname = chlmlinfo.name

    unit_mode = {
                'Physiological Units': NeuroMLUnitsMode.Physiological,
                "SI Units":  NeuroMLUnitsMode.SI
                }[chlmlinfo.units]


    # Some sanity checks on what is supported:
    # ------------------------------------------
    # Check we are dealing with an IV law, not an IAF type mechanism:
    if chlmlinfo.iv_cond_law and chlmlinfo.iv_cond_law != 'ohmic':
        raise NeuroUnitsImportNeuroMLNotImplementedException("Non-IV Cond law-type Channels")

    if chlmlinfo.iv_default_gmax is None or chlmlinfo.iv_default_erev is None:
        raise NeuroUnitsImportNeuroMLNotImplementedException("Can't find default reversal potentials/conductances")

    if chlmlinfo.unsupported_tags is not None:
        raise NeuroUnitsImportNeuroMLNotImplementedException(chlmlinfo.unsupported_tags)

    if chlmlinfo.parameters:
        raise NeuroUnitsImportNeuroMLNotImplementedException("Can't deal with parameters")

    neuroml_dt = {
        NeuroMLUnitsMode.Physiological: "{1ms}",
        NeuroMLUnitsMode.SI: "{1s}",
    }[unit_mode]

    neuroml_v_unit = {
        NeuroMLUnitsMode.Physiological: "{1mV}",
        NeuroMLUnitsMode.SI: "{1V}",
    }[unit_mode]



    eqns = []
    initial_conditions = []

    # Build the Q10 Info:
    q10gateadjustments, q10_eqns = build_gate_q10_settings_dict(chlmlinfo)
    eqns.extend(q10_eqns)


    # Build the conductance and current equations:
    eqns.append( '%s =  %s * %s' % ( Name.Conductance, Name.OpenConductance,  Name.PropGatesOpen ) )
    eqns.append( '%s =  %s * ( (%s) - (%s) ) '% ( Name.MembraneCurrent, Name.Conductance, Name.Voltage, Name.ReversalPotential ) )

    gate_prop_names = dict( [ (gate, '%s' % gate.name) for gate in chlmlinfo.gates ] )
    gate_prop_terms = dict( [ (gate, '*'.join( [ gate_prop_names[gate] ] * gate.instances )) for gate in chlmlinfo.gates ] )

    if gate_prop_terms:
        eqns.append( '%s = %s'% (Name.PropGatesOpen, '*'.join(gate_prop_terms.values() ) ) )
    else:
        eqns.append( '%s = 1.0'% (Name.PropGatesOpen ) )

    # Build Eqns for individual gates:
    for g in chlmlinfo.gates:

        q10tempadjustmentName = q10gateadjustments.get(g.name,q10gateadjustments[None])


        # Gate with alpha/beta rate variables specified:
        if g.transitions:
            gate_eqns, _initial_conditions = _build_gate_alphabetainftau(g=g, q10tempadjustmentName=q10tempadjustmentName, neuroml_dt=neuroml_dt)
            eqns.extend(gate_eqns)
            initial_conditions.extend( _initial_conditions )

        # Gate specified as an inf-tau value:
        elif len(g.time_courses) == 1 and len(g.steady_states) == 1:
            gate_eqns, _initial_conditions = _build_gate_inftau(g=g, q10tempadjustmentName=q10tempadjustmentName, neuroml_dt=neuroml_dt)
            eqns.extend(gate_eqns)
            initial_conditions.extend( _initial_conditions )

        else:
            raise NeuroUnitsImportNeuroMLNotImplementedException('Non-Standard Gate/Transtions')



    #Voltage Offsets:
    vOffset = None
    if chlmlinfo.offset:
        vOffset = "( %f * %s )"%( chlmlinfo.offset, neuroml_v_unit )
    vOffsetTerm = "-%s" %vOffset if vOffset is not None else ""


    # OK, use regular expressions to remap variables
    # to the variable with the unit:
    remaps = [
        lambda e: re.sub(r"""\bcelsius\b""", "(celsius/{1K})", e),
        lambda e: re.sub(r"""\b__VGate__\b""", "((V %s)/%s)"%(vOffsetTerm,neuroml_v_unit),e ),
        lambda e: re.sub(r"""\b__V__\b""", "(V)", e ),
                ]


    # Apply the remappings:
    for r in remaps:
        eqns = [ r(e) for e in eqns]



    io_string = Template( """
    <=> PARAMETER    $OpenConductance : (S/m2)
    <=> PARAMETER    $ReversalPotential : (mV)
    <=> OUTPUT       $MembraneCurrent :(A/m2)    METADATA {"mf":{"role":"TRANSMEMBRANECURRENT"} }
    <=> INPUT        V:(V)       METADATA {"mf":{"role":"MEMBRANEVOLTAGE"} }
    <=> INPUT        $Temperature :(K) METADATA {"mf":{"role":"TEMPERATURE"} } """).substitute(**Name.__dict__)


    import_string = """
        from std.math import exp
        from std.math import pow
        from std.math import fabs """


    print initial_conditions

    initial_conditions_defaults = {
            'm_inf': 0.0,
            'h_inf': 0.0,
            }

    initial_blk = """
        initial {
            %s
        }
    """ % "\n\t\t".join( ["%s=%s"%(ic[0],initial_conditions_defaults.get(ic[1],ic[1]) ) for ic in initial_conditions] )


    neuroEqn = """
    define_component %s{
        %s
        %s
        %s
        %s
    }"""%( componentname, import_string, "\n\t\t".join(eqns), initial_blk, io_string  )


    neuroEqn = "\n".join( [l for l in neuroEqn.split("\n") if l.strip() ] )

    options = NeuroUnitParserOptions(
                allow_unused_parameter_declarations=True,
                allow_unused_suppliedvalue_declarations=True)
    eqnset = NeuroUnitParser.Parse9MLFile(text=neuroEqn, options=options  )


    default_params = {
        NeuroMLUnitsMode.Physiological:   {
                "GMAX": NeuroUnitParser.QuantitySimple( "%s mS/cm2" %  ( chlmlinfo.iv_default_gmax ) ),
                "VREV": NeuroUnitParser.QuantitySimple( "%s mV"%       ( chlmlinfo.iv_default_erev ) ),
                },
        NeuroMLUnitsMode.SI:   {
                "GMAX": NeuroUnitParser.QuantitySimple( "%s S/m2" % ( chlmlinfo.iv_default_gmax ) ),
                "VREV": NeuroUnitParser.QuantitySimple( "%s V"    % ( chlmlinfo.iv_default_erev ) ),
                },
    }[unit_mode]

    return eqnset, default_params


