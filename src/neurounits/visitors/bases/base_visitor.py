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


class ASTVisitorBase(object):


    def visit(self, o, **kwargs):
        return o.accept_visitor(self, **kwargs)

    def VisitEqnSet(self, o, **kwargs):
        raise NotImplementedError()
    def VisitNineMLComponent(self, o, **kwargs):
        raise NotImplementedError()

    def VisitOnEvent(self, o, **kwargs):
        raise NotImplementedError()
    def VisitOnEventStateAssignment(self, o, **kwargs):
        raise NotImplementedError()

    def VisitSymbolicConstant(self, o, **kwargs):
        raise NotImplementedError()

    def VisitIfThenElse(self, o, **kwargs):
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
        raise NotImplementedError()

    def VisitParameter(self, o, **kwargs):
        raise NotImplementedError()

    def VisitConstant(self, o, **kwargs):
        raise NotImplementedError()

    def VisitAssignedVariable(self, o, **kwargs):
        raise NotImplementedError()
    def VisitSuppliedValue(self, o, **kwargs):
        raise NotImplementedError()

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        raise NotImplementedError()

    def VisitRegimeDispatchMap(self, o, **kwargs):
        raise NotImplementedError()

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        raise NotImplementedError()


    def VisitAddOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitSubOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitMulOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitDivOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitExpOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        raise NotImplementedError()


