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

from neurounits.units_misc import Chainmap
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from .base import ASTObject
from neurounits.ast.astobjects import Parameter, SuppliedValue, AssignedVariable
from neurounits.ast.astobjects_nineml import AnalogReducePort
from neurounits.ast.astobjects_nineml import Regime
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
from neurounits.io_types import IOType
from neurounits.units_misc import LookUpDict


import itertools


class Block(object):

    def __init__(self, name, library_manager, builder):
        super(Block, self).__init__()
        # General info, and connected objects:
        self.name = name
        self.library_manager = library_manager
        self._builder = builder

    @property
    def terminal_symbols(self):
        raise NotImplementedError()

    def get_terminal_obj(self, symbol):
        raise NotImplementedError()

    def has_terminal_obj(self, symbol):
        raise NotImplementedError()

    def to_redoc(self):
        from neurounits.writers import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)


class Library(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitLibrary(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata):
        super(Library,self).__init__(library_manager=library_manager, builder=builder, name=builddata.eqnset_name)

        # We have to read the _eqn_assignment, although they should be
        # reduced during the conversion to symbolic constants.
        self._eqn_assignment = dict( [(o.lhs, o) for o in builddata.assignments ] )
        self._function_defs = builddata.funcdefs
        self._symbolicconstants = builddata.symbolicconstants

    def get_terminal_obj(self, sym):
        if sym in self._symbolicconstants:
            return self._symbolicconstants[sym]
        if sym in self._function_defs:
            return self._function_defs[sym]
        assert False, "Can't find Symbol: %s in: %s" % (sym, self.name)

    @property
    def functiondefs(self):
        return self._function_defs.values()

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants.values(), key=lambda a: a.symbol)

    def _cache_nodes(self):
        pass


class EqnSet(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata, name=None):
        if name == None:
            name = builddata.eqnset_name

        super(EqnSet, self).__init__(library_manager=library_manager, builder=builder, name=name)

        # Metadata about the inputs and outputs:
        #self.io_data = io_data
        #self.initial_conditions = [p for p in io_data if p.iotype == IOType.InitialCondition]
        import neurounits.ast as ast

        # Top-level objects:
        print 'Getting assignments:'
        print builddata.assignments
        self._eqn_assignment = LookUpDict( builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,) )
        print 'DONE!'


        self._function_defs = LookUpDict( builddata.funcdefs, accepted_obj_types=(ast.FunctionDef) )
        self._eqn_time_derivatives = LookUpDict( builddata.timederivatives, accepted_obj_types=(ast.EqnTimeDerivativeByRegime,) )
        self._symbolicconstants = LookUpDict( builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant, ) )
       
        self._on_events = builddata.onevents

        # Symbols in equations, these values are
        # cached and regenerated by a call to '_cache_nodes'
        #self._parameters = None
        #self._supplied_values = None

        # Initialise _parameters and _supplied_values cache.
        self._cache_nodes()

    def _cache_nodes(self):
        pass
    #    t = EqnsetVisitorNodeCollector()
    #    t.visit(self)
    #    self._parameters = t.nodes[Parameter]
    #    self._supplied_values = t.nodes[SuppliedValue]
    #    self._analog_reduce_ports = t.nodes[AnalogReducePort]

    @property
    def onevents(self):
        return self._on_events.values()


    @property
    def states(self):
        return self.state_variables
        #return sorted(list(self._eqn_time_derivatives), key=lambda a:a.symbol)

    # OK:
    @property
    def assignments(self):
        return list( iter(self._eqn_assignment) )

    @property
    def timederivatives(self):
        return list( iter(self._eqn_time_derivatives) )

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)

    @property
    def state_variables(self):
        return sorted(list(self._eqn_time_derivatives.get_objects_attibutes('lhs')), key=lambda a:a.symbol)

    @property
    def functiondefs(self):
        return iter(self._function_defs)

    @property
    def symbolicconstants(self):
        return sorted(list(self._symbolicconstants), key=lambda a:a.symbol)

    @property
    def parameters(self):
        return self._parameters

    @property
    def suppliedvalues(self):
        return self._supplied_values

    @property
    def analog_reduce_ports(self):
        return self._analog_reduce_ports_lut

    @property
    def terminal_symbols(self):
        possible_objs = itertools.chain(
                        self._parameters_lut,
                        self._supplied_lut,
                        self._analog_reduce_ports_lut,
                        self.assignedvalues,
                        self.state_variables,
                        self.symbolicconstants)

        possible_objs = list(possible_objs)
        for t in possible_objs:
            assert isinstance(t, ASTObject)
        return possible_objs
        



        ts = list(self.states) + list(self.assignedvalues) \
            + list(self.parameters) + list(self.suppliedvalues) \
            + list(self.symbolicconstants) + list(self.analog_reduce_ports)
        for t in ts:
            assert isinstance(t, ASTObject)
        return ts




    def get_terminal_obj(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) + \
                        self._supplied_lut.get_objs_by(symbol=symbol) + \
                        self._analog_reduce_ports_lut.get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.state_variables).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)

        print 'Looking for:', symbol
        print possible_objs
        if not len(possible_objs) == 1:
            raise KeyError("Can't find terminal: %s" % symbol)

        return possible_objs[0]


    # Recreate each time - this is not! efficient!!
    @property
    def _parameters_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[Parameter] )

    @property
    def _supplied_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        
        return LookUpDict(t.nodes[SuppliedValue] )
    @property
    def _analog_reduce_ports_lut(self):
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[AnalogReducePort] )


    def has_terminal_obj(self, symbol):
        try:
            self.get_terminal_obj(symbol=symbol)
            return True
        except KeyError:
            return False
        except:
            raise

    #def _getSuppliedValuesDict(self):
    #    return dict([(s.symbol, s) for s in self._supplied_values])

    #def _getAnalogPortsDict(self):
    #    return dict([(s.symbol, s) for s in self._analog_reduce_ports])

    #def _getParametersDict(self):
    #    return dict([(s.symbol, s) for s in self._parameters])

    #def _getAssignedVariablesDict(self):
    #    return dict([(ass.lhs.symbol, ass.lhs) for ass in self._eqn_assignment.values()])

    #def _getStateVariablesDict(self):
    #    return dict([(td.lhs.symbol, td.lhs) for td in self._eqn_time_derivatives.values()])


    # These should be tidied up:
    def getSymbolDependancicesDirect(self, sym, include_constants=False):

        assert sym in self.terminal_symbols

        if isinstance(sym, AssignedVariable):
            sym = self._eqn_assignment[sym]

        d = VisitorFindDirectSymbolDependance()

        return list(set(d.visit(sym)))

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
        return self.get_terimal_symbol_obj(sym)._metadata._metadata


