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
import itertools
from neurounits import ast
from neurounits.io_types import IOType
from neurounits.units_misc import SingleSetDict
from eqnsetbuilder_io import parse_io_line
from builder_visitor_propogate_units import PropogateUnits
from builder_visitor_remove_proxies import RemoveAllSymbolProxy
from eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.visitors.common.clone_from_eqnset import CloneObject
from neurounits.visitors.common.simplify_symbolic_constants import ReduceConstants






class Scope(object):
    def __init__(self,proxy_if_absent=False):
        self.symbol_dict = {}
        self.proxy_if_absent = proxy_if_absent

    def getSymbolOrProxy(self, symbol):
        assert isinstance(symbol, basestring)
        if not symbol in self.symbol_dict:
            self.symbol_dict[symbol] = SymbolProxy()
        return self.symbol_dict[symbol]

    def getSymbol(self, symbol):
        assert isinstance(symbol, basestring)
        if not symbol in self.symbol_dict:
            raise ValueError("Symbol not in scope: %s"%symbol)
        return self.symbol_dict[symbol]


    def hasSymbol(self,symbol):
        return symbol in self.symbol_dict

    def iteritems(self,):
        return self.symbol_dict.iteritems()

    def __getitem__(self,symbol):
        assert isinstance(symbol, basestring)
        return self.symbol_dict[symbol]
    def __setitem__(self,symbol,value):
        assert isinstance(symbol, basestring)
        self.symbol_dict[symbol] = value

    


class BuildData(object):
    
    def __init__(self,):
        self.assignments = SingleSetDict() 
        self.onevents = SingleSetDict()
        self.timederivatives = SingleSetDict() 
        self.funcdefs = SingleSetDict()
        self.constants = SingleSetDict() 
        self.summary_data = []
        self.eqnset_name = None


        self.io_data_lines = []
            


