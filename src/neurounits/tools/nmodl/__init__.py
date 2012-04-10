#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
import string

from neurounits.visitors import ASTVisitorBase
from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate 

from neurounits.unit_errors import panic
from neurounits import ast 
from neurounits.units_wrapper import NeuroUnitParser
from neurounits.io_types import IOType



class MechanismType:
    Point = "Point"
    Distributed = "Distributed"
    
class NeuronSuppliedValues:
    Time = "Time"
    MembraneVoltage = "MembraneVoltage"
    Temperature = "Temperature"


class NEURON():
    current_units = {
            MechanismType.Distributed: NeuroUnitParser.Unit("mA/cm2"), 
            MechanismType.Point: NeuroUnitParser.Unit("nA"), 
            }
    #supplied_value_names = {NeuronSuppliedValues.MembraneVoltage : 'v', NeuronSuppliedValues.Time: 't' }
    supplied_value_names = {NeuronSuppliedValues.MembraneVoltage : 'v', NeuronSuppliedValues.Time: 't', NeuronSuppliedValues.Temperature: 'celsius'  }
    supplied_value_units= {NeuronSuppliedValues.MembraneVoltage : NeuroUnitParser.Unit("mV"), NeuronSuppliedValues.Time: NeuroUnitParser.Unit("ms"), NeuronSuppliedValues.Temperature: NeuroUnitParser.Unit("K") }
    
    
    

class ModFileContents(object):
    def __init__(self):
        self.section_NEURON = []
        self.section_UNITS_units = []
        self.section_UNITS_convs = []
        self.section_UNITS_constants = []
        self.section_PARAMETER = []
        self.section_ASSIGNED = []
        self.section_STATE = []
        self.section_STATE_locals = []
        self.section_STATE_init = []
        self.section_INITIAL = []
        self.section_BREAKPOINT_si_to_natural = []
        self.section_BREAKPOINT_si_assignments = []
        self.section_BREAKPOINT_si_to_nrn = []
        self.section_DERIVATIVE = []
        self.section_FUNCTIONS = []
        self.section_NETRECEIVES = []

    def to_text(self):
        
        
        
        
        std_sects = [
        ( self.section_NEURON,   'NEURON' ),
        ( self.section_UNITS_units + self.section_UNITS_convs+self.section_UNITS_constants,    'UNITS' ),
        ( self.section_PARAMETER,'PARAMETER' ),
        ( self.section_ASSIGNED, 'ASSIGNED' ),
        ( self.section_STATE_locals +[''] + self.section_STATE_init  +[''] + self.section_STATE ,    'STATE' ),
        
        ( self.section_INITIAL,  'INITIAL' ),
        ( ["SOLVE states METHOD derivimplicit" if self.section_STATE != [] else ""]+ self.section_BREAKPOINT_si_assignments +[""]+ self.section_BREAKPOINT_si_to_natural+[""]+self.section_BREAKPOINT_si_to_nrn,  'BREAKPOINT' ),
        ( self.section_DERIVATIVE,  'DERIVATIVE states' ),
        ]
        
        
        
        def split_if_long(l):
            max_length = 500
            if len(l) < max_length:
                return l
            else:
                breakPoint = l.rfind(" ", 0, max_length)
                assert breakPoint != -1, "Unable to find breakpoint when splitting string"
                st1, st2 = l[:breakPoint], l[breakPoint:]
                return "\n".join( [st1]+[split_if_long(st2)])
            
        def newlineandtabjoinlines(lines): return "\n".join(["    %s"% split_if_long(sl) for sl in lines] )
        def buildersection(s,t): return "%s\n{\n%s\n}\n"%(t, newlineandtabjoinlines(lines=s) ) if len(s) != 0 else ""

        t1 = "\n".join( [buildersection(s,t) for (s,t) in std_sects]  )
        
        t2 = "\n\n".join(self.section_FUNCTIONS)
        t3  = "\n\n".join(self.section_NETRECEIVES)
        return t1 + "\n\n" + t2 + "\n\n" + t3


class ASTActionerDefaultIgnoreMissing(ASTActionerDefault):
    
    def __init__(self, **kwargs):
        ASTActionerDefault.__init__(self, **kwargs)
    
    def ActionNode(self, n, **kwargs):
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

