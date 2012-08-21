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


class StringWriterVisitor(ASTVisitorBase):

    def VisitEqnSet(self, o, **kwargs):
        print 'AST:'
        print '----'

        for a in o.assignments:
            print self.visit(a)

        for a in o.timederivatives:
            print self.visit(a)

        for a in o.functiondefs:
            print self.visit(a)


    def VisitFunctionDef(self, o, **kwargs):
        return '<FUNCDEF: %s => %s>' % (o.funcname, self.visit(o.rhs))

    def VisitFunctionDefParameter(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)

    def VisitBuiltInFunction(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.funcname)

    def VisitStateVariable(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)

    def VisitParameter(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)

    def VisitConstant(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.value)

    def VisitAssignedVariable(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)

    def VisitSuppliedValue(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)

    def VisitSymbolicConstant(self, o, **kwargs):
        return '<%s: %s %s>' % (o.__class__.__name__, o.symbol, o.value)

    # AST Objects:

    def VisitEqnTimeDerivative(self, o, **kwargs):
        return "%s' = %s" % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitEqnAssignment(self, o, **kwargs):
        return '%s = %s' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitAddOp(self, o, **kwargs):
        return '(%s + %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitSubOp(self, o, **kwargs):
        return '(%s - %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitMulOp(self, o, **kwargs):
        return '(%s * %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitDivOp(self, o, **kwargs):
        return '(%s / %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitExpOp(self, o, **kwargs):
        return '(%s ** %s)' % (self.visit(o.lhs), o.rhs)

    def VisitBoolAnd(self, o, **kwargs):
        return '(%s && %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitBoolOr(self, o, **kwargs):
        return '(%s || %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitBoolNot(self, o, **kwargs):
        return '(! %s)'%( self.visit(o.lhs) )


    def VisitFunctionDefInstantiation(self, o, **kwargs):
        p = [self.visit(p) for p in o.parameters.values()]
        return '<%s: %s(%s)>' % (o.__class__.__name__,
                                 o.function_def.funcname, ','.join(p))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return '<%s: %s>' % (o.__class__.__name__, o.symbol)


    def VisitIfThenElse(self, o, **kwargs):
        return "[%s] if [%s] else [%s]" % (self.visit(o.if_true_ast),
                                           self.visit(o.predicate),
                                           self.visit(o.if_false_ast) )
    def VisitInEquality(self, o, **kwargs):
        return "[%s < %s]" % (self.visit(o.less_than),self.visit(o.greater_than) )

