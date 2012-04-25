#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
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
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY
# WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#-------------------------------------------------------------------------------


from neurounits.units_misc import Chainmap
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from base import ASTObject
from neurounits.ast.astobjects import Parameter, SuppliedValue, ConstValue
    




# TODO: Why does it derived from ASTObject??
class EqnSet(ASTObject):
    """A class that represents a system of dynamic equations with dimensions attached"""




    def __init__(self,):
        self._eqn_time_derivatives = {}
        self._eqn_assignment  = {}
        self._function_defs = {}
        self._symbolicconstants = {}



        self._parameters =  None
        self._supplied_values =  None
        self._constants = None


        self.name = None

        self.summary_data = []

        self.on_events = []

        self._builder = None


        # In Use!
        self.library_manager = None


    @property
    def src_text(self):
        return self.library_manager.src_text


    def _cache_nodes(self):
        t = EqnsetVisitorNodeCollector()
        t.Visit(self)

        self._parameters =  t.nodes[Parameter]
        self._supplied_values =  t.nodes[SuppliedValue]
        self._constants = t.nodes[ConstValue]




    def get_working_dir(self):
        return self._builder.library_manager.working_dir + "/" + self.name + "/"




    @property
    def assignments(self):
        return self._eqn_assignment.values()

    @property
    def timederivatives(self):
        return self._eqn_time_derivatives.values()

    @property
    def assignedvalues(self):
        return self._eqn_assignment.keys()

    @property
    def states(self):
        return self._eqn_time_derivatives.keys()

    @property
    def functiondefs(self):
        return self._function_defs.values()

    @property
    def symbolicconstants(self):
        return self._symbolicconstants.values()




    @property
    def parameters(self):
        return self._parameters
    @property
    def constants(self):
        return self._constants
    @property
    def suppliedvalues(self,):
        return self._supplied_values



    @property
    def terminal_symbols(self):
        ts =  list(self.states) + \
                list(self.assignedvalues) + \
                list(self.parameters) + \
                list(self.suppliedvalues) + \
                list(self.symbolicconstants)
        for t in ts:
            assert isinstance(t, ASTObject)
        return ts


    def get_terminal_obj(self, symbol):
#        m1 =  self._getParametersDict()
#        m2 = self._getSuppliedValuesDict()
#        m3 = self._getAssignedVariablesDict()
#        m4 = self._getStateVariablesDict()
#        m5 = self._symbolicconstants
#        print "M1", m1, type(m1)
#        print "M2", m2, type(m2)
#        print "M3", m3, type(m3)
#        print "M4", m4, type(m4)
#        print "M5", m5, type(m5)

        m = Chainmap( self._getParametersDict(),
                      self._getSuppliedValuesDict(),
                      self._getAssignedVariablesDict(),
                      self._getStateVariablesDict(),
                      self._symbolicconstants  )
        return m[symbol]

    def has_terminal_obj(self, symbol):
        try:
            self.get_terminal_obj(symbol=symbol)
            return True
        except KeyError:
            return False
        except:
            raise



    def getSymbol(self, sym):
        assert False
        try:
            return Chainmap(self._function_defs,self._constants)[sym]
        except KeyError:
            raise ValueError("Library: %s does not contain symbol: %s"%(self.name, sym) )



    def _getSuppliedValuesDict(self):
        return dict( [(s.symbol, s)  for s in self._supplied_values ])
    def _getParametersDict(self):
        return dict( [(s.symbol, s)  for s in self._parameters ])
    #def _getSymbolicConstantsDict(self):
        #return dict( [(s.symbol, s)  for s in self._symbolicconstants ])
    def _getAssignedVariablesDict(self):
        return  dict( [(ass.lhs.symbol, ass.lhs)  for ass in self._eqn_assignment.values() ])
    def _getStateVariablesDict(self):
        return dict([(td.lhs.symbol, td.lhs)  for td in self._eqn_time_derivatives.values() ])





    def AcceptVisitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)