class VariableInNeuron(object):
    def __init__(self, raw_name, in_si_name):
        self.raw_name = raw_name
        self.in_si_name = in_si_name



def unit_to_str_no_multiplier(u):
    terms = [ ("meter", u.meter),
              ("kilogram", u.kilogram),
              ("second", u.second),
              ("ampere", u.ampere),
              ("kelvin", u.kelvin),
              ("cd", u.candela),
            ]
    pos_terms = " ".join( ["%s%d"%(t1,t2) for (t1,t2) in terms if t2 > 0] )
    neg_terms = " ".join( ["%s%d"%(t1,t2*-1) for (t1,t2) in terms if t2 < 0] )
    
    if pos_terms == "":
        pos_terms = "1"
    if neg_terms != "":
        neg_terms = "/" + neg_terms 
    
    return pos_terms + neg_terms
    
    




def UnitToTuple(u):
    return (u.meter, u.kilogram, u.second, u.ampere,u.kelvin,u.candela,u.powerTen)

class Namer(object):
    def __init__(self):
        self.current = "unita"
    
    def getNext(self):
        self.current += 'a'
        return self.current



class UnitsToStringDatabase(object):
    
    def __init__(self):
        self.unittuple_to_nmmodl_name = {}
        self.unittuple_to_unit = {}
        self.namer = Namer()
        
    def get_unit_nmodlname(self, u):
        k = UnitToTuple(u)
        if not k in self.unittuple_to_nmmodl_name:
            self.unittuple_to_nmmodl_name[k] =self.namer.getNext() 
            self.unittuple_to_unit[k] = u
        return self.unittuple_to_nmmodl_name[k]
        
    def write_unit_defs_to_nmodl(self, modfile):
        for k,v in self.unittuple_to_nmmodl_name.iteritems():
            u = self.unittuple_to_unit[k]
            nmodl_def = "1%+d %s"%( u.powerTen, unit_to_str_no_multiplier(u)  )
            p_def = '(%s) = (%s)' % (v, nmodl_def ) 
            modfile.section_UNITS_units.append( p_def )



def unit_to_si(u):
    return u.unit_to_si()
    
class VariableInNeuronUnits(object):
    unit_name_dict = {}
    def __init__(self, o):
        self.natural_units = o.get_unit()
    def is_dimensionless(self, allow_non_zero_power_of_ten):
        return self.natural_units.is_dimensionless(allow_non_zero_power_of_ten=allow_non_zero_power_of_ten)
    def get_si_unit(self,):
        return unit_to_si(self.natural_units)


class ModFileStringBuilder(object):

    @classmethod
    def AssignedRaw(cls, n, varnames, varunits, units_db ):
        if varunits[n].is_dimensionless(allow_non_zero_power_of_ten=False):
            return '%s'% varnames[n].raw_name 
        else:
            raw_unit_name_nmmodl = units_db.get_unit_nmodlname( varunits[n].natural_units)
            return '%s (%s) '%( varnames[n].raw_name, raw_unit_name_nmmodl) 

    @classmethod
    def AssignedSI(cls, n, varnames, varunits, units_db ):
        if varunits[n].is_dimensionless(allow_non_zero_power_of_ten=False):
            return '%s'% varnames[n].in_si_name 
        else:
            si_unit_name_nmmodl = units_db.get_unit_nmodlname( varunits[n].get_si_unit())
            return '%s (%s) '%( varnames[n].in_si_name, si_unit_name_nmmodl) 
        
    @classmethod
    def StateSI(cls,n,varnames,varunits,units_db):
        return cls.AssignedSI(n=n,varnames=varnames,varunits=varunits,units_db=units_db)

    @classmethod
    def ParameterRaw(cls, n, varnames, varunits, units_db ):
        if varunits[n].is_dimensionless(allow_non_zero_power_of_ten=False):
            return '%s = 0'% varnames[n].raw_name 
        else:
            raw_unit_name_nmmodl = units_db.get_unit_nmodlname( varunits[n].natural_units)
            return '%s = 0 (%s) '%( varnames[n].raw_name, raw_unit_name_nmmodl) 

    @classmethod
    def si_to_raw_assignment(cls, n, varnames, varunits, units_db ):
        if varunits[n].is_dimensionless(allow_non_zero_power_of_ten=False):
            assert varunits[n].natural_units.powerTen == 0
            return '%s = %s'%( varnames[n].raw_name, varnames[n].in_si_name) 
        else:
            return  '%s = (1e%d) * %s'%( varnames[n].raw_name, -1*varunits[n].natural_units.powerTen, varnames[n].in_si_name ) 
    @classmethod
    def raw_to_si_assignment(cls, n, varnames, varunits, units_db ):
        if varunits[n].is_dimensionless(allow_non_zero_power_of_ten=False):
            assert varunits[n].natural_units.powerTen == 0
            return '%s = %s'%( varnames[n].in_si_name, varnames[n].raw_name) 
        else:
            return  '%s = (1e%d) * %s'%( varnames[n].in_si_name, varunits[n].natural_units.powerTen, varnames[n].raw_name ) 

    @classmethod
    def constant_def_si(cls, n, varnames, varunits, units_db ):
        v = n.value.magnitude * 10 ** n.value.units.powerTen
        si_unit = varunits[n].get_si_unit()
        si_unit_name_nmmodl = units_db.get_unit_nmodlname( si_unit )
        return  '%s = %e (%s) '%( varnames[n].in_si_name, v, si_unit_name_nmmodl )




class ParameterWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionParameter(self, n, modfilecontents, varnames, varunits,nmodl_units_to_str_db,  **kwargs):
        modfilecontents.section_INITIAL.append(   ModFileStringBuilder.raw_to_si_assignment( n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db  ) )
        modfilecontents.section_ASSIGNED.append(  ModFileStringBuilder.AssignedSI(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db ) )
        modfilecontents.section_PARAMETER.append( ModFileStringBuilder.ParameterRaw(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db ) )

class StateWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ])

    def ActionStateVariable(self, n, modfilecontents, varnames, varunits, nmodl_units_to_str_db, **kwargs):
        modfilecontents.section_BREAKPOINT_si_to_natural.append(   ModFileStringBuilder.si_to_raw_assignment( n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db  ) )
        modfilecontents.section_ASSIGNED.append( ModFileStringBuilder.AssignedRaw(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db ) )
        modfilecontents.section_STATE.append( ModFileStringBuilder.StateSI(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db ) )

    def ActionEqnTimeDerivative(self, n, modfilecontents, varnames, varunits, nmodl_units_to_str_db,  **kwargs):
        #Assigned values **must** be expanded here, otherwise the gradient function will be wrong!!
        rhs = CString.Build(n.rhs, varnames=varnames, varunits=varunits,   expand_assignments=True)
        p_def = "%s' = (0.001) * %s" %( varnames[n.lhs].in_si_name, rhs )
        modfilecontents.section_DERIVATIVE.append( p_def )



class SuppliedValuesWriter(ASTActionerDefaultIgnoreMissing):
    
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def ActionSuppliedValue(self, n, modfilecontents, varnames, varunits,nmodl_units_to_str_db, buildparameters,  **kwargs):

        assert n in buildparameters.supplied_values,  " Can't find %s in supplied values[%s]"%(n.symbol,  ",".join([s.symbol for s in buildparameters.supplied_values]) )
        
        what = buildparameters.supplied_values[n]
        
        nrn_name = NEURON.supplied_value_names[what]
        nrn_unit = NEURON.supplied_value_units[what]

        if what == NeuronSuppliedValues.MembraneVoltage:
            modfilecontents.section_ASSIGNED.append( 'v (millivolt)')
        
        funcunit_modl =  nmodl_units_to_str_db.get_unit_nmodlname(unit_to_si(nrn_unit))
        func_tmpl = "FUNCTION $funcname () ($funcunit) { $funcname = $assStr } "
        func = string.Template(func_tmpl) .substitute( funcname=varnames[n].in_si_name,
                                                                        assStr='(1e%d) * %s'%(  nrn_unit.powerTen, nrn_name ) , 
                                                                        funcunit=funcunit_modl )
        modfilecontents.section_FUNCTIONS.append( func )




