
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

from neurounits.visitors import ASTVisitorBase
import itertools
import networkx as nx
from itertools import chain
import pylab



import neurounits.ast as ast




class VisitorSymbolDependance(object):



    def __init__(self, component):
        # Build the symbol dependancy graph:
        self.component = component
        self.direct_dependancy_graph = VisitorSymbolDependance.build_direct_dependancy_graph(component)

    def get_assignment_dependancy_ordering(self):
        return self.get_assignment_ordering()

    def get_assignment_ordering(self, ):

        graph = nx.DiGraph()
        for assignment in self.component.assignments:
            deps = self.get_terminal_dependancies(assignment, expand_assignments=False, include_random_variables=False, include_supplied_values=False, include_symbolic_constants=False, include_parameters=False, include_analog_input_ports=False)
            graph.add_node(assignment.lhs)
            for dep in deps:
                assert isinstance(dep, (ast.StateVariable,ast.AssignedVariable, ast.TimeVariable))
                if isinstance(dep, ast.AssignedVariable):
                    graph.add_edge(assignment.lhs, dep)


        assigned_ordering = list( reversed( list(nx.topological_sort(graph)) ) )

        assert len(assigned_ordering) == len(self.component.assignments)
        return assigned_ordering


    def get_terminal_dependancies(self, terminal, expand_assignments, include_random_variables=False, include_supplied_values=True,include_symbolic_constants=True, include_parameters=True, include_analog_input_ports=True):
        """ Does not expand through states"""

        if isinstance( terminal, ast.EqnAssignmentByRegime):
            terminal = terminal.lhs
        if isinstance( terminal, ast.EqnTimeDerivativeByRegime):
            terminal = terminal.lhs

        if isinstance(terminal, ast.SymbolicConstant):
            return []

        assert isinstance(terminal, (ast.StateVariable, ast.AssignedVariable, ast.OnEventStateAssignment, ast.OnConditionTriggerTransition) )

        # Switch lhs to the assignment/time deriatives
        if isinstance( terminal, ast.StateVariable):
            terminal = self.component._eqn_time_derivatives.get_single_obj_by(lhs=terminal)
        if isinstance( terminal, ast.AssignedVariable):
            terminal = self.component._eqn_assignment.get_single_obj_by(lhs=terminal)
        if isinstance( terminal, ast.OnConditionTriggerTransition):
            terminal = terminal.trigger


        return self._get_dependancies(
                node=terminal,
                expand_assignments=expand_assignments,
                include_random_variables=include_random_variables,
                include_supplied_values=include_supplied_values,
                include_symbolic_constants=include_symbolic_constants,
                include_parameters=include_parameters,
                include_analog_input_ports=include_analog_input_ports)


    def _get_dependancies(self, node, expand_assignments, include_random_variables=False, include_supplied_values=True, include_symbolic_constants=True, include_parameters=True, include_analog_input_ports=True, include_inevent_parameters=True, include_time=True):

        dependancies = nx.bfs_successors(self.direct_dependancy_graph, source=node)
        if node in dependancies:
            dependancies = dependancies[node]
        else:
            assert node in self.direct_dependancy_graph.nodes()
            dependancies = []

        dependancies = [d for d in dependancies if not isinstance( d, ast.RTBlock)]





        if expand_assignments:
            dependancies_statevars =   set([dep for dep in dependancies if isinstance(dep, (ast.StateVariable, ast.RandomVariable, ast.SuppliedValue, ast.OnEventDefParameter, ast.TimeVariable))])
            unexpanded_assignment_dependancies = set([dep for dep in dependancies if isinstance(dep, ast.AssignedVariable)])
            assert len(dependancies_statevars) + len(unexpanded_assignment_dependancies) == len(set(dependancies))

            expanded_assignment_dependancies = set([node]) if isinstance(node, ast.AssignedVariable) else set([])

            while unexpanded_assignment_dependancies:

                ass = unexpanded_assignment_dependancies.pop()
                expanded_assignment_dependancies.add(ass)

                assignment_node = self.component._eqn_assignment.get_single_obj_by(lhs=ass)
                ass_deps = nx.bfs_successors(self.direct_dependancy_graph, assignment_node )[assignment_node]

                for ass_dep in ass_deps:
                    if isinstance( ass_dep, (ast.StateVariable, ast.RandomVariable, ast.SuppliedValue, ast.TimeVariable)):
                        dependancies_statevars.add(ass_dep)
                    elif isinstance( ass_dep, ast.AssignedVariable):
                        if ass_dep in expanded_assignment_dependancies:
                            continue
                        elif ass_dep in unexpanded_assignment_dependancies:
                            continue
                        else:
                            unexpanded_assignment_dependancies.add(ass_dep)
                    else:
                        if isinstance(ass_dep, ast.RTBlock):
                                continue
                        assert False

            dependancies = dependancies_statevars


        if include_random_variables == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.RandomVariable)]
        if include_supplied_values == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.SuppliedValue)]
        if include_symbolic_constants == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.SymbolicConstant)]
        if include_parameters == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.Parameter)]
        if include_analog_input_ports == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.AnalogReducePort)]
        if include_inevent_parameters == False:
            dependancies = [d for d in dependancies if not isinstance(d, ast.InEventPortParameter)]


        assert len(dependancies) == len(set(dependancies))
        return dependancies










    @classmethod
    def build_direct_dependancy_graph(cls, component, plot=False):
        import neurounits.ast as ast
        dep_find = _DependancyFinder(component)
        dep_find.visit(component)

        g = nx.DiGraph()
        all_objs = set( list(chain(*dep_find.dependancies.values()))  + dep_find.dependancies.keys() )
        for o in all_objs:
            g.add_node(o)

        for k,v in dep_find.dependancies.items():
            for c in v:
                g.add_edge(k,c)



        if plot:
            nx.draw_networkx(g, with_labels=True, labels={n:repr(n) for n in all_objs} )
            pylab.show()

        return g










