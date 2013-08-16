
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

    #@classmethod
    #def get_assignment_dependancy_ordering(cls, eqnset):
    #    from neurounits.ast.astobjects import AssignedVariable
    #    deps = dict([(ass.lhs, VisitorFindDirectSymbolDependance_OLD().visit(ass.rhs_map)) for ass in eqnset.assignments])

    #    ordered = []
    #    to_order = set(deps.keys())

    #    while to_order:
    #        found = False
    #        for o in sorted(to_order, key=lambda o:o.symbol):
    #            o_deps = [d for d in deps[o] if type(d) == AssignedVariable]
    #            o_deps_unsatisfied = [d for d in o_deps if not d in ordered]
    #            if len(o_deps_unsatisfied) == 0:
    #                ordered.append(o)
    #                to_order.remove(o)
    #                found = True
    #                break
    #        # Prevent recursion:
    #        assert found == True, """Can't find the dependencies for: %s"""%",".join( [o.symbol for o in to_order] )

    #    assert len(ordered) == len(eqnset._eqn_assignment)
    #    return ordered

    #@classmethod
    #def get_assignment_dependancy_ordering_recursive(cls, eqnset, ass):
    #    from neurounits.ast.astobjects import AssignedVariable
    #    D = VisitorFindDirectSymbolDependance_OLD()
    #    D.visit(eqnset)

    #    def ass_deps(a):
    #        return [t for t in D.dependancies[a] if isinstance(t, AssignedVariable)]

    #    # resolved_deps = set()

    #    required_deps = set(ass_deps(ass))

    #    # required_deps = set()

    #    # Find all the dependancies:
    #    start_dep_len = None
    #    while start_dep_len != len(required_deps):
    #        start_dep_len = len(required_deps)
    #        to_add = set()
    #        for i in required_deps:
    #            for i_dep in ass_deps(i):
    #                if not i_dep in required_deps:
    #                    to_add.add(i_dep)

    #        required_deps = required_deps | to_add

    #    op = [o for o in cls.get_assignment_dependancy_ordering(eqnset) if o in required_deps]
    #    return op

    #def __init__(self):
    #    self.dependancies = {}

#class SymbolDependance


class VisitorSymbolDependance(object):



    def __init__(self, component):
        # Build the symbol dependancy graph:
        self.component = component
        self.direct_dependancy_graph = VisitorSymbolDependance.build_direct_dependancy_graph(component)

    def get_assignment_dependancy_ordering(self):
        return self.get_assignment_ordering()

    def get_assignment_ordering(self, ):
        # Copy the graph, and add nodes from assigned variables to thier right hand sides:
        #graph = self.direct_dependancy_graph.copy()

        #for assignment in self.component.assignments:
        #    print 'Removing:', repr(assignment)
        #    graph.remove_node(assignment)
        #    #graph.add_edge(assignment.lhs, assignment)

        #nx.draw_networkx(graph, with_labels=True, labels={n:repr(n) for n in graph.nodes()} )
        #pylab.show()
        #t = nx.topological_sort(graph)

        #print t
        graph = nx.DiGraph()
        for assignment in self.component.assignments:
            deps = self.get_terminal_dependancies(assignment, expand_assignments=False, include_random_variables=False, include_supplied_values=False)
            graph.add_node(assignment.lhs)
            for dep in deps:
                print dep
                assert isinstance(dep, (ast.StateVariable,ast.AssignedVariable))
                if isinstance(dep, ast.AssignedVariable):
                    graph.add_edge(assignment.lhs, dep)


        assigned_ordering = list( reversed( list(nx.topological_sort(graph)) ) )
        print assigned_ordering

        assert len(assigned_ordering) == len(self.component.assignments)
        return assigned_ordering


    def get_terminal_dependancies(self, terminal, expand_assignments, include_random_variables=False, include_supplied_values=True):
        """ Does not expand through states"""

        if isinstance( terminal, ast.EqnAssignmentByRegime):
            terminal = terminal.lhs
        if isinstance( terminal, ast.EqnTimeDerivativeByRegime):
            terminal = terminal.lhs

        assert isinstance(terminal, (ast.StateVariable, ast.AssignedVariable, ast.OnEventStateAssignment, ast.OnTriggerTransition) )

        # Switch lhs to the assignment/time deriatives
        if isinstance( terminal, ast.StateVariable):
            terminal = self.component._eqn_time_derivatives.get_single_obj_by(lhs=terminal)
        if isinstance( terminal, ast.AssignedVariable):
            terminal = self.component._eqn_assignment.get_single_obj_by(lhs=terminal)
        if isinstance( terminal, ast.OnTriggerTransition):
            terminal = terminal.trigger


        return self._get_dependancies(node=terminal, expand_assignments=expand_assignments, include_random_variables=include_random_variables, include_supplied_values=include_supplied_values)


    def _get_dependancies(self, node, expand_assignments, include_random_variables=False, include_supplied_values=True):

        dependancies = nx.bfs_successors(self.direct_dependancy_graph, source=node)
        if node in dependancies:
            dependancies = dependancies[node]
        else:
            assert node in self.direct_dependancy_graph.nodes()
            dependancies = []

        dependancies = [d for d in dependancies if not isinstance( d, ast.RTBlock)]

        if expand_assignments:
            dependancies_statevars =   set([dep for dep in dependancies if isinstance(dep, (ast.StateVariable, ast.RandomVariable, ast.SuppliedValue))])
            unexpanded_assignment_dependancies = set([dep for dep in dependancies if isinstance(dep, ast.AssignedVariable)])
            assert len(dependancies_statevars) + len(unexpanded_assignment_dependancies) == len(set(dependancies))

            expanded_assignment_dependancies = set([node]) if isinstance(node, ast.AssignedVariable) else set([])

            while unexpanded_assignment_dependancies:

                ass = unexpanded_assignment_dependancies.pop()
                expanded_assignment_dependancies.add(ass)

                assignment_node = self.component._eqn_assignment.get_single_obj_by(lhs=ass)
                ass_deps = nx.bfs_successors(self.direct_dependancy_graph, assignment_node )[assignment_node]

                for ass_dep in ass_deps:
                    if isinstance( ass_dep, (ast.StateVariable, ast.RandomVariable, ast.SuppliedValue)):
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
            color_lut = {
                    ast.AssignedVariable: 'green',
                    ast.StateVariable: 'blue', }
            color = color_lut[type(o)] if type(o) in color_lut else 'red'

            g.add_node(o, label=repr(o), color=color)

        for k,v in dep_find.dependancies.items():
            for c in v:
                g.add_edge(k,c)



        if plot or True:
            #pylab.ion()
            nx.draw_networkx(g, with_labels=True, labels={n:repr(n) for n in all_objs} )
            #pylab.show()

        return g














