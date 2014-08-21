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

from base import ASTObject
from neurounits.ast.astobjects import Parameter, SuppliedValue
from neurounits.ast.astobjects_nineml import AnalogReducePort
from neurounits.ast.astobjects_nineml import Regime

from neurounits.units_misc import LookUpDict

import itertools


class Block(ASTObject):

    def __init__(self, name, library_manager, builder):
        super(Block, self).__init__()
        self.name = name
        self.library_manager = library_manager
        self._builder = builder

        # Annotations:
        from neurounits.ast_annotations import ASTTreeAnnotationManager
        self.annotation_mgr = ASTTreeAnnotationManager()

    def annotate_ast(self, annotator, ast_label=None):
        annotator.annotate_ast(self)

        if ast_label is not None:
            self.annotation_mgr.add_annotator(ast_label, annotator)

    @property
    def terminal_symbols(self):
        raise NotImplementedError()

    def get_terminal_obj(self, symbol):
        raise NotImplementedError()

    def has_terminal_obj(self, symbol):
        raise NotImplementedError()

    def to_redoc(self):
        from neurounits.visualisation.mredoc import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)

    @property
    def short_name(self):
        return self.name.split('.')[-1]

    def all_ast_nodes(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        c = EqnsetVisitorNodeCollector()
        c.visit(self)
        return itertools.chain(*c.nodes.values())


class Library(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitLibrary(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata, name):
        super(Library, self).__init__(library_manager=library_manager, builder=builder, name=name)
        import neurounits.ast as ast

        self._function_defs = LookUpDict(builddata.funcdefs, accepted_obj_types=(ast.FunctionDefUser, ast.FunctionDefBuiltIn))
        self._symbolicconstants = LookUpDict(builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant,))
        self._eqn_assignment = LookUpDict(builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,))

    def get_terminal_obj(self, symbol):

        possible_objs = LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol)+ \
                        LookUpDict(self.functiondefs).get_objs_by(funcname=symbol)


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
        return list(iter(self._eqn_assignment))

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)


    @property
    def ordered_assignments_by_dependancies(self):
        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
        ordered_assigned_values =  VisitorSymbolDependance(self).get_assignment_dependancy_ordering()
        ordered_assignments =  [LookUpDict(self.assignments).get_single_obj_by(lhs=av) for av in ordered_assigned_values]
        assert len(ordered_assignments) == len(self.assignments)
        assert set(ordered_assignments) == set(self.assignments)
        return ordered_assignments


