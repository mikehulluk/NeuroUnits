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

    def __init__(self,  library_manager, builder, builddata,name):
        super(Library,self).__init__(library_manager=library_manager, builder=builder, name=name)
        import neurounits.ast as ast


        # Top-level objects:
        self._function_defs = LookUpDict( builddata.funcdefs, accepted_obj_types=(ast.FunctionDef, ast.BuiltInFunction) )
        self._symbolicconstants = LookUpDict( builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant, ) )
        self._eqn_assignment = LookUpDict( builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,) )

    def get_terminal_obj(self, symbol):
        #print self.functiondefs
        possible_objs = LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.functiondefs).get_objs_by(funcname=symbol)

        #print 'Looking for:', symbol
        #print possible_objs
        if not len(possible_objs) == 1:
            raise KeyError("Can't find terminal: %s" % symbol)

        return possible_objs[0]


    @property
    def functiondefs(self):
        return self._function_defs

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants, key=lambda a: a.symbol)

    @property
    def assignments(self):
        return list( iter(self._eqn_assignment) )

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)


class EqnSet(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata, name):
        super(EqnSet, self).__init__(library_manager=library_manager, builder=builder, name=name)

        import neurounits.ast as ast

        # Top-level objects:
        self._function_defs = LookUpDict( builddata.funcdefs, accepted_obj_types=(ast.FunctionDef) )
        self._symbolicconstants = LookUpDict( builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant, ) )

        self._eqn_assignment = LookUpDict( builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,) )
        self._eqn_time_derivatives = LookUpDict( builddata.timederivatives, accepted_obj_types=(ast.EqnTimeDerivativeByRegime,) )





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








    def get_terminal_obj(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) + \
                        self._supplied_lut.get_objs_by(symbol=symbol) + \
                        self._analog_reduce_ports_lut.get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.state_variables).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)

        #print 'Looking for:', symbol
        #print possible_objs
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

    def propagate_and_check_dimensions(self):
        from .builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self)


    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLComponent(self, **kwargs)


    def __init__(self,  library_manager, builder, builddata, name=None):
        super(NineMLComponent,self).__init__(library_manager=library_manager, builder=builder, builddata=builddata, name=name)

        self._transitions_triggers = LookUpDict( builddata.transitions_triggers )
        self._transitions_events = LookUpDict( builddata.transitions_events )
        self._rt_graphs = LookUpDict( builddata.rt_graphs)


    def __repr__(self):
        return '<NineML Component: %s>' % self.name

    @property
    def rt_graphs(self):
        return self._rt_graphs

    @property
    def transitions(self):
        return itertools.chain( self._transitions_triggers, self._transitions_events)

    def transitions_from_regime(self, regime):
        assert isinstance(regime,Regime)
        return [tr for tr in self.transitions if tr.src_regime == regime]

    def summarise(self):
        print
        print '  Paramters: [%s]' %', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.parameters)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.state_variables)

        print '  Inputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self.suppliedvalues)

        print '  Outputs: [%s]'% ', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.assignedvalues)
        print '  ReducePorts: [%s] '% ', '.join("'%s (%s)'" % (p.symbol, p.get_dimension()) for p in self.analog_reduce_ports)

        print

        print
        print 'NineML Component: %s' % self.name
        print '  Paramters: [%s]' %', '.join("'%s'" %p.symbol for p in self.parameters)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.state_variables)

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
        for rt in self.rt_graphs:
            print '     Graph:', rt
            for regime in rt.regimes:
                print '       Regime:', regime

                for tr in self.transitions_from_regime(regime):
                    print '          Transition:', tr



    def all_ast_nodes(self):
        c = EqnsetVisitorNodeCollector()
        c.visit(self)
        return itertools.chain( *c.nodes.values() )

    def clone(self, ):


        # Nasty Hack - serialise and unserialse to clone the object

        import pickle
        import cStringIO
        c = cStringIO.StringIO()
        pickle.dump(self, c)

        new = pickle.load(cStringIO.StringIO(c.getvalue()))
        return new


        from neurounits.visitors.common.ast_cloning import ASTClone
        return ASTClone().clone_root(self)




class NineMLModule(object):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLModule(self, **kwargs)

    def __init__(self, **kwargs):
        pass


