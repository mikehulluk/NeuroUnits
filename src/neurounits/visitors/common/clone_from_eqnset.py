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

from neurounits import ast 
from neurounits.unit_errors import panic


class CloneObject(object):
    
    @classmethod
    def SymbolicConstant(cls, srcObj, dst_symbol=None):
        dst_symbol = dst_symbol or srcObj.symbol
        return ast.SymbolicConstant(symbol=dst_symbol, value=srcObj.value)

    @classmethod        
    def BuiltinFunction(cls, srcObj, dst_symbol=None ):
        return srcObj        
        
        
        
    @classmethod        
    def FunctionDef(cls, srcObj, dst_symbol=None ):
        #dst_symbol = dst_symbol or srcObj.funcname
        fNew = _CloneFuncDef().Visit(srcObj)
        
        print fNew
        #assert False
        if dst_symbol:
            fNew.funcname = dst_symbol 
        
        assert isinstance(fNew, ast.FunctionDef)
        return fNew
        
        #new_obj =     









class _CloneFuncDef(ASTVisitorBase):   


    def __init__(self, ):
        self.func_param_map = {}

    def VisitEqnSet(self, o, **kwargs):
        panic()

    def VisitOnEvent(self, o, **kwargs):
        panic()
        
    def VisitOnEventStateAssignment(self, o, **kwargs):
        panic()
            # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        panic()

    def VisitEqnAssignment(self, o, **kwargs):
        panic()
    def VisitStateVariable(self, o, **kwargs):
        panic()

    def VisitParameter(self, o, **kwargs):
        panic()
    # Function Definitions:

    def VisitAssignedVariable(self, o, **kwargs):
        panic()
    def VisitSuppliedValue(self, o, **kwargs):
        panic()


    def VisitFunctionDef(self, o, **kwargs):
        params = {}
        for pName,pObj in o.parameters.iteritems():
             p = ast.FunctionDefParameter(symbol=pObj.symbol)
             params[pName] = p
             self.func_param_map[pObj] = p 
        fDef = ast.FunctionDef(funcname=o.funcname, parameters=params, rhs=self.Visit(o.rhs))
        return fDef

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


    
    def VisitAddOp(self, o, **kwargs):
        return ast.AddOp(self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitSubOp(self, o, **kwargs):
        return ast.SubOp(self.Visit(o.lhs), self.Visit(o.rhs) )
    
    def VisitMulOp(self, o, **kwargs):
        return ast.MulOp(self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitDivOp(self, o, **kwargs):
        return ast.DivOp(self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitExpOp(self, o, **kwargs):
        return ast.ExpOp(self.Visit(o.lhs), o.rhs )

    
    def VisitBuiltInFunction(self, o, **kwargs):
        return o
    def VisitFunctionDefParameter(self, o, **kwargs):
        return self.func_param_map[o]
    
    def VisitSymbolicConstant(self, o, **kwargs):
        return ast.SymbolicConstant( symbol=o.symbol, value=o.value)
    
    def VisitConstant(self, o, **kwargs):
        return ast.ConstValue(value=o.value)

    

        


    def VisitFunctionDefInstantiation(self, o, **kwargs):
        
        # Clone the defintion:
        newDef = self.Visit( o.function_def)
        
        params = {}
        for pName,pObj in o.parameters.iteritems():
            p = ast.FunctionDefParameterInstantiation(rhs_ast=self.Visit(pObj.rhs_ast), symbol=pObj.symbol )
            p.set_function_def_parameter( newDef.parameters[pName]  )
            params[pName] = p
            self.func_param_map[pObj] = p 
        
        return ast.FunctionDefInstantiation(parameters=params, function_def=newDef)


    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        panic() 
