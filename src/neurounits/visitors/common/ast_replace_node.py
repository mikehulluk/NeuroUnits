#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
from neurounits.visitors.bases.base_visitor import ASTVisitorBase

import itertools

class ReplaceNode(ASTVisitorBase):
    
    def __init__(self, srcObj, dstObj):
        self.srcObj = srcObj
        self.dstObj = dstObj
        
        
    def replace_or_visit(self, o):
        if o == self.srcObj:
            return self.dstObj
        else:
            return self.Visit(o)
        
        
    def Visit(self, o, **kwargs):
        return o.AcceptVisitor(self, **kwargs)

    def VisitEqnSet(self, o, **kwargs):
        subnodes = itertools.chain( o.assignments, o.timederivatives, o.functiondefs, o.on_events)
        for f in subnodes:
            self.Visit(f,**kwargs)
        return o

    def VisitOnEvent(self, o, **kwargs):
        raise NotImplementedError()
    def VisitOnEventStateAssignment(self, o, **kwargs):
        raise NotImplementedError()

    def VisitSymbolicConstant(self, o, **kwargs):
        return o

    def VisitIfThenElse(self, o, **kwargs):
        raise NotImplementedError()

    def VisitInEquality(self, o ,**kwargs):
        raise NotImplementedError()
    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        pNew = {}
        for pName,p in o.parameters.iteritems():
            pNew[pName] = self.replace_or_visit(p,**kwargs)
        o.parameters = pNew
        o.rhs = self.replace_or_visit(o.rhs)
        return o        
    
    def VisitBuiltInFunction(self, o, **kwargs):
        return o
    
    
    def VisitFunctionDefParameter(self, o, **kwargs):
        return o

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return o
    def VisitParameter(self, o, **kwargs):
        return o
    def VisitConstant(self, o, **kwargs):
        return o
    def VisitAssignedVariable(self, o, **kwargs):
        return o
    def VisitSuppliedValue(self, o, **kwargs):
        return o

    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitEqnAssignment(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitAddOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitSubOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitMulOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitDivOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitExpOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        return o

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        pNew = {}
        for pName,p in o.parameters.iteritems():
            pNew[pName] = self.replace_or_visit(p,**kwargs)
        o.parameters = pNew
        o.function_def = self.replace_or_visit(o.function_def)
        return o

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return o

