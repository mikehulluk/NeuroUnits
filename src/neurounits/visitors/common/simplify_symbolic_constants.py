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

from neurounits import ast
from neurounits.visitors.common.ast_replace_node import ReplaceNode
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector


class ReduceConstants(ASTVisitorBase):

    def visit(self, o, **kwargs):
        return o.accept_visitor(self, **kwargs)

    def _res_assignments(self, o, **kwargs):
        removed = []
        for aKey in o._eqn_assignment.keys():
            a = o._eqn_assignment[aKey]
            alhs = a.lhs
            fixed_value = self.visit(a.rhs_map)
            if fixed_value:

                sym_suffix = '_as_symconst'
                sym_suffix = ''
                s = ast.SymbolicConstant(symbol=aKey.symbol
                        + sym_suffix, value=fixed_value)

                #ReplaceNode(a.lhs, s).visit(o)
                ReplaceNode.replace_and_check(srcObj=a.lhs, dstObj=s, root = o)



                o._symbolicconstants[aKey.symbol] = s

                from neurounits.misc import SeqUtils
                old_ass = SeqUtils.filter_expect_single( o._eqn_assignment, lambda o:o.symbol == aKey.symbol )
                del o._eqn_assignment[ old_ass ] #o.get_terminal_obj(aKey.symbol) ]

                #del o._eqn_assignment[ o.get_terminal_obj(aKey.symbol) ]

                removed.append(alhs)

        # Double check they have gone:
        for a in removed:
            nc = EqnsetVisitorNodeCollector()
            nc.visit(o)
            assert not a in nc.all()



    def _res_assignments_new(self, o, **kwargs):

        removed = []

        for assignment in list(o.assignments):
            fixed_value = self.visit(assignment.rhs_map)
            if fixed_value:


                removed.extend([assignment, assignment.lhs])

                # Replace the 'Assigned' object with a 'SymbolicConst' in the tree:
                sym_node = ast.SymbolicConstant(symbol=assignment.lhs.symbol, value=fixed_value)
                #ReplaceNode(assignment.lhs, sym_node).visit(o)
                ReplaceNode.replace_and_check(srcObj=assignment.lhs, dstObj=sym_node, root = o)

                # Remove the Assignment equation:
                o._eqn_assignment._objs.remove(assignment)
                o._symbolicconstants._add_item(sym_node)

                

        for a in removed:
            nc = EqnsetVisitorNodeCollector(o)
            assert not a in nc.all(), 'Did not fully remove: %s' % a




    def VisitNineMLComponent(self, o, **kwargs):
        self._res_assignments_new(o, **kwargs)

    def VisitEqnSet(self, o, **kwargs):
        self._res_assignments(o, **kwargs)

    def VisitLibrary(self, o, **kwargs):
        self._res_assignments(o, **kwargs)
        assert len(o._eqn_assignment) == 0

    def VisitOnEvent(self, o, **kwargs):
        raise NotImplementedError()

    def VisitOnEventStateAssignment(self, o, **kwargs):
        raise NotImplementedError()

    def VisitSymbolicConstant(self, o, **kwargs):
        return o.value

    def VisitIfThenElse(self, o, **kwargs):
        # Optimisation's possible here
        return None
        raise NotImplementedError()

    def VisitInEquality(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBuiltInFunction(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefParameter(self, o, **kwargs):
        raise NotImplementedError()

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return None

    def VisitParameter(self, o, **kwargs):
        return None

    def VisitConstant(self, o, **kwargs):
        return o.value

    def VisitSuppliedValue(self, o, **kwargs):
        return None

    def VisitAnalogReducePort(self, o, **kwargs):
        return None

    def VisitAssignedVariable(self, o, **kwargs):
        return None
        assert False, 'Deprecated'
        return self.visit(o.assignment_rhs)

    def VisitRegimeDispatchMap(self, o, **kwargs):
        if len(o.rhs_map) == 1:
            return self.visit(o.rhs_map.values()[0])
        return None

    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        raise NotImplementedError()

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        raise NotImplementedError()

    def VisitAddOp(self, o, **kwargs):
        (t1, t2) = (self.visit(o.lhs), self.visit(o.rhs))
        if t1 is None or t2 is None:
            return None
        return t1 + t2

    def VisitSubOp(self, o, **kwargs):
        (t1, t2) = (self.visit(o.lhs), self.visit(o.rhs))
        if t1 is None or t2 is None:
            return None
        return t1 - t2

    def VisitMulOp(self, o, **kwargs):
        (t1, t2) = (self.visit(o.lhs), self.visit(o.rhs))
        if t1 is None or t2 is None:
            return None
        return t1 * t2

    def VisitDivOp(self, o, **kwargs):
        (t1, t2) = (self.visit(o.lhs), self.visit(o.rhs))
        if t1 is None or t2 is None:
            return None
        return t1 / t2

    def VisitExpOp(self, o, **kwargs):
        t1 = self.visit(o.lhs)
        if t1 is None:
            return None
        return t1 ** o.rhs

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        # Check if the parameters are constant
        params = {}
        for p in o.parameters.values():
            pres = self.visit(p.rhs_ast)
            if pres is None:
                return None
            params[p] = pres


        # Not Implmented how to calculate it yet!
        print 'We can evalute function:' , o.function_def.funcname
        print 'BUT THE LOGIC IS MISSING :)'
        #assert False
        return None
        raise NotImplementedError()

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        raise NotImplementedError()


