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
from builder_visitor_propogate_dimensions import PropogateDimensions
from builder_visitor_remove_proxies import RemoveAllSymbolProxy
from eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.visitors.common.clone_from_eqnset import CloneObject
from neurounits.visitors.common.simplify_symbolic_constants import ReduceConstants
from neurounits.ast.astobjects import SymbolicConstant

class StdFuncs(object):

    @classmethod
    def get_sin(cls, backend):
        return ast.BuiltInFunction(funcname='sin',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_cos(cls, backend):
        return ast.BuiltInFunction(funcname='cos',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_tan(cls, backend):
        return ast.BuiltInFunction(funcname='tan',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_sinh(cls, backend):
        return ast.BuiltInFunction(funcname='sinh',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_cosh(cls, backend):
        return ast.BuiltInFunction(funcname='cosh',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_tanh(cls, backend):
        return ast.BuiltInFunction(funcname='tanh',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_asin(cls, backend):
        return ast.BuiltInFunction(funcname='asin',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_acos(cls, backend):
        return ast.BuiltInFunction(funcname='acos',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_atan(cls, backend):
        return ast.BuiltInFunction(funcname='atan',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_atan2(cls, backend):
        return ast.BuiltInFunction(funcname='atan2',
                                    parameters={
                                        'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ),
                                        'y':ast.FunctionDefParameter(symbol='y', dimension=backend.Unit() ),
                                        },
                                    dimension=backend.Unit() )

    @classmethod
    def get_exp(cls,backend):
        return ast.BuiltInFunction(funcname='exp',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )

    @classmethod
    def get_ln(cls,backend):
        return ast.BuiltInFunction(funcname='ln',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_log2(cls,backend):
        return ast.BuiltInFunction(funcname='log2',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )
    @classmethod
    def get_log10(cls,backend):
        return ast.BuiltInFunction(funcname='log10',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )



    @classmethod
    def get_pow(cls, backend):
        return ast.BuiltInFunction(funcname='pow',
                                    parameters={'base':ast.FunctionDefParameter(symbol='base', dimension=backend.Unit() ),
                                                'exp':ast.FunctionDefParameter(symbol='exp', dimension=backend.Unit() )  },
                                    dimension=backend.Unit() )
    @classmethod
    def get_sqrt(cls, backend):
        return ast.BuiltInFunction(funcname='sqrt',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=None ), },
                                    dimension=None )

    @classmethod
    def get_powint(cls, backend):
        return ast.BuiltInFunction(funcname='powint',
                                    parameters={
                                        'x':ast.FunctionDefParameter(symbol='x', dimension=None ),
                                        'n':ast.FunctionDefParameter(symbol='n', dimension=backend.Unit() ),
                                        'd':ast.FunctionDefParameter(symbol='d', dimension=backend.Unit() ),
                                        },
                                    dimension=None )


    @classmethod
    def get_fabs(cls,backend):
        return ast.BuiltInFunction(funcname='fabs',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )

    @classmethod
    def get_ceil(cls,backend):
        return ast.BuiltInFunction(funcname='ceil',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )

    @classmethod
    def get_floor(cls,backend):
        return ast.BuiltInFunction(funcname='floor',
                                    parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
                                    dimension=backend.Unit() )


    @classmethod
    def get_builtin_function(cls, name, backend):
        lut = {
                "__sin__":cls.get_sin,
                "__cos__":cls.get_cos,
                "__tan__":cls.get_tan,
                "__sinh__":cls.get_sinh,
                "__cosh__":cls.get_cosh,
                "__tanh__":cls.get_tanh,
                "__asin__":cls.get_asin,
                "__acos__":cls.get_acos,
                "__atan__":cls.get_atan,
                "__atan2__":cls.get_atan2,

                "__exp__":cls.get_exp,
                "__ln__":cls.get_ln,
                "__log2__":cls.get_log2,
                "__log10__":cls.get_log10,

                "__pow__":cls.get_pow,
                "__sqrt__":cls.get_sqrt,
                "__powint__":cls.get_powint,

                "__ceil__":cls.get_ceil,
                "__fabs__":cls.get_fabs,
                "__floor__":cls.get_floor,
                }
        return lut[name](backend=backend)



#    @classmethod
#    def getMath(cls, backend):
#
#        consts = {
#          'pi':           backend.Quantity(3.141592653,   backend.Unit() ),
#          'e_euler':      backend.Quantity(2.718281828,   backend.Unit() ),
#        }
#        constants = dict( [ (sym, ast.SymbolicConstant(symbol=sym, value=val) ) for (sym,val) in consts.iteritems()] )
#
#        functiondefs ={
#            'exp' : ast.BuiltInFunction(funcname='exp',
#                                        parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
#                                        dimension=backend.Unit() ),
#
#            'fabs' : ast.BuiltInFunction(funcname='fabs',
#                                        parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
#                                        dimension=backend.Unit() ),
#
#            'pow' : ast.BuiltInFunction(funcname='pow',
#                                        parameters={'base':ast.FunctionDefParameter(symbol='base', dimension=backend.Unit() ),
#                                                    'exp':ast.FunctionDefParameter(symbol='exp', dimension=backend.Unit() )  },
#                                        dimension=backend.Unit() ),
#        }
#
#        return ast.Library('std.math', constants = constants, functiondefs = functiondefs, )
#
#
#    @classmethod
#    def getPhysics(cls, backend):
#
#        uL = UnitTermData.getUnitLUT(backend)
#        consts = {
#                   'F':         backend.Quantity(96485.3365,    uL['coulomb']/uL["mole"] ),
#                   'R':         backend.Quantity(8.3144621,     uL['joule']/(uL["mole"]*uL['kelvin'] ) ),
#                   'Na':        backend.Quantity(6.02214129e23, backend.Unit(mole=-1) ),
#                   'k':         backend.Quantity(1.380648e-23,  uL['joule']/uL["kelvin"] ),
#                   'e_charge':  backend.Quantity(1.602176565,   uL['coulomb']   ),
#                   }
#        constants = dict( [ (sym, ast.SymbolicConstant(symbol=sym, value=val) ) for (sym,val) in consts.iteritems()] )
#
#        return ast.Library('std.physics', constants = constants, functiondefs={} )
#
#
#
#    @classmethod
#    def get_default(cls, backend):
#        return []
#        return [cls.getMath(backend=backend), cls.getPhysics(backend=backend) ]




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
        self.eqnset_name = None
        self.assignments = SingleSetDict()
        self.onevents = SingleSetDict()
        self.timederivatives = SingleSetDict()
        self.funcdefs = SingleSetDict()
        self.symbolicconstants = SingleSetDict()

        self.io_data_lines = []





class AbstractBlockBuilder(object):
    def __init__(self,library_manager,block_type):
        self.library_manager = library_manager
        self.builddata = BuildData()
        self.block_type = block_type

        # Scoping:
        self.global_scope = Scope(proxy_if_absent=True)
        self.active_scope = None


    def set_name(self, name):
        self.builddata.eqnset_name = name.strip()


    # Internal symbol handling:
    def get_symbol_or_proxy(self, s):
        # Are we in a function definition?
        if self.active_scope is not None:
            return self.active_scope.getSymbolOrProxy(s)
        else:
            return self.global_scope.getSymbolOrProxy(s)

    def _resolve_global_symbol(self,symbol,target, expect_is_unresolved=False):
        if expect_is_unresolved and not self.global_scope.hasSymbol(symbol):
                raise ValueError("I was expecting to resolve a symbol in globalnamespace that is not there %s"%symbol)

        if not self.global_scope.hasSymbol(symbol):
            self.global_scope[symbol] = target
        else:
            symProxy = self.global_scope[symbol]
            symProxy.set_target(target)


    # Handle the importing of other symbols into this namespace:
    # ###########################################################
    def do_import(self, srclibrary, tokens):
        lib = self.library_manager.get(srclibrary)

        for (token, alias) in tokens:

            sym = lib.get_terminal_obj(token)
            exc = { ast.FunctionDef:     self.do_import_function_def,
                    ast.BuiltInFunction: self.do_import_function_builtin,
                    ast.SymbolicConstant: self.do_import_constant }
            exc[type(sym)](sym, alias=alias)


    def do_import_constant(self,srcObjConstant, alias=None):
        new_obj = CloneObject.SymbolicConstant(srcObj=srcObjConstant, dst_symbol=alias )
        self._resolve_global_symbol(new_obj.symbol, new_obj)
        self.builddata.symbolicconstants[new_obj.symbol] = new_obj

        assert isinstance(new_obj, SymbolicConstant)

    def do_import_function_builtin(self,srcObjFuncDef, alias=None):
        new_obj = CloneObject.BuiltinFunction(srcObj=srcObjFuncDef, dst_symbol=alias )
        self.builddata.funcdefs[new_obj.funcname] = new_obj

    def do_import_function_def(self,srcObjFuncDef, alias=None):
        new_obj = CloneObject.FunctionDef(srcObj=srcObjFuncDef, dst_symbol=alias )
        self.builddata.funcdefs[new_obj.funcname] = new_obj


    # Function Definitions:
    # #########################
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
        # In the case of a library, we can also access global constants:

        for symbol, proxy in self.active_scope.iteritems():

            # If we are in a library, then it is OK to lookup symbols
            # in the global namespace, since they will be constants.
            # (Just make sure its not defined in both places)
            if self.block_type==ast.Library:
                if self.global_scope.hasSymbol(symbol):
                    assert not symbol in f.parameters
                    proxy.set_target( self.global_scope.getSymbol(symbol) )
                    continue



            if symbol in f.parameters:
                proxy.set_target( f.parameters[symbol] )
                continue
            assert False, 'Unable to find symbol: %s in function definition: %s'%(symbol, f)

        # Close the scope
        self.active_scope = None



    def create_function_call(self, funcname, parameters):

        # BuiltInFunctions have __XX__
        # Load it if not already exisitng:
        if funcname[0:2] == "__" and not funcname in self.builddata.funcdefs:
            self.builddata.funcdefs[funcname] = StdFuncs.get_builtin_function(funcname, backend=self.library_manager.backend)

        # Allow fully qulaified names that are not explicity imported
        if '.' in funcname and not funcname in self.builddata.funcdefs:
            mod = ".".join( funcname.split(".")[:-1] )
            self.do_import( mod, tokens= [(funcname.split(".")[-1], funcname), ])


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
            assert p in func_def.parameters, "Can't find %s in %s"%(p, func_def.parameters)
            # Connect the call parameter to the definition:
            parameters[p].symbol=p
            parameters[p].set_function_def_parameter( func_def.parameters[p] )


        # Create the functions
        return ast.FunctionDefInstantiation( parameters=parameters, function_def=func_def)



    # Although Library don't allow assignments, we turn assignments of contants
    # into symbolic constants later, so we allow for them both.
    def add_assignment(self, lhs_name, rhs_ast):

        # Create the lhs object:
        assigned_obj = ast.AssignedVariable( lhs_name )
        self._resolve_global_symbol( lhs_name, assigned_obj)

        # Create the assignment object:
        a = ast.EqnAssignment( lhs=assigned_obj, rhs=rhs_ast )

        assert not assigned_obj in self.builddata.assignments
        self.builddata.assignments[assigned_obj] = a
        # Connect the assignment values to its rhs:
        assigned_obj.assignment_rhs = a.rhs


    def finalise(self):

        # A few sanity checks....
        # ########################
        assert self.active_scope is None

        from neurounits.librarymanager import LibraryManager
        assert isinstance( self.library_manager, LibraryManager)



        # We inspect the io_data ( '<=>' lines), and use it to:
        #  - resolve the types of unresolved symbols
        #  - set the dimensionality
        # ###################################################

        # Parse the IO data lines:
        io_data = list( itertools.chain( *[ parse_io_line(l) for l in self.builddata.io_data_lines] ) )

        # Update 'Parameter' and 'SuppliedValue' symbols from IO Data:
        param_symbols = [ ast.Parameter(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype==IOType.Parameter ]
        for p in param_symbols:
            if self.library_manager.options.allow_unused_parameter_declarations:
                self._resolve_global_symbol(p.symbol, p, expect_is_unresolved = False)
            else:
                self._resolve_global_symbol(p.symbol, p, expect_is_unresolved = True)

        supplied_symbols = [ ast.SuppliedValue(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype==IOType.Input ]
        for s in supplied_symbols:
            if self.library_manager.options.allow_unused_suppliedvalue_declarations:
                self._resolve_global_symbol(s.symbol, s, expect_is_unresolved = False)
            else:
                self._resolve_global_symbol(s.symbol, s, expect_is_unresolved = True)

        # We don't need to 'do' anything for 'output' information, since they
        # are 'AssignedValues' so will be resolved already. However, it might
        # contain dimensionality information.
        output_symbols = [ p for p in io_data if p.iotype==IOType.Output ]
        for o in output_symbols:
            os_obj = RemoveAllSymbolProxy().followSymbolProxy( self.global_scope.getSymbol(o.symbol) )
            assert not os_obj.is_dimensionality_known()
            if o.dimension:
                os_obj.set_dimensionality( o.dimension )


        # OK, everything in our namespace should be resoved.  If not, then
        # something has gone wrong.  Look for remaining unresolved symbols:
        # ########################################
        unresolved_symbols = [ (k,v) for (k,v) in self.global_scope.iteritems() if not v.is_resolved() ]
        # We shouldn't get here!
        if len(unresolved_symbols) != 0:
            raise ValueError("Unresolved Symbols:%s"%([s[0] for s in unresolved_symbols]))




        # Lets build the Block Object!
        # ################################
        #self._astobject = ast.EqnSet(
        self._astobject = self.block_type(
                    library_manager = self.library_manager,
                    builder = self,
                    builddata = self.builddata,
                    io_data = io_data,
                )


        # The object exists, but is not complete and needs some polishing:
        # #################################################################

        # 1. Resolve the SymbolProxies:
        RemoveAllSymbolProxy().visit(self._astobject)

        # 2. Propagate the dimensionalities accross the system:
        PropogateDimensions.propogate_dimensions(self._astobject)

        # 3. Reduce simple assignments to symbolic constants:
        ReduceConstants().visit(self._astobject)






class EqnSetBuilder(AbstractBlockBuilder):

    def __init__(self, library_manager):
        AbstractBlockBuilder.__init__(self,block_type=ast.EqnSet, library_manager=library_manager)

    def add_io_data(self,l):
        self.builddata.io_data_lines.append(l)

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
        self.builddata.onevents[ev.name] = ev


    def add_timederivative(self, lhs_state_name, rhs_ast):
        statevar_obj = ast.StateVariable( lhs_state_name )
        self._resolve_global_symbol( lhs_state_name, statevar_obj)

        # Create the assignment object:
        a = ast.EqnTimeDerivative( lhs=statevar_obj, rhs=rhs_ast )

        assert not statevar_obj in self.builddata.timederivatives
        self.builddata.timederivatives[statevar_obj] = a




class LibraryBuilder(AbstractBlockBuilder):

    def __init__(self, library_manager):
        AbstractBlockBuilder.__init__(self,block_type=ast.Library, library_manager=library_manager)






