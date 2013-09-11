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
import numpy


class ReduceConstants(ASTVisitorBase):


    def _res_assignments_new(self, o, **kwargs):

        removed = []

        for assignment in o.ordered_assignments_by_dependancies:
            fixed_value = self.visit(assignment.rhs_map)

            #print 'Is fixed? :', assignment.lhs.symbol, fixed_value
            if fixed_value is not None:


                removed.extend([assignment, assignment.lhs])

                # Replace the 'Assigned' object with a 'SymbolicConst' in the tree:
                sym_node = ast.SymbolicConstant(symbol=assignment.lhs.symbol, value=fixed_value)
                ReplaceNode.replace_and_check(srcObj=assignment.lhs, dstObj=sym_node, root = o)

                # Remove the Assignment equation:
                o._eqn_assignment._objs.remove(assignment)
                o._symbolicconstants._add_item(sym_node)



        for a in removed:
            #print 'Simplified:', a
            nc = EqnsetVisitorNodeCollector(o)
            assert not a in nc.all(), 'Did not fully remove: %s' % a




    def VisitNineMLComponent(self, o, **kwargs):
        self._res_assignments_new(o, **kwargs)

    def VisitLibrary(self, o, **kwargs):
        self._res_assignments_new(o, **kwargs)
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
    def VisitFunctionDefUser(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
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
    def VisitTimeVariable(self, o, **kwargs):
        return None

    def VisitAnalogReducePort(self, o, **kwargs):
        return None

    def VisitAssignedVariable(self, o, **kwargs):
        return None

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

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        # Check if the parameters are constant
        assert False
        params = {}
        for p in o.parameters.values():
            pres = self.visit(p.rhs_ast)
            if pres is None:
                return None
            params[p] = pres


        # Not Implmented how to calculate it yet!
        print 'We can evalute function:' , o.function_def.funcname
        print 'BUT THE LOGIC IS MISSING :)'
        assert False
        return None
        raise NotImplementedError()

    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        # Check if the parameters are constant
        #self.visit(o.rhs_ast)

        #assert False
        params = {}
        for p in o.parameters.values():
            pres = self.visit(p.rhs_ast)
            if pres is None:
                return None
            params[p] = pres


        if o.function_def.funcname== 'ln':
            from neurounits.units_backends.mh import MMQuantity, MMUnit
            assert len(params) == 1
            p = params.values()[0].float_in_si()
            return MMQuantity( numpy.log(p), MMUnit() )


        if o.function_def.funcname== 'exp':
            from neurounits.units_backends.mh import MMQuantity, MMUnit
            assert len(params) == 1
            p = params.values()[0].float_in_si()
            return MMQuantity( numpy.exp(p), MMUnit() )


        # Not Implmented how to calculate it yet!
        print 'We can evalute function:' , o.function_def.funcname
        print 'BUT THE LOGIC IS MISSING :)'
        #assert False
        return None
        raise NotImplementedError()


    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        raise NotImplementedError()



    def VisitRandomVariable(self, rv, **kwargs):
        # Check that the parameters are all constants for the moment:
        for p in rv.parameters:
            assert self.visit(p) != None, 'Random Variable parameters must all be compile time resolves'


        # Don't reduce random variables:
        return None

    def VisitRandomVariableParameter(self, p):
        return self.visit(p.rhs_ast)

