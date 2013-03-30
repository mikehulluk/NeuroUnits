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

from .eqnsetbuilder_symbol_proxy import SymbolProxy

from ..visitors import ASTVisitorBase

class RemoveAllSymbolProxy(ASTVisitorBase):

    def followSymbolProxy(self, node, visited_nodes=None):
        if visited_nodes is None:
            visited_nodes = set()
        if node in visited_nodes:
            assert False, 'Unable to resolve symbol-proxy! %s' \
                % str(visited_nodes)
        visited_nodes.add(node)

        if type(node) == SymbolProxy:
            assert node.is_resolved()
            return self.followSymbolProxy(node.target,visited_nodes=visited_nodes)
        return node

    def VisitEqnSet(self, o, **kwargs):
        for i in itertools.chain( o.timederivatives, o.assignments, o.functiondefs, o.symbolicconstants, o.onevents):
            self.visit(i)


        o._cache_nodes()

    def VisitNineMLComponent(self, o, **kwargs):
        for i in itertools.chain( o.timederivatives, o.assignments, o.functiondefs, o.symbolicconstants, o.onevents, o.transitions):
            self.visit(i)

        o._cache_nodes()


    def VisitLibrary(self, o, **kwargs):
        for i in itertools.chain( o.functiondefs, o.symbolicconstants):
            self.visit(i)


    def VisitStateVariable(self, o, **kwargs):
        pass

    def VisitParameter(self, o, **kwargs):
        pass

    def VisitConstant(self, o, **kwargs):
        pass

    def VisitAssignedVariable(self, o, **kwargs):
        pass

    def VisitSuppliedValue(self, o, **kwargs):
        pass

    def VisitSymbolicConstant(self, o, **kwargs):
        pass


    def VisitOnEventStateAssignment(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)
    def VisitOnEvent(self, o, **kwargs):
        for a in o.actions:
            self.visit(a)
        for p in o.parameters.values():
            self.visit(p)

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs_map = self.followSymbolProxy(o.rhs_map)
        self.visit(o.rhs_map)

    def VisitRegimeDispatchMap(self, o, **kwargs):
        o.rhs_map = dict( [(reg, self.followSymbolProxy(rhs)) for (reg,rhs) in o.rhs_map.items()])
        for rhs in o.rhs_map.values():
            self.visit(rhs) 



    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs_map = self.followSymbolProxy(o.rhs_map)
        self.visit(o.rhs_map)

    def VisitAddOp(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitSubOp(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitMulOp(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitDivOp(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitIfThenElse(self, o, **kwargs):
        o.if_true_ast = self.followSymbolProxy(o.if_true_ast)
        o.if_false_ast = self.followSymbolProxy(o.if_false_ast)
        o.predicate = self.followSymbolProxy(o.predicate)
        self.visit(o.if_true_ast)
        self.visit(o.if_false_ast)
        self.visit(o.predicate)

    def VisitInEquality(self, o, **kwargs):
        o.less_than = self.followSymbolProxy(o.less_than)
        o.greater_than = self.followSymbolProxy(o.greater_than)
        self.visit(o.less_than)
        self.visit(o.greater_than)


    def VisitBoolAnd(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitBoolOr(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.lhs)
        self.visit(o.rhs)

    def VisitBoolNot(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        self.visit(o.lhs)

    def VisitExpOp(self, o, **kwargs):
        o.lhs = self.followSymbolProxy(o.lhs)
        self.visit(o.lhs)

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p)

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        o.rhs_ast = self.followSymbolProxy(o.rhs_ast)
        self.visit(o.rhs_ast)

    def VisitBuiltInFunction(self, o, **kwargs):
        pass

    def VisitFunctionDef(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p)
        o.rhs = self.followSymbolProxy(o.rhs)
        self.visit(o.rhs)

    def VisitFunctionDefParameter(self, o, **kwargs):
        pass


    def VisitOnTransitionTrigger(self, o, **kwargs):
        for a in o.actions:
            self.visit(a)
        self.visit(o.trigger)
    
    def VisitOnTransitionEvent(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p)

    def VisitEmitEvent(self, o, **kwargs):
        o.parameter_map= dict( [(reg, self.followSymbolProxy(rhs)) for (reg,rhs) in o.parameter_map.items()])
        for p in o.parameter_map.values():
            self.visit(p)

    def VisitOnEventDefParameter(self, o, **kwargs):
        pass

