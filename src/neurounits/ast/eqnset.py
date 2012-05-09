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
from neurounits.ast.astobjects import Parameter, SuppliedValue, ConstValue,\
    AssignedVariable
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
    




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
        self.io_data = None
        
        


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
        return sorted( self._eqn_assignment.keys(), key=lambda a:a.symbol )

    @property
    def states(self):
        return sorted( self._eqn_time_derivatives.keys(), key=lambda a:a.symbol )

    @property
    def functiondefs(self):
        return self._function_defs.values()

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants.values(), key=lambda a:a.symbol )




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
    def _getAssignedVariablesDict(self):
        return  dict( [(ass.lhs.symbol, ass.lhs)  for ass in self._eqn_assignment.values() ])
    def _getStateVariablesDict(self):
        return dict([(td.lhs.symbol, td.lhs)  for td in self._eqn_time_derivatives.values() ])





    def getSymbolDependancicesDirect(self, sym, include_constants=False):
        
        assert sym in self.terminal_symbols
        
        if isinstance(sym, AssignedVariable):
            sym = sym.assignment_rhs
        
        d = VisitorFindDirectSymbolDependance()
        
        return list( set( d.Visit(sym) ) ) 
    
    def getSymbolDependancicesIndirect(self, sym,include_constants=False, include_ass_in_output=False):
        res_deps = []
        un_res_deps =  self.getSymbolDependancicesDirect(sym, include_constants=include_constants) 
        
        while un_res_deps:
            p = un_res_deps.pop()
            
            if p is sym:
                continue
            if p in res_deps:
                continue
            
            p_deps = self.getSymbolDependancicesIndirect(p, include_constants=include_constants) 
            un_res_deps.extend(p_deps)
            res_deps.append(p)
            
        if not include_ass_in_output:
            res_deps = [d for d in res_deps if not isinstance(d,AssignedVariable) ]
        return res_deps
            


    def getSymbolMetadata(self, sym):
        assert sym in self.terminal_symbols
        for io in self.io_data:
            if io.symbol == sym.symbol:
                return io.metadata
        return None

            


    def AcceptVisitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)