class ConstantWriter(ASTActionerDefaultIgnoreMissing):

    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])
    
    def ActionConstant(self, n, modfilecontents, varnames, varunits,nmodl_units_to_str_db,  **kwargs ):
        modfilecontents.section_PARAMETER.append( ModFileStringBuilder.constant_def_si( n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db  ) )

    def ActionSymbolicConstant(self, n, modfilecontents, varnames, varunits, nmodl_units_to_str_db, **kwargs ):
        modfilecontents.section_PARAMETER.append( ModFileStringBuilder.constant_def_si( n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db  ) )


class AssignmentWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def ActionEqnAssignment(self, n, modfilecontents, varnames, varunits, nmodl_units_to_str_db, **kwargs):
        rhs = CString.Build(n.rhs, varnames=varnames, varunits=varunits)
        p_def = "%s = %s" %( varnames[n.lhs].in_si_name, rhs )
        modfilecontents.section_BREAKPOINT_si_assignments.append( p_def )

    def ActionAssignedVariable(self, n, modfilecontents, varnames, varunits,nmodl_units_to_str_db,  **kwargs):
        modfilecontents.section_ASSIGNED.append( ModFileStringBuilder.AssignedSI(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db )   )
        modfilecontents.section_ASSIGNED.append( ModFileStringBuilder.AssignedRaw(n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db ) )
        modfilecontents.section_BREAKPOINT_si_to_natural.append(   ModFileStringBuilder.si_to_raw_assignment( n,varnames=varnames,varunits=varunits,units_db=nmodl_units_to_str_db  ) )


class FunctionWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self,):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionFunctionDef(self, o, modfilecontents, varnames, varunits,nmodl_units_to_str_db, **kwargs):
        
        func_def_tmpl = """
            FUNCTION $func_name ($func_params) ($func_unit)
            {
                $func_name = $result_string 
            }"""
        
        func_def = string.Template(func_def_tmpl).substitute( {'func_name' :  varnames[o].raw_name,
                                                               'func_params' : ",".join( [ self.getParameterString(p,varnames=varnames,varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db ) for p in o.parameters.values()] ),
                                                               'result_string' : CString().Visit(o.rhs, varnames=varnames, varunits=varunits ),
                                                               'func_unit' : nmodl_units_to_str_db.get_unit_nmodlname(varunits[o].get_si_unit() ),
                                                                }  )
        modfilecontents.section_FUNCTIONS.append(func_def)
        
        
    
    def getParameterString(self, p,varnames,varunits, nmodl_units_to_str_db ):
        nmodl_unit_string = nmodl_units_to_str_db.get_unit_nmodlname(varunits[p].get_si_unit() )
        return varnames[p].raw_name + "(" + nmodl_unit_string + ")"




class OnEventWriter(ASTActionerDefaultIgnoreMissing):

    def ActionOnEvent(self, o, modfilecontents, varnames, varunits,nmodl_units_to_str_db, buildparameters,  **kwargs):
        
        if o != buildparameters.event_function:
            return 
        
        # No Arguments:
        assert len( o.parameters ) == 0
        tmpl = """NET_RECEIVE( weight ) \n {    $contents \n}"""
        
        contents = "\n".join( [ "" + self.DoActionOnEventAssignment(a, modfilecontents, varnames, varunits,nmodl_units_to_str_db, **kwargs ) for a in o.actions ] )
        txt = string.Template( tmpl).substitute( contents=contents)        
        modfilecontents.section_NETRECEIVES.append(txt)

    def DoActionOnEventAssignment(self, o, modfilecontents, varnames, varunits,nmodl_units_to_str_db, **kwargs):
        rhs = CString.Build(o.rhs, varnames=varnames, varunits=varunits)
        return  "%s = %s" %( varnames[o.lhs].in_si_name, rhs )





            

