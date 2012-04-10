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
from neurounits.visitors import ASTVisitorBase
import itertools





class VisitorFindDirectSymbolDependance(ASTVisitorBase):
    """ Finds symbol dependance on one another, but does
        not recurse over assignments. I.e
        a = b+2
        d = c+a

        Then 'b' will not be reported as a dependancy on 'd'
    """

    
    def __init__(self, ):
        self.dependancies = {}


    def VisitEqnSet(self, o, **kwargs):
        for a in o.assignments:
            self.dependancies[a.lhs] = self.Visit(a)
            
    

    def VisitSymbolicConstant(self, o, **kwargs):
        return []
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

    def VisitAssignedVariable(self, o, **kwargs):
        return [o]
    
    def VisitSuppliedValue(self, o, **kwargs):
        return [o]

    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        raise NotImplementedError()

    def VisitEqnAssignment(self, o, **kwargs):
        return self.Visit(o.rhs)


    def VisitAddOp(self, o, **kwargs):
        return self.Visit(o.lhs) + self.Visit(o.rhs)

    def VisitSubOp(self, o, **kwargs):
        return self.Visit(o.lhs) + self.Visit(o.rhs)

    def VisitMulOp(self, o, **kwargs):
        return self.Visit(o.lhs) + self.Visit(o.rhs)

    def VisitDivOp(self, o, **kwargs):
        return self.Visit(o.lhs) + self.Visit(o.rhs) 

    def VisitExpOp(self, o, **kwargs):
        return self.Visit(o.lhs)

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        return list( itertools.chain( * [ self.Visit(p) for p in o.parameters.values() ] ) ) 

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return self.Visit(o.rhs_ast)