def save_deps_for_node(func):
    def new_func(self, node, *args, **kwargs):
        deps = func(self, node, *args, **kwargs)
        self.dependancies[node] = deps
        return deps
    return new_func





class _DependancyFinder(ASTVisitorBase):

    def __init__(self, component):
        self.dependancies = {}


    def VisitLibrary(self, o, **kwargs):
        for a in o.assignments:
            self.dependancies[a.lhs] = self.visit(a)
            self.dependancies[a] = self.visit(a)


    def VisitNineMLComponent(self, o, **kwargs):
        self.visit(o._time_node)
        for a in o.assignments:
            self.dependancies[a.lhs] = self.visit(a)
            self.dependancies[a] = self.visit(a)
        for a in o.timederivatives:
            self.dependancies[a] = self.visit(a)
            self.dependancies[a.lhs] = [a]

        for rt_graph in o._rt_graphs:
            self.dependancies[rt_graph] = []


        for tr in o.transitions:
            for state_assignment in tr.state_assignments:
                self.dependancies[state_assignment] = self.visit(state_assignment.rhs)

            for emitted_event in tr.emitted_events:
                self.dependancies[emitted_event] = self.visit(emitted_event)

        for tr in o.triggertransitions:
            self.dependancies[tr.trigger]=self.visit(tr.trigger)


    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    @save_deps_for_node
    def VisitIfThenElse(self, o, **kwargs):
        d1 = self.visit(o.predicate, **kwargs)
        d2 = self.visit(o.if_true_ast, **kwargs)
        d3 = self.visit(o.if_false_ast, **kwargs)
        return d1 + d2 + d3 

    @save_deps_for_node
    def VisitInEquality(self, o, **kwargs):
        d1 = self.visit(o.lesser_than, **kwargs)
        d2 = self.visit(o.greater_than, **kwargs)
        return d1 + d2


    def VisitBoolAnd(self, o, **kwargs):
        d1 = self.visit(o.lhs, **kwargs)
        d2 = self.visit(o.rhs, **kwargs)
        return d1 + d2

    def VisitBoolOr(self, o, **kwargs):
        d1 = self.visit(o.lhs, **kwargs)
        d2 = self.visit(o.rhs, **kwargs)
        return d1 + d2

    def VisitBoolNot(self, o, **kwargs):
        d1 = self.visit(o.lhs, **kwargs)
        return d1

    # Function Definitions:
    def VisitFunctionDefUser(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefParameter(self, o, **kwargs):
        raise NotImplementedError()

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return [o]

    def VisitParameter(self, o, **kwargs):
        return [o]

    def VisitConstant(self, o, **kwargs):
        return []
    def VisitConstantZero(self, o, **kwargs):
        return []

    def VisitAssignedVariable(self, o, **kwargs):
        return [o]

    def VisitSuppliedValue(self, o, **kwargs):
        return [o]
    def VisitTimeVariable(self, o, **kwargs):
        return [o]
    

    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)

    @save_deps_for_node
    def VisitRegimeDispatchMap(self, o, **kwargs):
        symbols = []
        for rhs in o.rhs_map.values():
            symbols.extend(self.visit(rhs, **kwargs))
        # The RT graph is only a dependance if there is more than one possibility!
        return symbols + ([o.get_rt_graph()] if len(o.rhs_map) > 1 else [] )

    def VisitRTGraph(self, o, **kwargs):
        return []


    def visit_trans(self,o):
        action_deps = []
        for a in o.actions:
            action_deps.extend( self.visit(a, rt_graph=o.rt_graph))

        return list(set(action_deps))

    def VisitOnConditionTriggerTransition(self, o, **kwargs):
        return [o.rt_graph] + self.visit_trans(o) + self.visit(o.trigger)

    def VisitOnTransitionEvent(self, o, **kwargs):
        return [o.rt_graph] + self.visit_trans(o) 

    @save_deps_for_node
    def VisitOnEventStateAssignment(self, o, **kwargs):
        return self.visit(o.rhs)

    def VisitEmitEvent(self, o,):
        return list( chain(*[self.visit(p) for p in o.parameters]) )

    def VisitEmitEventParameter(self, o):
        return self.visit(o.rhs)

    def VisitOnEventDefParameter(self,o):
        #assert False
        return [o]

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)

    @save_deps_for_node
    def VisitAddOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    @save_deps_for_node
    def VisitSubOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    @save_deps_for_node
    def VisitMulOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    @save_deps_for_node
    def VisitDivOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    @save_deps_for_node
    def VisitExpOp(self, o, **kwargs):
        return self.visit(o.lhs)

    @save_deps_for_node
    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return list(itertools.chain(*[self.visit(p) for p in o.parameters.values()]))

    @save_deps_for_node
    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        return list(itertools.chain(*[self.visit(p) for p in o.parameters.values()]))

    @save_deps_for_node
    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        return self.visit(o.rhs_ast)

    def VisitAnalogReducePort(self, o, **kwargs):
        return [o] + list(itertools.chain( *[self.visit(a) for a in o.rhses]))


    def VisitRandomVariable(self, o):
        return list(itertools.chain( *[self.visit(p) for p in o.parameters])) + [o]

    def VisitRandomVariableParameter(self,o):
        return self.visit(o.rhs_ast)
