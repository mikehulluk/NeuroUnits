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

import itertools
from neurounits import ast
from neurounits.io_types import IOType
from neurounits.units_misc import SingleSetDict
from .eqnsetbuilder_io import parse_io_line
from .builder_visitor_propogate_dimensions import PropogateDimensions
from .builder_visitor_remove_proxies import RemoveAllSymbolProxy
from .eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.visitors.common.clone_from_eqnset import CloneObject
from neurounits.visitors.common.simplify_symbolic_constants import ReduceConstants
from neurounits.ast.astobjects import SymbolicConstant
from neurounits.ast.astobjects_nineml import RTBlock

from collections import defaultdict


class StdFuncs(object):

    @classmethod
    def get_sin(cls, backend):
        return ast.BuiltInFunction(funcname='sin',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_cos(cls, backend):
        return ast.BuiltInFunction(funcname='cos',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_tan(cls, backend):
        return ast.BuiltInFunction(funcname='tan',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_sinh(cls, backend):
        return ast.BuiltInFunction(funcname='sinh',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_cosh(cls, backend):
        return ast.BuiltInFunction(funcname='cosh',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_tanh(cls, backend):
        return ast.BuiltInFunction(funcname='tanh',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_asin(cls, backend):
        return ast.BuiltInFunction(funcname='asin',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_acos(cls, backend):
        return ast.BuiltInFunction(funcname='acos',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_atan(cls, backend):
        return ast.BuiltInFunction(funcname='atan',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_atan2(cls, backend):
        return ast.BuiltInFunction(funcname='atan2',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit()),
                                   'y': ast.FunctionDefParameter(symbol='y'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_exp(cls, backend):
        return ast.BuiltInFunction(funcname='exp',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_ln(cls, backend):
        return ast.BuiltInFunction(funcname='ln',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_log2(cls, backend):
        return ast.BuiltInFunction(funcname='log2',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_log10(cls, backend):
        return ast.BuiltInFunction(funcname='log10',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_pow(cls, backend):
        return ast.BuiltInFunction(funcname='pow',
                                   parameters={'base': ast.FunctionDefParameter(symbol='base'
                                   , dimension=backend.Unit()),
                                   'exp': ast.FunctionDefParameter(symbol='exp'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_sqrt(cls, backend):
        return ast.BuiltInFunction(funcname='sqrt',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=None)}, dimension=None)

    @classmethod
    def get_powint(cls, backend):
        return ast.BuiltInFunction(funcname='powint',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=None),
                                   'n': ast.FunctionDefParameter(symbol='n'
                                   , dimension=backend.Unit()),
                                   'd': ast.FunctionDefParameter(symbol='d'
                                   , dimension=backend.Unit())},
                                   dimension=None)

    @classmethod
    def get_fabs(cls, backend):
        return ast.BuiltInFunction(funcname='fabs',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_ceil(cls, backend):
        return ast.BuiltInFunction(funcname='ceil',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

    @classmethod
    def get_floor(cls, backend):
        return ast.BuiltInFunction(funcname='floor',
                                   parameters={'x': ast.FunctionDefParameter(symbol='x'
                                   , dimension=backend.Unit())},
                                   dimension=backend.Unit())

   # @classmethod
   # def get_max(cls, backend):
   #     return ast.BuiltInFunction(funcname='min',
   #                                parameters={
   #                                    'x': ast.FunctionDefParameter(symbol='x', dimension=None),
   #                                    'y': ast.FunctionDefParameter(symbol='y', dimension=None)
   #                                    },
   #                                dimension=backend.Unit())

    @classmethod
    def get_builtin_function(cls, name, backend):
        lut = {
            '__sin__': cls.get_sin,
            '__cos__': cls.get_cos,
            '__tan__': cls.get_tan,
            '__sinh__': cls.get_sinh,
            '__cosh__': cls.get_cosh,
            '__tanh__': cls.get_tanh,
            '__asin__': cls.get_asin,
            '__acos__': cls.get_acos,
            '__atan__': cls.get_atan,
            '__atan2__': cls.get_atan2,
            '__exp__': cls.get_exp,
            '__ln__': cls.get_ln,
            '__log2__': cls.get_log2,
            '__log10__': cls.get_log10,
            '__pow__': cls.get_pow,
            '__sqrt__': cls.get_sqrt,
            '__powint__': cls.get_powint,
            '__ceil__': cls.get_ceil,
            '__fabs__': cls.get_fabs,
            '__floor__': cls.get_floor,
            }
        return lut[name](backend=backend)


class Scope(object):

    def __init__(self, proxy_if_absent=False):
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
            raise ValueError('Symbol not in scope: %s' % symbol)
        return self.symbol_dict[symbol]

    def hasSymbol(self, symbol):
        return symbol in self.symbol_dict

    def iteritems(self):
        return self.symbol_dict.iteritems()

    def __getitem__(self, symbol):
        assert isinstance(symbol, basestring)
        return self.symbol_dict[symbol]

    def __setitem__(self, symbol, value):
        assert isinstance(symbol, basestring)
        self.symbol_dict[symbol] = value


class BuildData(object):

    def __init__(self):
        self.eqnset_name = None

        self.onevents = SingleSetDict()
        self.timederivatives = SingleSetDict()
        self.funcdefs = SingleSetDict()
        self.symbolicconstants = SingleSetDict()

        self.io_data_lines = []

        self.transitions_triggers = []
        self.transitions_events = []

        self.timederivatives = None
        self.assignments = None

        # Temporary lists, that will be resolved later:
        self._time_derivatives_per_regime = []
        self._assigments_per_regime = []


class AbstractBlockBuilder(object):

    def __init__(self, library_manager, block_type, name):
        self.library_manager = library_manager
        self.builddata = BuildData()
        self.builddata.eqnset_name = name
        self.block_type = block_type

        # Scoping:
        self.global_scope = Scope(proxy_if_absent=True)
        self.active_scope = None

        # RT-Graph & Regime:
        self._all_rt_graphs = dict([(None, RTBlock())])
        self._current_rt_graph = self._all_rt_graphs[None]
        self._current_regime = self._current_rt_graph.get_or_create_regime(None)
        
        self.builddata.eqnset_name = name.strip()

    def open_regime(self, regime_name):
        self._current_regime = self._current_rt_graph.get_or_create_regime(regime_name)

    def close_regime(self):
        self._current_regime = self._current_rt_graph.get_or_create_regime(None)

    def get_current_regime(self):
        return self._current_regime

    def open_rt_graph(self, name):
        assert self._current_rt_graph == self._all_rt_graphs[None]

        if not name in self._all_rt_graphs:
            self._all_rt_graphs[name] = RTBlock(name)

        self._current_rt_graph = self._all_rt_graphs[name]

    def close_rt_graph(self):
        self._current_rt_graph = self._all_rt_graphs[None]

    # Internal symbol handling:
    def get_symbol_or_proxy(self, s):
        #print 'get_symbol_or_proxy:', s
        # Are we in a function definition?
        if self.active_scope is not None:
            return self.active_scope.getSymbolOrProxy(s)
        else:
            return self.global_scope.getSymbolOrProxy(s)

    def _resolve_global_symbol(self,symbol,target, expect_is_unresolved=False):
        if expect_is_unresolved and not self.global_scope.hasSymbol(symbol):
                raise ValueError("I was expecting to resolve a symbol in globalnamespace that is not there %s" % symbol)

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
            exc = {ast.FunctionDef: self.do_import_function_def,
                   ast.BuiltInFunction: self.do_import_function_builtin,
                   ast.SymbolicConstant: self.do_import_constant}
            exc[type(sym)](sym, alias=alias)


    def do_import_constant(self,srcObjConstant, alias=None):
        new_obj = CloneObject.SymbolicConstant(srcObj=srcObjConstant, dst_symbol=alias)
        self._resolve_global_symbol(new_obj.symbol, new_obj)
        self.builddata.symbolicconstants[new_obj.symbol] = new_obj

        assert isinstance(new_obj, SymbolicConstant)

    def do_import_function_builtin(self,srcObjFuncDef, alias=None):
        new_obj = CloneObject.BuiltinFunction(srcObj=srcObjFuncDef, dst_symbol=alias)
        self.builddata.funcdefs[new_obj.funcname] = new_obj

    def do_import_function_def(self,srcObjFuncDef, alias=None):
        new_obj = CloneObject.FunctionDef(srcObj=srcObjFuncDef, dst_symbol=alias)
        self.builddata.funcdefs[new_obj.funcname] = new_obj

    # Function Definitions:
    # #########################
    def open_new_scope(self):
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

        for (symbol, proxy) in self.active_scope.iteritems():

            # If we are in a library, then it is OK to lookup symbols
            # in the global namespace, since they will be constants.
            # (Just make sure its not defined in both places)
            if self.block_type == ast.Library:
                if self.global_scope.hasSymbol(symbol):
                    assert not symbol in f.parameters
                    proxy.set_target(self.global_scope.getSymbol(symbol))
                    continue

            if symbol in f.parameters:
                proxy.set_target(f.parameters[symbol])
                continue
            assert False, 'Unable to find symbol: %s in function definition: %s'%(symbol, f)

        # Close the scope
        self.active_scope = None



    def close_scope_and_create_transition_event(self, event_name, event_params, actions, target_regime):
        # Close up the scope:
        assert self.active_scope is not None
        scope = self.active_scope
        self.active_scope = None

        # Resolve the symbols in the namespace
        for (sym, obj) in scope.iteritems():
            # Resolve Symbol from the Event Parameters:
            if sym in event_params:
                obj.set_target(event_params[sym])
        else:
            # Resolve at global scope:
            obj.set_target(self.global_scope.getSymbolOrProxy(sym))

        src_regime = self.get_current_regime()
        if target_regime is None:
            target_regime = src_regime
        else:
            target_regime = self._current_rt_graph.get_or_create_regime(target_regime)


        self.builddata.transitions_events.append(
            ast.OnEventTransition(event_name=event_name, parameters=event_params, actions= actions, target_regime=target_regime, src_regime=src_regime)
        )



    def create_transition_trigger(self, trigger, actions, target_regime):
        assert self.active_scope is not None
        scope = self.active_scope
        self.active_scope = None

        # Resolve all symbols from the global namespace:
        for (sym, obj) in scope.iteritems():
            # print 'Resolving:', sym
            obj.set_target(self.global_scope.getSymbolOrProxy(sym))
            # print self.global_scope.__dict__

        src_regime = self.get_current_regime()
        if target_regime is None:
            target_regime = src_regime
        else:
            target_regime = self._current_rt_graph.get_or_create_regime(target_regime)

        assert self.active_scope is None
        self.builddata.transitions_triggers.append(ast.OnTriggerTransition(trigger=trigger,
                actions=actions, target_regime=target_regime,
                src_regime=src_regime))

    def create_function_call(self, funcname, parameters):

        # BuiltInFunctions have __XX__
        # Load it if not already exisitng:
        if funcname[0:2] == '__' and not funcname in self.builddata.funcdefs:
            self.builddata.funcdefs[funcname] = StdFuncs.get_builtin_function(funcname, backend=self.library_manager.backend)

        # Allow fully qulaified names that are not explicity imported
        if '.' in funcname and not funcname in self.builddata.funcdefs:
            mod = '.'.join(funcname.split('.')[:-1])
            self.do_import(mod, tokens=[(funcname.split('.')[-1], funcname)])


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
            assert p in func_def.parameters, "Can't find %s in %s" % (p, func_def.parameters)
            # Connect the call parameter to the definition:
            parameters[p].symbol = p
            parameters[p].set_function_def_parameter(func_def.parameters[p])

        # Create the functions
        return ast.FunctionDefInstantiation(parameters=parameters, function_def=func_def)

    # Although Library don't allow assignments, we turn assignments of contants
    # into symbolic constants later, so we allow for them both.
    def add_assignment(self, lhs_name, rhs_ast):

        # Create the assignment object:
        assert self.active_scope == None
        a = ast.EqnAssignmentPerRegime(lhs=lhs_name, rhs=rhs_ast, regime=self.get_current_regime())
        self.builddata._assigments_per_regime.append(a)

    def finalise(self):

        # A few sanity checks....
        # ########################
        assert self.active_scope is None

        from neurounits.librarymanager import LibraryManager
        assert isinstance(self.library_manager, LibraryManager)

        # Resolve the TimeDerivatives into a single object:
        time_derivatives = SingleSetDict()
        maps_tds = defaultdict(SingleSetDict)
        for regime_td in self.builddata._time_derivatives_per_regime:
            maps_tds[regime_td.lhs][regime_td.regime] = regime_td.rhs

        for (sv, tds) in maps_tds.items():

            statevar_obj = ast.StateVariable(sv)
            self._resolve_global_symbol(sv, statevar_obj)

            mapping = dict([(reg, rhs) for (reg,rhs) in tds.items()])
            rhs = ast.EqnTimeDerivativeByRegime(
                    lhs=statevar_obj,
                    rhs_map=ast.EqnRegimeDispatchMap(mapping)
                    )
            time_derivatives[statevar_obj] = rhs

        self.builddata.timederivatives = time_derivatives.values()
        del self.builddata._time_derivatives_per_regime

        ## Resolve the Assignments into a single object:
        assignments = SingleSetDict()
        maps_asses = defaultdict(SingleSetDict)
        for reg_ass in self.builddata._assigments_per_regime:
            maps_asses[reg_ass.lhs][reg_ass.regime] = reg_ass.rhs

        for (ass_var, tds) in maps_asses.items():

            assvar_obj = ast.AssignedVariable(ass_var)
            self._resolve_global_symbol(ass_var, assvar_obj)

            mapping = dict([ (reg, rhs) for (reg,rhs) in tds.items()] )
            rhs = ast.EqnAssignmentByRegime(
                    lhs=assvar_obj,
                    rhs_map=ast.EqnRegimeDispatchMap(mapping)
                    )
            assignments[assvar_obj] = rhs

        self.builddata.assignments = assignments.values()
        del self.builddata._assigments_per_regime

        # Copy rt-grpahs into builddata
        self.builddata.rt_graphs = self._all_rt_graphs.values()

        # OK, perhaps we used some functions or constants from standard libraries,
        # and we didn't import them. Lets let this slide and automatically import them:
        unresolved_symbols = [(k, v) for (k, v) in self.global_scope.iteritems() if not v.is_resolved()]
        for (symbol, proxyobj) in unresolved_symbols:
            if not symbol.startswith('std.'):
                continue
            (lib, token) = symbol.rsplit('.', 1)
            print 'Automatically importing: %s' % symbol
            self.do_import(srclibrary=lib, tokens=[(token, symbol)])

        # We inspect the io_data ('<=>' lines), and use it to:
        #  - resolve the types of unresolved symbols
        #  - set the dimensionality
        # ###################################################

        # Parse the IO data lines:
        io_data = list(itertools.chain(*[parse_io_line(l) for l in self.builddata.io_data_lines]))

        # Update 'Parameter' and 'SuppliedValue' symbols from IO Data:
        param_symbols = [ast.Parameter(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype == IOType.Parameter ]
        for p in param_symbols:
            if self.library_manager.options.allow_unused_parameter_declarations:
                self._resolve_global_symbol(p.symbol, p, expect_is_unresolved=False)
            else:
                self._resolve_global_symbol(p.symbol, p, expect_is_unresolved=True)

        reduce_ports = [ast.AnalogReducePort(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype is IOType.AnalogReducePort ]
        for s in reduce_ports:
            self._resolve_global_symbol(s.symbol, s, expect_is_unresolved=True)


        supplied_symbols = [ast.SuppliedValue(symbol=p.symbol,dimension=p.dimension) for p in io_data if p.iotype is IOType.Input]
        for s in supplied_symbols:
            if self.library_manager.options.allow_unused_suppliedvalue_declarations:
                self._resolve_global_symbol(s.symbol, s, expect_is_unresolved=False)
            else:
                self._resolve_global_symbol(s.symbol, s, expect_is_unresolved=True)

        # We don't need to 'do' anything for 'output' information, since they
        # are 'AssignedValues' so will be resolved already. However, it might
        # contain dimensionality information.
        output_symbols = [p for p in io_data if p.iotype == IOType.Output]
        for o in output_symbols:
            os_obj = RemoveAllSymbolProxy().followSymbolProxy(self.global_scope.getSymbol(o.symbol))
            assert not os_obj.is_dimensionality_known()
            if o.dimension:
                os_obj.set_dimensionality(o.dimension)





        # OK, everything in our namespace should be resoved.  If not, then
        # something has gone wrong.  Look for remaining unresolved symbols:
        # ########################################
        unresolved_symbols = [(k,v) for (k,v) in self.global_scope.iteritems() if not v.is_resolved()]
        # We shouldn't get here!
        if len(unresolved_symbols) != 0:
            raise ValueError('Unresolved Symbols:%s' % ([s[0] for s in unresolved_symbols]))




        # Lets build the Block Object!
        # ################################
        #self._astobject = ast.EqnSet(
        #print self.block_type
        print self.block_type
        self._astobject = self.block_type(
                    library_manager=self.library_manager,
                    builder=self,
                    builddata=self.builddata,
                )

        from neurounits.ast.eqnset import NineMLComponent
        if isinstance(self.block_type, NineMLComponent):
            print 'a---------------------------'
            print 'a---------------------------'
            
            x =  self._astobject._supplied_lut
            print x



        # The object exists, but is not complete and needs some polishing:
        # #################################################################

        from neurounits.visitors.common.plot_networkx import ActionerPlotNetworkX
        # ActionerPlotNetworkX(self._astobject)

        # 1. Resolve the SymbolProxies:
        RemoveAllSymbolProxy().visit(self._astobject)

        # ActionerPlotNetworkX(self._astobject)


        # 2. Setup the meta-data in each node from IO lines
        for io_data in io_data:
            self._astobject.get_terminal_obj(io_data.symbol).set_metadata(io_data)


        # 3. Propagate the dimensionalities accross the system:
        PropogateDimensions.propogate_dimensions(self._astobject)

        # 4. Reduce simple assignments to symbolic constants:
        ReduceConstants().visit(self._astobject)


class EqnSetBuilder(AbstractBlockBuilder):

    def __init__(self, library_manager, name, block_type=ast.EqnSet):
        AbstractBlockBuilder.__init__(self,block_type=block_type, library_manager=library_manager,name=name)

    def add_io_data(self, l):
        self.builddata.io_data_lines.append(l)

    def close_scope_and_create_onevent(self, ev):
        assert self.active_scope is not None
        scope = self.active_scope
        self.active_scope = None

        # Resolve the symbols in the namespace
        for (sym, obj) in scope.iteritems():
            # Resolve Symbol from the Event Parameters:
            if sym in ev.parameters:
                obj.set_target(ev.parameters[sym])
            else:
                obj.set_target(self.global_scope.getSymbolOrProxy(sym))

        # Save this event
        self.builddata.onevents[ev.name] = ev

    def add_timederivative(self, lhs_state_name, rhs_ast):
        # Create the assignment object:
        a = ast.EqnTimeDerivativePerRegime(lhs=lhs_state_name, rhs=rhs_ast, regime=self.get_current_regime())
        self.builddata._time_derivatives_per_regime.append(a)


class LibraryBuilder(AbstractBlockBuilder):

    def __init__(self, library_manager,name):
        AbstractBlockBuilder.__init__(self,block_type=ast.Library, library_manager=library_manager,name=name)






class NineMLComponentBuilder(EqnSetBuilder):

    def __init__(self, library_manager, name):
        EqnSetBuilder.__init__(self,block_type=ast.NineMLComponent, library_manager=library_manager,name=name)