class NineMLComponent(Block):

    def run_sanity_checks(self):
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree

        # Check all default regimes are on this graph:
        for rt_graph in self.rt_graphs:
            if rt_graph.default_regime:
                assert rt_graph.default_regime in rt_graph.regimes

        VerifyUnitsInTree(self, unknown_ok=False)

    @classmethod
    def _build_ADD_ast(cls, nodes):
        import neurounits.ast as ast
        assert len(nodes) > 0
        if len(nodes) == 1:
            return nodes[0]
        if len(nodes) == 2:
            return ast.AddOp(nodes[0], nodes[1])
        else:
            return ast.AddOp(nodes[0], cls._build_ADD_ast(nodes[1:]))

    def close_analog_port(self, ap):
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        if len(ap.rhses) == 0:
            assert False, 'No input found for reduce port? (maybe this is OK!)'

        new_node = NineMLComponent._build_ADD_ast(ap.rhses)

        assert new_node is not None
        ReplaceNode.replace_and_check(srcObj=ap, dstObj=new_node, root=self)

        PropogateDimensions.propogate_dimensions(self)

    def close_all_analog_reduce_ports(self):
        for ap in self.analog_reduce_ports:
            self.close_analog_port(ap)

    def simulate(self, **kwargs):
        from neurounits.codegen.python_functor.simulate_component import simulate_component
        return simulate_component(self, **kwargs)

    @classmethod
    def build_compound_component(cls, **kwargs):
        from neurounits.ast_operations.merge_components import build_compound_component
        return build_compound_component(**kwargs)

    def expand_all_function_calls(self):
        from neurounits.visitors.common import FunctionExpander
        FunctionExpander(self)

    @property
    def ordered_assignments_by_dependancies(self):
        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
        ordered_assigned_values =  VisitorSymbolDependance(self).get_assignment_dependancy_ordering()
        ordered_assignments =  [LookUpDict(self.assignments).get_single_obj_by(lhs=av) for av in ordered_assigned_values]
        assert len(ordered_assignments) == len(self.assignments)
        assert set(ordered_assignments) == set(self.assignments)
        return ordered_assignments

    @property
    def assignments(self):
        return sorted(list(iter(self._eqn_assignment)), key=lambda o: o.lhs.symbol)

    @property
    def timederivatives(self):
        return sorted(list(iter(self._eqn_time_derivatives)), key=lambda o: o.lhs.symbol)

    @property
    def assignedvalues(self):
        return sorted(list(self._eqn_assignment.get_objects_attibutes('lhs')), key=lambda a:a.symbol)

    @property
    def state_variables(self):
        return sorted(list(self._eqn_time_derivatives.get_objects_attibutes('lhs')), key=lambda a: a.symbol)

    @property
    def functiondefs(self):
        return iter(self._function_defs)

    @property
    def symbolicconstants(self):
        return sorted(list(self._symbolicconstants), key=lambda a: a.symbol)

    @property
    def parameters(self):
        return self._parameters_lut

    @property
    def suppliedvalues(self):
        return self._supplied_lut

    @property
    def analog_reduce_ports(self):
        return self._analog_reduce_ports_lut

    @property
    def random_variable_nodes(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        from neurounits.ast import RandomVariable
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[RandomVariable])

    @property
    def autoregressive_model_nodes(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        from neurounits.ast import AutoRegressiveModel
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[AutoRegressiveModel])

    @property
    def conditioncrosses_nodes(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        from neurounits.ast import OnConditionCrossing
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[OnConditionCrossing])

    @property
    def terminal_symbols(self):
        possible_objs = itertools.chain(
            self._parameters_lut,
            self._supplied_lut,
            self._analog_reduce_ports_lut,
            self.assignedvalues,
            self.state_variables,
            self.symbolicconstants,
            [self._time_node],
            )

        possible_objs = list(possible_objs)
        for t in possible_objs:
            assert isinstance(t, ASTObject)
        return possible_objs

    @property
    def all_input_terminals(self):
        #TODO - whty is state_variables in this list?
        return list(itertools.chain(
                        self._parameters_lut,
                        self._supplied_lut,
                        self._analog_reduce_ports_lut,
                        self.state_variables,
                        [self._time_node]
                        )
                    )



    def all_terminal_objs(self):
        possible_objs = self._parameters_lut.get_objs_by() \
            + self._supplied_lut.get_objs_by() \
            + self._analog_reduce_ports_lut.get_objs_by() \
            + LookUpDict(self.assignedvalues).get_objs_by() \
            + LookUpDict(self.state_variables).get_objs_by() \
            + LookUpDict(self.symbolicconstants).get_objs_by()

        return possible_objs

    def get_terminal_obj_or_port(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) \
            + self._supplied_lut.get_objs_by(symbol=symbol) \
            + self._analog_reduce_ports_lut.get_objs_by(symbol=symbol) \
            + LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol) \
            + LookUpDict(self.state_variables).get_objs_by(symbol=symbol) \
            + LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol) \
            + self.input_event_port_lut.get_objs_by(symbol=symbol) \
            + self.output_event_port_lut.get_objs_by(symbol=symbol) \
            + (([self._time_node] if self._time_node.symbol
               == symbol else []))

        if not len(possible_objs) == 1:
            all_syms = [ p.symbol for p in self.all_terminal_objs() ] + self.input_event_port_lut.get_objects_attibutes(attr='symbol')
            raise KeyError("Can't find terminal/EventPort: '%s' \n (Terminals/EntPorts found: %s)" % (symbol, ','.join(all_syms)))

        return possible_objs[0]

    def get_terminal_obj(self, symbol):
        possible_objs = self._parameters_lut.get_objs_by(symbol=symbol) \
            + self._supplied_lut.get_objs_by(symbol=symbol) \
            + self._analog_reduce_ports_lut.get_objs_by(symbol=symbol) \
            + LookUpDict(self.assignedvalues).get_objs_by(symbol=symbol) \
            + LookUpDict(self.state_variables).get_objs_by(symbol=symbol) \
            + LookUpDict(self.symbolicconstants).get_objs_by(symbol=symbol) \
            + (([self._time_node] if self._time_node.symbol
               == symbol else []))

        if not len(possible_objs) == 1:
            all_syms = [ p.symbol for p in self.all_terminal_objs()]
            raise KeyError("Can't find terminal: '%s' \n (Terminals found: %s)" % (symbol, ','.join(sorted(all_syms))))

        return possible_objs[0]

    # Recreate each time - this is not! efficient!!
    @property
    def _parameters_lut(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[Parameter])

    @property
    def _supplied_lut(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[SuppliedValue])

    @property
    def _analog_reduce_ports_lut(self):
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[AnalogReducePort])

    @property
    def input_event_port_lut(self):
        import neurounits.ast as ast
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[ast.InEventPort])

    @property
    def output_event_port_lut(self):
        import neurounits.ast as ast
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        return LookUpDict(t.nodes[ast.OutEventPort])

    @property
    def get_time_node(self):
        import neurounits.ast as ast
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
        t = EqnsetVisitorNodeCollector(obj=self)
        nodes = list(t.nodes[ast.TimeVariable])
        if len(nodes) == 0:
            return None
        elif len(nodes) == 1:
            return nodes[0]
        else:
            assert False

    @property
    def time_node(self):
        return self.get_time_node

    def has_terminal_obj(self, symbol):
        try:
            self.get_terminal_obj(symbol=symbol)
            return True
        except KeyError:
            return False
        except:
            raise

    # These should be tidied up:
    def getSymbolDependancicesDirect(self, sym, include_constants=False, include_parameters=True):
        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
        return VisitorSymbolDependance(self).get_terminal_dependancies(sym, expand_assignments=False, include_parameters=include_parameters)

    def getSymbolDependancicesIndirect(self, sym, include_constants=False, include_ass_in_output=False):
        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
        return VisitorSymbolDependance(self).get_terminal_dependancies(sym, expand_assignments=True)

    def getSymbolMetadata(self, sym):
        assert sym in self.terminal_symbols
        if not sym._metadata:
            return None
        if isinstance(sym._metadata, dict):
            return sym._metadata
        return sym._metadata.metadata

    def propagate_and_check_dimensions(self):
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self)

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLComponent(self, **kwargs)

    def assignedvariable_to_assignment(self, assignedvariable):
        from neurounits import ast
        assert isinstance(assignedvariable, ast.AssignedVariable)
        return self._eqn_assignment.get_single_obj_by(lhs=assignedvariable)


    def __init__(self,  library_manager, builder, builddata, name=None):
        super(NineMLComponent, self).__init__(library_manager=library_manager, builder=builder,  name=name)


        import neurounits.ast as ast

        # Top-level objects:
        self._function_defs = LookUpDict(builddata.funcdefs, accepted_obj_types=(ast.FunctionDefUser))
        self._symbolicconstants = LookUpDict(builddata.symbolicconstants, accepted_obj_types=(ast.SymbolicConstant,))

        self._eqn_assignment = LookUpDict(builddata.assignments, accepted_obj_types=(ast.EqnAssignmentByRegime,))
        self._eqn_time_derivatives = LookUpDict(builddata.timederivatives, accepted_obj_types=(ast.EqnTimeDerivativeByRegime,))


        self._transitions_conditiontriggers = LookUpDict(builddata.transitions_conditiontriggers)
        self._transitions_events = LookUpDict(builddata.transitions_events)
        self._rt_graphs = LookUpDict(builddata.rt_graphs)

        self._time_node = builddata.time_node

        # This is a list of internal event port connections:
        self._event_port_connections = LookUpDict()

        from neurounits.ast import CompoundPortConnector
        # This is a list of the available connectors from this component
        self._interface_connectors = LookUpDict(accepted_obj_types=(CompoundPortConnector,), unique_attrs=('symbol',))









    def add_interface_connector(self, multiportconnector):
        self._interface_connectors._add_item(multiportconnector)



    def build_interface_connector(self, local_name, porttype, direction, wire_mapping_txts):
        assert isinstance(local_name, basestring)
        assert isinstance(porttype, basestring)
        assert isinstance(direction, basestring)
        for src, dst in wire_mapping_txts:
            assert isinstance(src, basestring)
            assert isinstance(dst, basestring)

        import neurounits.ast as ast
        interface_def = self.library_manager.get(porttype)
        wire_mappings = []
        for wire_mapping_txt in wire_mapping_txts:
            wire_map = ast.CompoundPortConnectorWireMapping(
                            component_port = self.get_terminal_obj(wire_mapping_txt[0]),
                            interface_port = interface_def.get_wire(wire_mapping_txt[1]),
                            )
            wire_mappings.append(wire_map)

        conn = ast.CompoundPortConnector(symbol=local_name, interface_def = interface_def, wire_mappings=wire_mappings, direction=direction)
        self.add_interface_connector(conn)

    def add_event_port_connection(self, conn):
        assert conn.dst_port in self.input_event_port_lut
        assert conn.src_port in self.output_event_port_lut
        self._event_port_connections._add_item(conn)

    def __repr__(self):
        return '<NineML Component: %s [Supports interfaces: %s ]>' % (self.name, ','.join([ "'%s'" % conn.interface_def.name for conn in self._interface_connectors]))

    @property
    def rt_graphs(self):
        return self._rt_graphs

    @property
    def transitions(self):
        return itertools.chain(self._transitions_conditiontriggers, self._transitions_events)

    @property
    def eventtransitions(self):
        return self._transitions_events

    @property
    def conditiontriggertransitions(self):
        return self._transitions_conditiontriggers

    def transitions_from_regime(self, regime):
        assert isinstance(regime, Regime)
        return [tr for tr in self.transitions if tr.src_regime == regime]

    def eventtransitions_from_regime(self, regime):
        assert isinstance(regime, Regime)

        return [tr for tr in self.eventtransitions if tr.src_regime == regime]

    def conditiontriggertransitions_from_regime(self, regime):
        assert isinstance(regime, Regime)
        return [tr for tr in self.conditiontriggertransitions if tr.src_regime == regime]

    def _summarise_node_full(self):
        return self.summarise()

    def _summarise_node_short(self):
        return 'NineML Component: %s' % self.name

    def summarise(self):
        print
        print 'NineML Component: %s' % self.name
        print '  Paramters: [%s]' %', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self._parameters_lut)
        print '  StateVariables: [%s]' % ', '.join("'%s'" %p.symbol for p in self.state_variables)

        print '  Inputs: [%s]'% ', '.join("'%s'" %p.symbol for p in self._supplied_lut)

        print '  Outputs: [%s]'% ', '.join("'%s (%s)'" %(p.symbol, p.get_dimension()) for p in self.assignedvalues)
        print '  ReducePorts: [%s] '% ', '.join("'%s (%s)'" % (p.symbol, p.get_dimension()) for p in self.analog_reduce_ports)

        print

        print

        print '  Time Derivatives:'

        for td in self.timederivatives:
            print '    %s -> ' % td.lhs.symbol

        print '  Assignments:'
        for td in self.assignments:
            print '    %s -> ' % td.lhs.symbol

        print '  RT Graphs'
        for rt in self.rt_graphs:
            print '     Graph:', rt
            for regime in rt.regimes:
                print '       Regime:', regime

                for tr in self.transitions_from_regime(regime):
                    print '          Transition:', tr

    def get_initial_regimes(self, initial_regimes=None):
        if initial_regimes is None:
            initial_regimes = {}

        rt_graphs = self.rt_graphs

        # Sanity Check:
        for rt_graph in rt_graphs:
            if rt_graph.default_regime:
                assert rt_graph.default_regime in rt_graph.regimes

        # Resolve initial regimes:
        # ========================
        # i. Initial, make initial regimes 'None', then lets try and work it out:
        current_regimes = dict([(rt, None) for rt in rt_graphs])

        # ii. Is there just a single regime?
        for (rt_graph, regime) in current_regimes.items():
            if len(rt_graph.regimes) == 1:
                current_regimes[rt_graph] = rt_graph.regimes.get_single_obj_by()

        # iii. Do the transion graphs have a 'initial' block?
        for rt_graph in rt_graphs:
            if rt_graph.default_regime is not None:
                current_regimes[rt_graph] = rt_graph.default_regime

        # iv. Explicitly provided:
        for (rt_name, regime_name) in initial_regimes.items():
            rt_graph = rt_graphs.get_single_obj_by(name=rt_name)
            assert current_regimes[rt_graph] is None, "Initial state for '%s' set twice " % rt_graph.name
            current_regimes[rt_graph]=rt_graph.get_regime(name=regime_name)

        # v. Check everything is hooked up OK:
        for rt_graph, regime in current_regimes.items():
            assert regime is not None, " Start regime for '%s' not set! " % rt_graph.name
            assert regime in rt_graph.regimes, 'regime: %s [%s]' % (repr(regime), rt_graph.regimes)

        return current_regimes

    def get_initial_state_values(self, initial_state_values):
        from neurounits import ast
        # Resolve the inital values of the states:

        state_values = {}
        # Check initial state_values defined in the 'initial {...}' block: :
        for td in self.timederivatives:
            sv = td.lhs
            if sv.initial_value:
                assert isinstance(sv.initial_value, ast.ConstValue)
                state_values[sv.symbol] = sv.initial_value.value

        for (k, v) in initial_state_values.items():
            assert not k in state_values, 'Double set intial values: %s' % k
            assert k in [td.lhs.symbol for td in self.timederivatives]
            state_values[k]= v

        return state_values

    def clone(self):

        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        from neurounits.visitors.common.ast_node_connections import ASTAllConnections
        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector

        class ReplaceNodeHack(ReplaceNode):

            def __init__(self, mapping_dict):
                assert isinstance(mapping_dict, dict)
                self.mapping_dict = mapping_dict

            def replace_or_visit(self, o):
                return self.replace(o)

            def replace(self, o):
                if o in self.mapping_dict:
                    return self.mapping_dict[o]
                else:
                    return o

        from neurounits.visitors.common.ast_cloning import ASTClone
        from collections import defaultdict

        import neurounits.ast as ast

        # CONCEPTUALLY THIS IS VERY SIMPLE< BUT THE CODE
        # IS A HORRIBLE HACK!
		#TODO!

        no_remap = (ast.MultiportInterfaceDef, ast.MultiportInterfaceDefWireContinuous, ast.MultiportInterfaceDefWireEvent, ast.FunctionDefBuiltIn, ast.FunctionDefParameter)
        # First, lets clone each and every node:
        old_nodes = list(set(list(EqnsetVisitorNodeCollector(self).all())))
        old_to_new_dict = {}
        for old_node in old_nodes:

            if not isinstance(old_node, no_remap):
                new_node = ASTClone().visit(old_node)
            else:
                new_node = old_node

            assert type(old_node) == type(new_node)
            old_to_new_dict[old_node] = new_node

        # Clone self:
        old_to_new_dict[self] = ASTClone().visit(self)

        # Check that all the nodes hav been replaced:
        overlap = (set(old_to_new_dict.keys()) & set(old_to_new_dict.values()))
        for o in overlap:
            assert isinstance(o, no_remap)

        # Now, lets visit each of the new nodes, and replace (old->new) on it:
        # Build the mapping dictionary:
        mapping_dict = {}
        for (old_repl, new_repl) in old_to_new_dict.items():

            if isinstance(old_repl, no_remap):
                continue

            mapping_dict[old_repl] = new_repl

        # Remap all the nodes:
        for new_node in old_to_new_dict.values():

            node_mapping_dict = mapping_dict.copy()
            if new_node in node_mapping_dict:
                del node_mapping_dict[new_node]

            replacer = ReplaceNodeHack(mapping_dict=node_mapping_dict)
            new_node.accept_visitor(replacer)

        # ok, so the clone should now be all clear:
        new_obj = old_to_new_dict[self]

        new_nodes = list(EqnsetVisitorNodeCollector(new_obj).all())

        # Who points to what!?
        connections_map_obj_to_conns = {}
        connections_map_conns_to_objs = defaultdict(list)
        for node in new_nodes:

            conns = list(node.accept_visitor(ASTAllConnections()))
            connections_map_obj_to_conns[node] = conns
            for c in conns:
                connections_map_conns_to_objs[c].append(node)





        shared_nodes = set(new_nodes) & set(old_nodes)
        shared_nodes_invalid = [sn for sn in shared_nodes if not isinstance(sn, no_remap)]

        if len(shared_nodes_invalid) != 0:
            print 'Shared Nodes:'
            print shared_nodes_invalid
            for s in shared_nodes_invalid:
                print ' ', s, s in old_to_new_dict
                print '  Referenced by:'
                for c in connections_map_conns_to_objs[s]:
                    print '    *', c
                print
            assert len(shared_nodes_invalid) == 0


        return new_obj



    def has_state(self):
        #assert False, 'Removed August 2014'
        for rt_graph in self.rt_graphs:
            if len(rt_graph.regimes) >1:
                return True
        return len(self.timederivatives)