class NeuronBlockWriter(object):
    def __init__(self,  eqnset,  eqnset_build_parameters,  modfilecontents,  varnames, varunits,  nmodl_units_to_str_db):
        
        # Heading
        if eqnset_build_parameters.mechanismtype == MechanismType.Point:
            modfilecontents.section_NEURON.append("POINT_PROCESS %s"%eqnset_build_parameters.suffix )
        elif eqnset_build_parameters.mechanismtype == MechanismType.Distributed:
            modfilecontents.section_NEURON.append("SUFFIX %s"%eqnset_build_parameters.suffix )
        else:
            assert False
    

        current_unit_in_nrn = NEURON.current_units[eqnset_build_parameters.mechanismtype]        
        # Currents:
        for current in eqnset_build_parameters.currents:
            modfilecontents.section_NEURON.append("NONSPECIFIC_CURRENT %s"%current.get_neuron_name())
            
            current_name_nmodl  = current.get_neuron_name()
            current_unit_nmodl = nmodl_units_to_str_db.get_unit_nmodlname(current_unit_in_nrn) 
            modfilecontents.section_ASSIGNED.append("%s (%s)"%(current_name_nmodl, current_unit_nmodl ) )
            modfilecontents.section_BREAKPOINT_si_to_nrn.append("%s = (%E) * %s "%(current_name_nmodl,  10**(current_unit_in_nrn.powerTen*-1), varnames[current.obj].in_si_name) )



class NeuronInterfaceWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )
    
    def ActionAssignedVariable(self, n, modfilecontents, varnames, varunits,nmodl_units_to_str_db,  **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(varnames[n].raw_name) )
        modfilecontents.section_NEURON.append("RANGE %s_in_si"%(varnames[n].raw_name) )
        
    def ActionStateVariable(self, n, modfilecontents, varnames, varunits, nmodl_units_to_str_db, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(varnames[n].raw_name) )
        modfilecontents.section_NEURON.append("RANGE %s_in_si"%(varnames[n].raw_name) )




class BuildParameters(object):
    def __init__(self,  mechanismtype, currents,   supplied_values,  suffix, event_function=None ):
        self.mechanismtype = mechanismtype
        self.currents = currents
        self.supplied_values = supplied_values
        self.suffix = suffix
        self.event_function = event_function
        
class NeuronMembraneCurrent(object):
    def __init__(self,  symbol,  obj):
        self.symbol = symbol
        self.obj = obj
    
    def get_neuron_name(self):
        return self.symbol + "_tonrn"
    
    def getCurrentType(self):

        if self.obj.get_unit().is_compatible( NEURON.current_units[MechanismType.Point] ):
            return MechanismType.Point
        elif self.obj.get_unit().is_compatible( NEURON.current_units[MechanismType.Distributed] ):
            return MechanismType.Distributed
        else:
            assert False, "Unknown type: %s"% self.obj.get_unit()
        






def MakeBuildParameters(eqnset):

    currents = []
    supplied_values = {}
    
    for io_info in [ io_info for io_info in eqnset.io_data if io_info.iotype in ( IOType.Output, IOType.Input)    ]:
        if not io_info.metadata or not 'mf' in io_info.metadata:
            continue
        role = io_info.metadata['mf'].get('role', None)
        if role:
            obj = eqnset.get_terminal_obj( io_info.symbol)
            
            # Outputs:
            if role == "TRANSMEMBRANECURRENT":
                assert io_info.iotype== IOType.Output
                currents.append( NeuronMembraneCurrent( obj=obj,  symbol=obj.symbol))
            
            # Inputs (Supplied Values):
            elif role == "MEMBRANEVOLTAGE":
                assert io_info.iotype== IOType.Input
                supplied_values[obj] = NeuronSuppliedValues.MembraneVoltage
            elif role == "TIME":
                assert io_info.iotype== IOType.Input
                supplied_values[obj] = NeuronSuppliedValues.Time
            elif role == "TEMPERATURE":
                assert io_info.iotype== IOType.Input
                supplied_values[obj] = NeuronSuppliedValues.Temperature
            else:
                assert False
    
    if not currents:
        raise ValueError('Mechanism does not expose any currents! %s'% eqnset.name)
    
    # PointProcess or Distributed  Process:
    mech_type = currents[0].getCurrentType()
    for c in currents:
        assert mech_type == c.getCurrentType(),  'Mixed Current types [Distributed/Point]'
    
    
    # Event Handling:
    zero_arg_events = [ ev for ev in eqnset.on_events if len(ev.parameters) == 0 ]
    if len(zero_arg_events) == 0:
        event_function= None
    elif len(zero_arg_events) == 1:
        event_function= zero_arg_events[0]
    else:
        raise ValueError("Multiple Zero-Param Events")
    
    
    return BuildParameters(mechanismtype=mech_type, currents=currents, supplied_values=supplied_values, suffix="nmmodl"+eqnset.name, event_function=event_function  )
    

