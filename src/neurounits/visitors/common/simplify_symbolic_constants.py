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
from neurounits import ast 
from neurounits.visitors.common.ast_replace_node import ReplaceNode
from neurounits.visitors.bases.base_visitor import ASTVisitorBase



class ReduceConstants(ASTVisitorBase):
    
    def Visit(self, o, **kwargs):
        return o.AcceptVisitor(self, **kwargs)

    def VisitEqnSet(self, o, **kwargs):
        
        
        
        for aKey in o._eqn_assignment.keys():
            a = o._eqn_assignment[aKey]
            fixed_value = self.Visit(a.rhs)
            if fixed_value:
                
                s = ast.SymbolicConstant( symbol=aKey.symbol, value=fixed_value )
                print 'New Symbolic Constant', s, aKey.symbol, s.value
                
                #assert False
                ReplaceNode(a.lhs, s).Visit(o)
                
                o._constants[aKey.symbol] = s
                del o._eqn_assignment[aKey]
            #else:
                
                
        #o._eqn_assignment = new_assignments
                

    def VisitOnEvent(self, o, **kwargs):
        raise NotImplementedError()
    def VisitOnEventStateAssignment(self, o, **kwargs):
        raise NotImplementedError()

    def VisitSymbolicConstant(self, o, **kwargs):
        return o.value

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
        return None

    def VisitParameter(self, o, **kwargs):
        return None

    def VisitConstant(self, o, **kwargs):
        return o.value

    def VisitSuppliedValue(self, o, **kwargs):
        return None

    def VisitAssignedVariable(self, o, **kwargs):
        return self.Visit(o.assignment_rhs)

    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        raise NotImplementedError()

    def VisitEqnAssignment(self, o, **kwargs):
        raise NotImplementedError()



    def VisitAddOp(self, o, **kwargs):
        t1,t2 = self.Visit(o.lhs), self.Visit(o.rhs)
        if t1 is None or t2 is None:
            return None
        return t1+t2
    
    def VisitSubOp(self, o, **kwargs):
        t1,t2 = self.Visit(o.lhs), self.Visit(o.rhs)
        if t1 is None or t2 is None:
            return None
        return t1-t2

    def VisitMulOp(self, o, **kwargs):
        t1,t2 = self.Visit(o.lhs), self.Visit(o.rhs)
        if t1 is None or t2 is None:
            return None
        return t1*t2

    def VisitDivOp(self, o, **kwargs):
        t1,t2 = self.Visit(o.lhs), self.Visit(o.rhs)
        if t1 is None or t2 is None:
            return None
        return t1/t2

    def VisitExpOp(self, o, **kwargs):
        t1 = self.Visit(o.lhs)
        if t1 is None:
            return None
        return t1**o.rhs



    def VisitFunctionDefInstantiation(self, o, **kwargs):
        # Check if the parameters are constant
        for p in o.parameters.values():
            if self.Visit(p.rhs_ast) is None:
                return None
        
        # Not Implmented how to calculate it yet!
        print 'We can evalute function:' , o.function_def.funcname
        print 'BUT THE LOGIC IS MISSING :)'
        return None
        raise NotImplementedError()

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        raise NotImplementedError()