class EqnSetBuilder(object):

    def AcceptVisitor(self, v, **kwargs):
        assert False
        return v.VisitAST(self, **kwargs)
    

    def __init__(self, library_manager): 
        self.library_manager = library_manager
        self.builddata = BuildData()        

        # Scoping:
        self.global_scope = Scope(proxy_if_absent=True) 
        self.active_scope = None


        
        

    def add_io_data(self,l):
        self.builddata.io_data_lines.append(l)
        
    def add_summary_info(self,l):
        from eqnsetbuilder_summary.summary_string_parser import parse_string
        p = parse_string(l)
        self.summary_data.append(p)
    
    def get_symbol_or_proxy(self, s):
        # Are we in a function definition?
        if self.active_scope is not None:
            return self.active_scope.getSymbolOrProxy(s)
        else:
            return self.global_scope.getSymbolOrProxy(s)



    def resolve_global_symbol(self,symbol,target, expect_is_unresolved=False):
        print 'Symbol', symbol
        print 
        if expect_is_unresolved and not self.global_scope.hasSymbol(symbol):
                raise ValueError("I was expecting to resolve a symbol in globalnamespace that is not there %s"%symbol)

        if not self.global_scope.hasSymbol(symbol):
            self.global_scope[symbol] = target
        else:
            symProxy = self.global_scope[symbol]
            symProxy.set_target(target)

    



    def set_name(self, name):
        self.builddata.eqnset_name = name.strip()




    # Handle Imports from other libraries:
    def do_import(self, srclibrary, tokens):        
        print 'Importing from : ', srclibrary
        lib = self.library_manager.get(srclibrary)
        
        for (token, alias) in tokens:
            
            sym = lib.getSymbol(token)
            exc = { ast.FunctionDef:     self.do_import_function_def,
                    ast.BuiltInFunction: self.do_import_function_builtin,
                    ast.SymbolicConstant: self.do_import_constant }
            exc[type(sym)](sym, alias=alias)
        
    def do_import_constant(self,srcObjConstant, alias=None):        
        new_obj = CloneObject.SymbolicConstant(srcObj=srcObjConstant, dst_symbol=alias )
        self.resolve_global_symbol(new_obj.symbol, new_obj)
        self.builddata.constants[new_obj.symbol] = new_obj
    
        
        
    def do_import_function_builtin(self,srcObjFuncDef, alias=None):
        print 'Importing Function'
        new_obj = CloneObject.BuiltinFunction(srcObj=srcObjFuncDef, dst_symbol=alias )
        self.builddata.funcdefs[new_obj.funcname] = new_obj

    def do_import_function_def(self,srcObjFuncDef, alias=None):
        print 'Importing Function'
        #return srcObjFuncDef
        new_obj = CloneObject.FunctionDef(srcObj=srcObjFuncDef, dst_symbol=alias )
        self.builddata.funcdefs[new_obj.funcname] = new_obj
        
        
        
        

            
        




    # Function Definitions:
    def open_function_def_scope(self):
        assert self.active_scope is None
        self.active_scope = Scope() 

    def close_scope_and_create_function_def(self, f):
        assert self.active_scope is not None
        self.builddata.funcdefs[f.funcname] = f


        # At this stage, there may be unresolved symbols in the 
        # AST of the function call. We need to map
        # these accross to the function call parameters:
        # These symbols will be available in the active_scope:
        # Hook up the parameters to what will currently 
        # be proxy-objects.
        for symbol, proxy in self.active_scope.iteritems():
            if not symbol in f.parameters:
                assert False, 'Unable to find symbol: %s in function definition: %s'%(symbol, f)
            proxy.set_target( f.parameters[symbol] )

        # Close the scope
        self.active_scope = None


    # Event Definitions:
    def open_event_def_scope(self):
        assert self.active_scope is None
        self.active_scope = Scope() 
       
    def close_scope_and_create_onevent(self, ev ):
        assert self.active_scope is not None
        scope = self.active_scope
        self.active_scope = None

        # Resolve the symbols in the namespace
        for sym,obj in scope.iteritems():
            # Resolve Symbol from the Event Parameters:
            if sym in ev.parameters:
                obj.set_target( ev.parameters[sym] )

            # Resolve at global scope:
            else:
                obj.set_target( self.global_scope.getSymbolOrProxy(sym) )

        # Save this event
        self.onevents.append(ev)  




    def create_function_call(self, funcname, parameters):

        assert funcname in self.builddata.funcdefs, ('Function not defined:'+ funcname)
        func_def = self.builddata.funcdefs[funcname]

            
        # Single Parameter functions do not need to be
        # identified by name: 
        if len(parameters) == 1:
            kFuncDef = list(func_def.parameters.keys())[0]
            kFuncCall = list(parameters.keys())[0]
            
            # Not called by name, remap to name:
            assert kFuncDef is not None
            if kFuncCall is None:
                parameters[kFuncDef] = parameters[kFuncCall]
                parameters[kFuncDef].symbol = parameters[kFuncDef].symbol
                del parameters[None]
            else:
                assert kFuncDef == kFuncCall
                 

        # Check the parameters tally: 
        assert len(parameters) == len(func_def.parameters)
        for p in parameters:
            assert p in func_def.parameters
            # Connect the call parameter to the definition:
            parameters[p].symbol=p 
            parameters[p].set_function_def_parameter( func_def.parameters[p] )
        
        
        # Create the functions
        return ast.FunctionDefInstantiation( parameters=parameters, function_def=func_def)
    
        


    def add_assignment(self, lhs_name, rhs_ast):
        
        # Create the lhs object:
        assigned_obj = ast.AssignedVariable( lhs_name )
        self.resolve_global_symbol( lhs_name, assigned_obj)
        
        # Create the assignment object:
        a = ast.EqnAssignment( lhs=assigned_obj, rhs=rhs_ast )
        
        assert not assigned_obj in self.builddata.assignments
        self.builddata.assignments[assigned_obj] = a
        # Connect the assignment values to its rhs:
        assigned_obj.assignment_rhs = a.rhs

    def add_timederivative(self, lhs_state_name, rhs_ast):
        statevar_obj = ast.StateVariable( lhs_state_name )
        self.resolve_global_symbol( lhs_state_name, statevar_obj)
        
        # Create the assignment object:
        a = ast.EqnTimeDerivative( lhs=statevar_obj, rhs=rhs_ast )

        assert not statevar_obj in self.builddata.timederivatives
        self.builddata.timederivatives[statevar_obj] = a

        #assert not statevar_obj in self._astobject._eqn_time_derivatives
        #self._astobject._eqn_time_derivatives[statevar_obj] = a









    def finalise(self, unresolved_to_params=False):
    
        
        
        self._astobject = ast.EqnSet()
        self._astobject.backend = self.library_manager.backend
        self._astobject._builder = self
        
        self._astobject.name = self.builddata.eqnset_name
        self._astobject._eqn_assignment = self.builddata.assignments        
        self._astobject._function_defs = self.builddata.funcdefs
        self._astobject._eqn_time_derivatives = self.builddata.timederivatives
        self._astobject._constants = self.builddata.constants
        self._astobject.on_events = self.builddata.onevents
        
        
        # Sanity Check:
        assert self.active_scope is None



        # Parse the IO data lines:
        io_data = list( itertools.chain( *[ parse_io_line(l) for l in self.builddata.io_data_lines] ) )
        self._astobject.io_data = io_data

        #print io_data[0]
        #assert False
        
        # Update Symbols from IO Data:
        # ############################
        # Look through the io_data, and look for parameter definitions, and supplied values:
        param_symbols = [ ast.Parameter(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype==IOType.Parameter ]
        for p in param_symbols:
            print 'Setting Parameter:', p.symbol
            self.resolve_global_symbol(p.symbol, p, expect_is_unresolved = True)
            self._astobject._parameters[p.symbol] = p

        supplied_symbols = [ ast.SuppliedValue(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype==IOType.Input ]
        for s in supplied_symbols:
            self.resolve_global_symbol(s.symbol, s, expect_is_unresolved = True)
            self._astobject._supplied_values[s.symbol] = s







        # We don't need to 'do' anything for OUTPUT information,
        # but it might contain unit information:
        output_symbols = [ p for p in io_data if p.iotype==IOType.Output ]
        for o in output_symbols:
#            from builder_visitor_remove_proxies import RemoveAllSymbolProxy
            os_obj = RemoveAllSymbolProxy().followSymbolProxy( self.global_scope.getSymbol(o.symbol) )
            assert not os_obj.is_dimensionality_known()
            if o.dimension:
                os_obj.set_dimensionality( o.dimension )


        



        # Look for remaining unresolved symbols:
        unresolved_symbols = [ (k,v) for (k,v) in self.global_scope.iteritems() if not v.is_resolved() ]


        
        if unresolved_to_params == True:
            raise NotImplementedError()
        else:
            if len(unresolved_symbols) != 0:
                raise ValueError("Unresolved Symbols:%s"%([s[0] for s in unresolved_symbols]))








        # Resolve the SymbolProxies:
        #from builder_visitor_remove_proxies import RemoveAllSymbolProxy
        print type(RemoveAllSymbolProxy)
        a = RemoveAllSymbolProxy()
        a.Visit( self._astobject)
        #RemoveAllSymbolProxy().Visit(self._astobject)
        
        # Ensure we have units for all the terms:
        PropogateUnits.propogate_units(self._astobject)


        ReduceConstants().Visit(self._astobject)