class NMODLInfo(object):
    def __init__(self,buildparameters, varnames, varunits, eqnset):
        self.buildparams = buildparameters
        self.varnames = varnames
        self.varunits = varunits
        self.eqnset = eqnset

        self.available_records = {}
        for k,v in eqnset.getAssignedVariablesDict().iteritems():
            self.available_records[k] = self.varunits[v].natural_units
        for k,v in eqnset.getStateVariablesDict().iteritems():
            self.available_records[k] = self.varunits[v].natural_units
            
        self.parameters = {}
        for k,v in eqnset.getParametersDict().iteritems():
            self.parameters[k] = self.varunits[v].natural_units
        






def WriteToNMODL(eqnset, buildparameters=None ):
    buildparameters = buildparameters or MakeBuildParameters(eqnset)

    # Work out names for the variables:
    varnames = TerminalSymbolNameDict(eqnset)
    varunits = TerminalSymbolUnitDict(eqnset)
    nmodl_units_to_str_db =  UnitsToStringDatabase()
    m = ModFileContents()
    
    
    # Write the header:
    NeuronBlockWriter(eqnset=eqnset,  eqnset_build_parameters=buildparameters,  modfilecontents=m,  varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db )
    NeuronInterfaceWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    
    # Write the sections (order is important for Assignment Block):
    ParameterWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    SuppliedValuesWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db, buildparameters=buildparameters)
    AssignmentWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    StateWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    FunctionWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    ConstantWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db)
    OnEventWriter().Visit(eqnset,modfilecontents=m, varnames=varnames, varunits=varunits, nmodl_units_to_str_db=nmodl_units_to_str_db, buildparameters=buildparameters)
    
    # Write the units in use to the mod-file
    nmodl_units_to_str_db.write_unit_defs_to_nmodl(m)


    txt = m.to_text()
    
    nmodl_info = NMODLInfo(buildparameters=buildparameters, varnames=varnames, varunits=varunits, eqnset=eqnset)

    return txt, nmodl_info


















class TerminalSymbolNameDict(ASTActionerDefaultIgnoreMissing):
    def __init__(self,eqnset):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ])
        self.dct = {}
        self.Visit(eqnset)

    def __getitem__(self,k):
        #print 'Getting', k.symbol
        return self.dct[k]

    def generate_unused_name(self,desired_name):
        return desired_name

    def generate_neuron_variable_names(self, n):
        return VariableInNeuron( raw_name= self.generate_unused_name(n), 
                                 in_si_name=self.generate_unused_name(n+"_in_si") )

    def ActionParameter(self,n,**kwargs):
        self.dct[n] = self.generate_neuron_variable_names(n.symbol)
        
    def ActionStateVariable(self,n,**kwargs):
        self.dct[n] = self.generate_neuron_variable_names(n.symbol)
        
    def ActionAssignedVariable(self,n,**kwargs):
        self.dct[n] = self.generate_neuron_variable_names(n.symbol)

    def ActionBuiltInFunction(self, n, **kwargs):
        self.dct[n] = self.generate_neuron_variable_names(n.funcname)

    def ActionFunctionDef(self, n, **kwargs):
        self.dct[n] = self.generate_neuron_variable_names("func_"+n.funcname)

    def ActionFunctionDefParameter(self, n, **kwargs):
        self.dct[n] = self.generate_neuron_variable_names("funcparam_"+n.symbol)

    def ActionSuppliedValue(self,n,**kwargs):
        self.dct[n] = self.generate_neuron_variable_names("func_for_"+n.symbol )

    def ActionConstant(self,n,**kwargs):
        s = "const%d"%len(self.dct)
        self.dct[n] = self.generate_neuron_variable_names(s)
        
    def ActionSymbolicConstant(self,n,**kwargs):
        s = "symbolicconst_%s_%d"%(n.symbol, len(self.dct))
        self.dct[n] = self.generate_neuron_variable_names(s)