class NineMLComponent(EqnSet):
    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLComponent(self, **kwargs)


    def __init__(self,  library_manager, builder, builddata, name=None):

        self._transitions_triggers = LookUpDict( builddata.transitions_triggers )
        self._transitions_events = LookUpDict( builddata.transitions_events )
        self.rt_graphs = LookUpDict( builddata.rt_graphs)

        if name == None:
            name = builddata.eqnset_name

        super(NineMLComponent,self).__init__(library_manager=library_manager, builder=builder, builddata=builddata, name=name)

        self._cache_nodes()

    @property
    def transitions(self):
        return itertools.chain( self._transitions_triggers, self._transitions_events)


    def __repr__(self):
        return '<NineML Component: %s>' % self.name

    def transitions_from_regime(self, regime):
        assert isinstance(regime,Regime)
        return [tr for tr in self.transitions if tr.src_regime == regime]

    def summarise(self):
        print
        print '  Paramters: [%s]' %', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.parameters)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.states)

        print '  Inputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self.suppliedvalues)

        print '  Outputs: [%s]'% ', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.assignedvalues)
        print '  ReducePorts: [%s] '% ', '.join("'%s (%s)'" % (p.symbol, p.get_dimension()) for p in self.analog_reduce_ports)

        print

        print
        print 'NineML Component: %s' % self.name
        print '  Paramters: [%s]' %', '.join("'%s'" %p.symbol for p in self.parameters)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.states)

        print '  Inputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self.suppliedvalues)

        print '  Outputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self.assignedvalues)
        print '  ReducePorts: [%s]'% ', '.join("'%s'" %p.symbol for p in self.analog_reduce_ports)

        print '  Time Derivatives:'

        for td in self.timederivatives:
            print '    %s -> ' % td.lhs.symbol
            for (regime, rhs) in td.rhs_map.rhs_map.items():
                print '      [%s] -> %s' % (regime.ns_string(), rhs)

        print '  Assignments:'
        for td in self.assignments:
            print '    %s -> ' % td.lhs.symbol
            for (regime, rhs) in td.rhs_map.rhs_map.items():
                print '      [In Regime:%s] -> %s' % (regime.ns_string(), rhs)

        print '  RT Graphs'
        for rt in self.rt_graphs.values():
            print '     Graph:', rt
            for regime in rt.regimes.values():
                print '       Regime:', regime

                for tr in self.transitions_from_regime(regime):
                    print '          Transition:', tr



    def all_ast_nodes(self):
        c = EqnsetVisitorNodeCollector()
        c.visit(self)
        return itertools.chain( *c.nodes.values() )

    def clone(self, ):
        from neurounits.visitors.common.ast_cloning import ASTClone
        return ASTClone().clone_root(self)




class NineMLModule(object):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLModule(self, **kwargs)

    def __init__(self, **kwargs):
        pass


