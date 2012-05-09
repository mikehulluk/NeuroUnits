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
#import string
#
#from neurounits.visitors import ASTVisitorBase
from neurounits.visitors import ASTActionerDefault
#from neurounits.visitors import SingleVisitPredicate 
#
#from neurounits.unit_errors import panic
#from neurounits import ast 
#from neurounits.neurounitparser import NeuroUnitParser
from neurounits.io_types import IOType


from section_writers import NeuronBlockWriter
from section_writers import NeuronInterfaceWriter


from section_writers import ParameterWriter
from section_writers import SuppliedValuesWriter
from section_writers import AssignmentWriter
from section_writers import StateWriter
from section_writers import FunctionWriter
from section_writers import ConstantWriter
from section_writers import OnEventWriter


from neuron_constants import NeuronSuppliedValues, NEURONMappings, MechanismType
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from neurounits.ast import EqnTimeDerivative, EqnAssignment, EqnSet,\
    ConstValue, InEquality



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
        self.section_BREAKPOINT_pre_solve = []
        self.section_BREAKPOINT_solve = []
        self.section_BREAKPOINT_post_solve = []
        self.section_DERIVATIVE = []
        self.section_FUNCTIONS = []
        self.section_NETRECEIVES = []
        


        ifthenelse = """FUNCTION ifthenelse (a,b,c,d) 
            {
                if(a < b ) { ifthenelse = c }
                else{ ifthenelse  =d } 
            }
            
            FUNCTION vtrap(VminV0, B) {
            if (fabs(VminV0/B) < 1e-6) {
            vtrap = (1 + VminV0/B/2)
            }else{
            vtrap = (VminV0 / B) /(1 - exp((-1 *VminV0)/B))
            }
            }
            
            
            """
        self.section_FUNCTIONS.append(ifthenelse)


    def to_text(self):
        
        
        
        
        std_sects = [
        ( self.section_NEURON,   'NEURON' ),
        ( self.section_UNITS_units + self.section_UNITS_convs+self.section_UNITS_constants,    'UNITS' ),
        ( self.section_PARAMETER,'PARAMETER' ),
        ( self.section_ASSIGNED, 'ASSIGNED' ),
        ( self.section_STATE_locals +[''] + self.section_STATE_init  +[''] + self.section_STATE ,    'STATE' ),
        
        ( self.section_INITIAL,  'INITIAL' ),
        ( self.section_BREAKPOINT_pre_solve + ["SOLVE states METHOD cnexp" if self.section_STATE != [] else ""]+ [""]+ self.section_BREAKPOINT_post_solve+[""],  'BREAKPOINT' ),
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
    
    
    
    
    
    
    
    
    
    





class NeuronMembraneCurrent(object):
    def __init__(self,  symbol,  obj):
        self.symbol = symbol
        self.obj = obj
    
    def get_neuron_name(self):
        return self.symbol + "_tonrn"
    
    def getCurrentType(self):

        if self.obj.get_dimension().is_compatible( NEURONMappings.current_units[MechanismType.Point] ):
            return MechanismType.Point
        elif self.obj.get_dimension().is_compatible( NEURONMappings.current_units[MechanismType.Distributed] ):
            return MechanismType.Distributed
        else:
            assert False, "Unknown type: %s"% self.obj.get_unit()
        






class MODLBuildParameters(object):
    def __init__(self,  mechanismtype, currents,   supplied_values,  suffix, symbol_units, event_function=None ):
        self.mechanismtype = mechanismtype
        self.currents = currents
        self.supplied_values = supplied_values
        self.suffix = suffix
        self.event_function = event_function
        self.symbol_units = symbol_units


    @classmethod
    def InferFromEqnset(cls, eqnset):
    
        currents = {}
        supplied_values = {}
        
        for io_info in [ io_info for io_info in eqnset.io_data if io_info.iotype in ( IOType.Output, IOType.Input)    ]:
            if not io_info.metadata or not 'mf' in io_info.metadata:
                continue
            role = io_info.metadata['mf'].get('role', None)
            
            if role:
                
                if not  eqnset.has_terminal_obj( io_info.symbol):
                    continue
                
                obj = eqnset.get_terminal_obj( io_info.symbol)
                
                # Outputs:
                if role == "TRANSMEMBRANECURRENT":
                    assert io_info.iotype== IOType.Output
                    
                    currents[obj] = NeuronMembraneCurrent( obj=obj,  symbol=obj.symbol)
                
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
        mech_type = currents.values()[0].getCurrentType()
        for c in currents.values():
            assert mech_type == c.getCurrentType(),  'Mixed Current types [Distributed/Point]'
        
        
        # Work out the units of all the terminal symbols:
        symbol_units = {}
        
        
        objs = eqnset.terminal_symbols
        n = EqnsetVisitorNodeCollector()
        n.Visit(eqnset)
        objs = n.all()
        for s in objs:
            
            if s in currents:
                symbol_units[s] = NEURONMappings.current_units[mech_type] 
            
            
            elif s in supplied_values:
                t = supplied_values[s]
                if t in NeuronSuppliedValues.All:
                    symbol_units[s] = NEURONMappings.supplied_value_units[ t ]  #NeuroUnitParser.Unit("mV")
                else:
                    print 'Unknown supplied value:', t
                    assert False
            else:
                if isinstance (s,( EqnTimeDerivative, EqnAssignment, EqnSet, ConstValue) ):
                    continue
                if isinstance (s,( InEquality) ):
                    continue
                
                symbol_units[s] = s.get_dimension()
                  
        
        
                  
        
        # Event Handling:
        zero_arg_events = [ ev for ev in eqnset.on_events if len(ev.parameters) == 0 ]
        if len(zero_arg_events) == 0:
            event_function= None
        elif len(zero_arg_events) == 1:
            event_function= zero_arg_events[0]
        else:
            raise ValueError("Multiple Zero-Param Events")
        
        return MODLBuildParameters(mechanismtype=mech_type, currents=currents, supplied_values=supplied_values, suffix="nmmodl"+eqnset.name, symbol_units=symbol_units, event_function=event_function  )
        





def WriteToNMODL(eqnset, buildparameters=None, initial_values=None ):
    
    if buildparameters is None:
        buildparameters = MODLBuildParameters.InferFromEqnset(eqnset)

         
    
    m = ModFileContents()
    
    # Write the header:
    NeuronBlockWriter(eqnset=eqnset,  build_parameters=buildparameters,  modfilecontents=m,   )
    NeuronInterfaceWriter().Visit(eqnset, build_parameters=buildparameters, modfilecontents=m)
    
    # Write the sections (order is important for Assignment Block):
    ParameterWriter().Visit(eqnset,modfilecontents=m,build_parameters=buildparameters, )
    SuppliedValuesWriter().Visit(eqnset,modfilecontents=m, build_parameters=buildparameters, buildparameters=buildparameters)
    AssignmentWriter().Visit(eqnset,modfilecontents=m, build_parameters=buildparameters)
    StateWriter().Visit(eqnset,modfilecontents=m,build_parameters=buildparameters, )
    FunctionWriter().Visit(eqnset,modfilecontents=m, build_parameters=buildparameters, )
    ConstantWriter().Visit(eqnset,modfilecontents=m, build_parameters=buildparameters, )
    OnEventWriter().Visit(eqnset,modfilecontents=m, buildparameters=buildparameters)
    
    txt = m.to_text()
    
    return txt, buildparameters