class TerminalSymbolUnitDict(ASTActionerDefaultIgnoreMissing):
    def __init__(self, eqnset):
        ASTActionerDefault.__init__(self)
        self.dct = {}
        self.Visit(eqnset)

    def __getitem__(self,k):
        return self.dct[k]

    def ActionParameter(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionStateVariable(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionAssignedVariable(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionSuppliedValue(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionConstant(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionSymbolicConstant(self,n,**kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionFunctionDef(self, n, **kwargs):
        self.dct[n] = VariableInNeuronUnits(n)
    def ActionFunctionDefParameter(self, n, **kwargs):
        self.dct[n] = VariableInNeuronUnits(n)





class CString(ASTVisitorBase):
    
    def __init__(self):
        ASTVisitorBase.__init__(self,)
    
    @classmethod
    def Build (self, lhs, varnames, varunits, expand_assignments=False):
        c = CString()
        return c.Visit(lhs, varnames=varnames, varunits=varunits,expand_assignments=expand_assignments)

    def VisitIfThenElse(self, o,varnames, varunits, **kwargs):
        raise NotImplementedError()
    def VisitInEquality(self, o, varnames, varunits,**kwargs):
        raise NotImplementedError()
    def VisitBoolAnd(self, o,varnames, varunits, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o,varnames, varunits, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o,varnames, varunits, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def VisitFunctionDef(self, o,varnames, varunits, **kwargs):
        panic()
        
    def VisitBuiltInFunction(self, o,varnames, varunits, **kwargs):
        raise NotImplementedError()
    
    def VisitFunctionDefParameter(self, o,varnames, varunits, **kwargs):
        return varnames[o].raw_name


    # Terminals:
    def VisitStateVariable(self, o,varnames, varunits, **kwargs):
        return varnames[o].in_si_name    
    def VisitParameter(self, o,varnames, varunits, **kwargs):
        return varnames[o].in_si_name
    def VisitAssignedVariable(self, o,varnames, varunits,expand_assignments, **kwargs):
        if expand_assignments:
            return varnames[o].in_si_name
        else:
            return self.Visit( o.assignment_rhs, varnames=varnames, varunits=varunits, expand_assignments=expand_assignments )
    
    def VisitSuppliedValue(self, o,varnames, varunits, **kwargs):
        return varnames[o].in_si_name + "()"
    def VisitConstant(self, o,varnames, varunits, **kwargs):
        return varnames[o].in_si_name
    def VisitSymbolicConstant(self, o,varnames, varunits, **kwargs):
        return varnames[o].in_si_name



    # AST Objects:
    
    def VisitEqnTimeDerivative(self, o,varnames, varunits, **kwargs):
        panic()
    def VisitEqnAssignment(self, o,varnames, varunits, **kwargs):
        panic()


    def VisitAddOp(self, o, **kwargs):
        return "( %s + %s )"%( self.Visit(o.lhs,**kwargs), self.Visit(o.rhs, **kwargs) )

    def VisitSubOp(self, o,  **kwargs):
        return "( %s - %s )"%( self.Visit(o.lhs,**kwargs), self.Visit(o.rhs, **kwargs) )

    def VisitMulOp(self, o, **kwargs):
        return "( %s * %s )"%( self.Visit(o.lhs,**kwargs), self.Visit(o.rhs, **kwargs) )

    def VisitDivOp(self, o, **kwargs):
        return "( %s / %s )"%( self.Visit(o.lhs,**kwargs), self.Visit(o.rhs, **kwargs) )

    def VisitExpOp(self, o, **kwargs):
        return "((%s)^%s )"%( self.Visit(o.lhs,**kwargs), o.rhs )

    def VisitFunctionDefInstantiation(self, o, varnames, varunits, **kwargs):
        
        if type(o.function_def) == ast.BuiltInFunction:
            assert len(o.parameters) == 1        
            r = "%s(%s)"%( varnames[o.function_def].raw_name, self.Visit(o.parameters.values()[0].rhs_ast, varnames=varnames, varunits=varunits,**kwargs) )
            return r
        elif type(o.function_def) == ast.FunctionDef:
            params = ",".join( self.Visit(p.rhs_ast,varnames=varnames, varunits=varunits,**kwargs) for p in o.parameters.values()  )
            func_call = "%s(%s)"%( varnames[o.function_def].raw_name, params)
            return func_call
        else:
            panic()
        
    
    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        panic()
















