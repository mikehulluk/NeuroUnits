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



class VisitorFindDirectSymbolDependance(ASTVisitorBase):
    """ Finds symbol dependance on one another, but does
        not recurse over assignments. I.e
        a = b+2
        d = c+a

        Then 'b' will not be reported as a dependancy on 'd'
    """

    @classmethod
    def get_assignment_dependancy_ordering(cls, eqnset):
        from neurounits.ast.astobjects import AssignedVariable
        deps = dict([(ass, VisitorFindDirectSymbolDependance().visit(ass_eqn.rhs)) for (ass, ass_eqn) in eqnset._eqn_assignment.iteritems()])

        ordered = []
        to_order = set(deps.keys())

        while to_order:
            found = False
            for o in to_order:
                o_deps = [d for d in deps[o] if type(d) == AssignedVariable]
                o_deps_unsatisfied = [d for d in o_deps if not d in ordered]
                if len(o_deps_unsatisfied) == 0:
                    ordered.append(o)
                    to_order.remove(o)
                    found = True
                    break
            # Prevent recursion:
            assert found == True, """Can't find the dependencies for: %s"""%",".join( [o.symbol for o in to_order] )

        assert len(ordered) == len(eqnset._eqn_assignment)
        return ordered

    @classmethod
    def get_assignment_dependancy_ordering_recursive(cls, eqnset, ass):
        from neurounits.ast.astobjects import AssignedVariable
        D = VisitorFindDirectSymbolDependance()
        D.visit(eqnset)

        def ass_deps(a):
            return [t for t in D.dependancies[a] if isinstance(t, AssignedVariable)]

        # resolved_deps = set()

        required_deps = set(ass_deps(ass))

        # required_deps = set()

        # Find all the dependancies:
        start_dep_len = None
        while start_dep_len != len(required_deps):
            start_dep_len = len(required_deps)
            to_add = set()
            for i in required_deps:
                for i_dep in ass_deps(i):
                    if not i_dep in required_deps:
                        to_add.add(i_dep)

            required_deps = required_deps | to_add

        op = [o for o in cls.get_assignment_dependancy_ordering(eqnset) if o in required_deps]
        return op

    def __init__(self):
        self.dependancies = {}


    @classmethod
    def build_direct_dependancy_graph(cls, component):
        import neurounits.ast as ast
        dep_find = VisitorFindDirectSymbolDependance()
        dep_find.visit(component)


        # Remap TimeDerivatives into StateVariables:
        #for k,v in dep_find.dependancies:
            



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
            print repr(k), v

        return g



        







    def VisitNineMLComponent(self, o, **kwargs):
        for a in o.assignments:
            self.dependancies[a.lhs] = self.visit(a)

        for a in o.timederivatives:
            self.dependancies[a.lhs] = self.visit(a)

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    def VisitIfThenElse(self, o, **kwargs):
        d1 = self.visit(o.predicate, **kwargs)
        d2 = self.visit(o.if_true_ast, **kwargs)
        d3 = self.visit(o.if_false_ast, **kwargs)
        return d1 + d2 + d3

    def VisitInEquality(self, o, **kwargs):
        d1 = self.visit(o.less_than, **kwargs)
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
    def VisitFunctionDef(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBuiltInFunction(self, o, **kwargs):
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
        symbols = []
        for rhs in o.rhs_map.values():
            symbols.extend(self.visit(rhs, **kwargs))
        return symbols

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

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        return list(itertools.chain(*[self.visit(p) for p in
                    o.parameters.values()]))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return self.visit(o.rhs_ast)

    def VisitAnalogReducePort(self, o, **kwargs):
        return [o] + list(itertools.chain( *[self.visit(a) for a in o.rhses]))


