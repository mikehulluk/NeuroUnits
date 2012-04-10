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
import itertools 
from base_visitor import ASTVisitorBase


class SingleVisitPredicate(object):
    def __init__(self,):
        self.visited = set()
    def __call__(self,n,**kwargs):
        has_not_visited = n not in self.visited
        self.visited.add(n)
        return has_not_visited






class ASTActionerDepthFirst(ASTVisitorBase):


    def __init__(self, action_predicates=None):
        self.action_predicates = action_predicates or [] 


    def VisitEqnSet(self, o, **kwargs):
        subnodes = itertools.chain( o.assignments, o.timederivatives, o.functiondefs, o.constants)
        for f in subnodes:
            self.Visit(f,**kwargs)

        for onev in o.on_events:
            self.Visit(onev,**kwargs)

        self._ActionEqnSet(o,**kwargs)


    def VisitOnEvent(self, o, **kwargs):
        for p in o.parameters.values():
            self.Visit(p,**kwargs)
        for action in o.actions:
            self.Visit(action, **kwargs)
        self._ActionOnEvent(o,**kwargs)

    def VisitOnEventStateAssignment(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionOnEventStateAssignment(o,**kwargs)



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
        for p in o.parameters.values():
            self.Visit(p,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionFunctionDef(o,**kwargs)

    def VisitBuiltInFunction(self, o, **kwargs):
        for p in o.parameters.values():
            self.Visit(p,**kwargs)
        self._ActionBuiltInFunction(o,**kwargs)

    def VisitFunctionDefParameter(self, o, **kwargs):
        self._ActionFunctionDefParameter(o,**kwargs)

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        self._ActionStateVariable(o,**kwargs)
    def VisitSymbolicConstant(self, o, **kwargs):
        self._ActionSymbolicConstant(o,**kwargs)
    def VisitParameter(self, o, **kwargs):
        self._ActionParameter(o,**kwargs)
    def VisitConstant(self, o, **kwargs):
        self._ActionConstant(o,**kwargs)
    def VisitAssignedVariable(self, o, **kwargs):
        self._ActionAssignedVariable(o,**kwargs)
    def VisitSuppliedValue(self, o, **kwargs):
        self._ActionSuppliedValue(o,**kwargs)

    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionEqnTimeDerivative(o,**kwargs)

    def VisitEqnAssignment(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionEqnAssignment(o,**kwargs)

    def VisitAddOp(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionAddOp(o,**kwargs)

    def VisitSubOp(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionSubOp(o,**kwargs)

    def VisitMulOp(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionMulOp(o,**kwargs)

    def VisitDivOp(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self.Visit(o.rhs,**kwargs)
        self._ActionDivOp(o,**kwargs)

    def VisitExpOp(self, o, **kwargs):
        self.Visit(o.lhs,**kwargs)
        self._ActionExpOp(o,**kwargs)

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        for p in o.parameters.values():
            self.Visit(p,**kwargs)
        self.Visit(o.function_def,**kwargs)
        self._ActionFunctionDefInstantiation(o,**kwargs)

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        self.Visit(o.rhs_ast,**kwargs)
        self._ActionFunctionDefInstantiationParater(o,**kwargs)


    def _ActionPredicate(self, o, **kwargs):
        for p in self.action_predicates:
            if not p(o,**kwargs):
                return False
        return True
    


    def _ActionEqnSet(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionEqnSet( o, **kwargs)

    def _ActionIfThenElse(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionIfThenElse( o, **kwargs)
    def _ActionInEquality(self, o ,**kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionInEquality(o ,**kwargs)
    def _ActionBoolAnd(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionBoolAnd(o, **kwargs)
    def _ActionBoolOr(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionBoolOr(o, **kwargs)
    def _ActionBoolNot(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionBoolNot(o, **kwargs)

    # Function Definitions:
    def _ActionFunctionDef(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionFunctionDef(o, **kwargs)
    def _ActionBuiltInFunction(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionBuiltInFunction(o, **kwargs)
    def _ActionFunctionDefParameter(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionFunctionDefParameter(o, **kwargs)

    # Terminals:
    def _ActionStateVariable(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionStateVariable(o, **kwargs)

    def _ActionSymbolicConstant(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionSymbolicConstant(o, **kwargs)

    def _ActionParameter(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionParameter(o, **kwargs)

    def _ActionConstant(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionConstant(o, **kwargs)

    def _ActionAssignedVariable(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionAssignedVariable(o, **kwargs)

    def _ActionSuppliedValue(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionSuppliedValue(o, **kwargs)

    # AST Objects:
    def _ActionEqnTimeDerivative(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionEqnTimeDerivative(o, **kwargs)

    def _ActionEqnAssignment(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionEqnAssignment(o, **kwargs)

    def _ActionAddOp(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionAddOp(o, **kwargs)
    def _ActionSubOp(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionSubOp(o, **kwargs)
    def _ActionMulOp(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionMulOp(o, **kwargs)
    def _ActionDivOp(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionDivOp(o, **kwargs)
    def _ActionExpOp(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionExpOp(o, **kwargs)

    def _ActionFunctionDefInstantiation(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionFunctionDefInstantiation(o, **kwargs)
    def _ActionFunctionDefInstantiationParater(self, o, **kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionFunctionDefInstantiationParater(o, **kwargs)



    def _ActionOnEvent(self, o,**kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionOnEvent(o,**kwargs)
    def _ActionOnEventStateAssignment(self, o,**kwargs):
        if self._ActionPredicate(o,**kwargs):
            return self.ActionOnEventStateAssignment(o,**kwargs)








    def ActionEqnSet(self, o, **kwargs):
        raise NotImplementedError()


    def ActionIfThenElse(self, o, **kwargs):
        raise NotImplementedError()
    def ActionInEquality(self, o ,**kwargs):
        raise NotImplementedError()
    def ActionBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def ActionBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def ActionBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def ActionFunctionDef(self, o, **kwargs):
        raise NotImplementedError()
    def ActionBuiltInFunction(self, o, **kwargs):
        raise NotImplementedError()
    def ActionFunctionDefParameter(self, o, **kwargs):
        raise NotImplementedError()

    # Terminals:
    def ActionStateVariable(self, o, **kwargs):
        raise NotImplementedError()
    def ActionSymbolicConstant(self, o, **kwargs):
        raise NotImplementedError()
    def ActionParameter(self, o, **kwargs):
        raise NotImplementedError()
    def ActionConstant(self, o, **kwargs):
        raise NotImplementedError()
    def ActionAssignedVariable(self, o, **kwargs):
        raise NotImplementedError()
    def ActionSuppliedValue(self, o, **kwargs):
        raise NotImplementedError()

    # AST Objects:
    def ActionEqnTimeDerivative(self, o, **kwargs):
        raise NotImplementedError()
    def ActionEqnAssignment(self, o, **kwargs):
        raise NotImplementedError()

    def ActionAddOp(self, o, **kwargs):
        raise NotImplementedError()
    def ActionSubOp(self, o, **kwargs):
        raise NotImplementedError()
    def ActionMulOp(self, o, **kwargs):
        raise NotImplementedError()
    def ActionDivOp(self, o, **kwargs):
        raise NotImplementedError()
    def ActionExpOp(self, o, **kwargs):
        raise NotImplementedError()

    def ActionFunctionDefInstantiation(self, o, **kwargs):
        raise NotImplementedError()
    def ActionFunctionDefInstantiationParater(self, o, **kwargs):
       raise NotImplementedError()