class _DependancyFinder(ASTVisitorBase):

    def __init__(self, component):
        self.dependancies = {}

    def VisitNineMLComponent(self, o, **kwargs):
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
                print 'SETTING DEPS FOR ASSIGNMENT!!'
                print state_assignment
                print 'deps: ', self.dependancies[state_assignment]

            for emitted_event in tr.emitted_events:
                self.dependancies[emitted_event] = self.visit(emitted_event)

        for tr in o.triggertransitions:
            self.dependancies[tr.trigger]=self.visit(tr.trigger)

            #tr_deps =self.visit(tr)
            #import neurounits.ast as ast
            #tr_deps = [o for o in tr_deps if not (isinstance(o, ast.SuppliedValue) and o.symbol=='t') ]
            #self.dependancies[tr.rt_graph].extend ( tr_deps)

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    def VisitIfThenElse(self, o, **kwargs):
        d1 = self.visit(o.predicate, **kwargs)
        d2 = self.visit(o.if_true_ast, **kwargs)
        d3 = self.visit(o.if_false_ast, **kwargs)
        return d1 + d2 + d3

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

    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)

    def VisitRegimeDispatchMap(self, o, **kwargs):
        # Visit the RT graph, to work out what it depends on!
        #self.visit(o.get_rt_graph())

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

    def VisitOnTransitionTrigger(self, o, **kwargs):
        return [o.rt_graph] + self.visit_trans(o) + self.visit(o.trigger)
    def VisitOnTransitionEvent(self, o, **kwargs):
        return [o.rt_graph] + self.visit_trans(o)

    def VisitOnEventStateAssignment(self, o, **kwargs):
        return self.visit(o.rhs)

    def VisitEmitEvent(self, o,):
        return list( chain(*[self.visit(p) for p in o.parameters]) )

    def VisitEmitEventParameter(self, o):
        return self.visit(o.rhs)

    def VisitOnEventDefParameter(self,o):
        return []

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)

    def VisitAddOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    def VisitSubOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    def VisitMulOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    def VisitDivOp(self, o, **kwargs):
        return self.visit(o.lhs) + self.visit(o.rhs)

    def VisitExpOp(self, o, **kwargs):
        return self.visit(o.lhs)

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        #assert False
        return list(itertools.chain(*[self.visit(p) for p in o.parameters.values()]))
    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        assert False
        return list(itertools.chain(*[self.visit(p) for p in o.parameters.values()]))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return self.visit(o.rhs_ast)

    def VisitAnalogReducePort(self, o, **kwargs):
        return [o] + list(itertools.chain( *[self.visit(a) for a in o.rhses]))


    def VisitRandomVariable(self, o):
        return list(itertools.chain( *[self.visit(p) for p in o.parameters])) + [o]

    def VisitRandomVariableParameter(self,o):
        return self.visit(o.rhs_ast)
