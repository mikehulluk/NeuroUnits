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

from .base import ASTObject


class ASTExpressionObject(ASTObject):

    def __init__(self, dimension=None):
        ASTObject.__init__(self)

        self._dimension = None

        if dimension:
            self.set_dimensionality(dimension)

    def is_dimension_known(self):
        return self.is_dimensionality_known()

    def get_dimension(self):
        return self.get_dimensionality()

    def set_dimension(self, dimension):
        return self.set_dimensionality(dimension)

    def is_dimensionality_known(self):
        return self._dimension is not None

    def get_dimensionality(self):
        assert self.is_dimensionality_known()
        return self._dimension

    def set_dimensionality(self, dimension):

        import neurounits
        assert isinstance(dimension, neurounits.units_backends.mh.MMUnit)

        assert not self.is_dimensionality_known()
        dimension = dimension.with_no_powerten()
        assert dimension.powerTen == 0
        self._dimension = dimension


class IfThenElse(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitIfThenElse(self, **kwargs)

    def __init__(self, predicate, if_true_ast, if_false_ast,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.predicate = predicate
        self.if_true_ast = if_true_ast
        self.if_false_ast = if_false_ast



class InEquality(ASTObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitInEquality(self, **kwargs)

    def __init__(self, less_than, greater_than, **kwargs):
        ASTObject.__init__(self, **kwargs)
        self.less_than = less_than
        self.greater_than = greater_than


class BoolAnd(ASTObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolAnd(self, **kwargs)

    def __init__(self, lhs, rhs, **kwargs):
        self.lhs = lhs
        self.rhs = rhs


class BoolOr(ASTObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolOr(self, **kwargs)

    def __init__(self, lhs, rhs, **kwargs):
        self.lhs = lhs
        self.rhs = rhs


class BoolNot(ASTObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolNot(self, **kwargs)

    def __init__(self, lhs, **kwargs):
        self.lhs = lhs


class AssignedVariable(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitAssignedVariable(self, **kwargs)

    def __init__(self, symbol, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol

    def __repr__(self):
        return "<AssignedVariable: '%s'>" % self.symbol


class SuppliedValue(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSuppliedValue(self, **kwargs)

    def __init__(self, symbol, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol

    def __repr__(self):
        return "<SuppliedValue: '%s'>" % self.symbol


class StateVariable(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitStateVariable(self, **kwargs)

    def __init__(self, symbol, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol
        self.initial_value = None

    def __repr__(self):
        return "<StateVariable: '%s'>" % self.symbol

    @property
    def default(self):
        return self.initial_value


class Parameter(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitParameter(self, **kwargs)

    def __init__(self, symbol, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol

    def __repr__(self):
        return "<Parameter: '%s'>" % self.symbol


class ConstValue(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitConstant(self, **kwargs)

    def __init__(self, value, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.value = value

        self.set_dimensionality(value.units.with_no_powerten())

    def __repr__(self):
        return "<Const: '%s'>" % self.value


class ConstValueZero(ASTExpressionObject):
    def __init__(self, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)

    def accept_visitor(self, v, **kwargs):
        return v.VisitConstantZero(self, **kwargs)





class SymbolicConstant(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSymbolicConstant(self, **kwargs)

    def __init__(self, symbol, value, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol
        self.value = value
        self.set_dimensionality(value.units.with_no_powerten())

    def __repr__(self):
        return '<SymbolicConstant: %s = %s>' % (self.symbol, self.value)





class FunctionDefBuiltIn(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefBuiltIn(self, **kwargs)

    def __init__(self, funcname, parameters, dimension=None, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.funcname = funcname
        self.parameters = parameters
        if dimension is not None:
            self.set_dimensionality(dimension)
    def __repr__(self,):
        return '<BuiltinFunction: %s>' % (self.funcname)

    def is_builtin(self):
        return True


class FunctionDefUser(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefUser(self, **kwargs)

    def __init__(self, funcname, parameters, rhs, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.funcname = funcname
        self.parameters = parameters
        self.rhs = rhs
    
    def __repr__(self,):
        return '<FunctionDefUser: %s>' % (self.funcname)

    def is_builtin(self):
        return False

class FunctionDefParameter(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefParameter(self, **kwargs)

    def __init__(self, symbol=None, dimension=None, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol
        if dimension is not None:
            self.set_dimensionality(dimension)

    def __repr__(self):
        return "<FunctionDefParameter '%s'>" % self.symbol


class FunctionDefUserInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefUserInstantiation(self, **kwargs)

    def __init__(self, parameters, function_def, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.function_def = function_def
        self.parameters = parameters
        assert not function_def.is_builtin()

    def __repr__(self):
        return "<FunctionDefUserInstantiation: '%s(%s)'>" % (self.function_def.funcname, "...")


class FunctionDefBuiltInInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefBuiltInInstantiation(self, **kwargs)

    def __init__(self, parameters, function_def, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.function_def = function_def
        self.parameters = parameters
        assert function_def.is_builtin()

    def __repr__(self):
        return "<FunctionDefBuiltInInstantiation: '%s(%s)'>" % (self.function_def.funcname, "...")




class FunctionDefParameterInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefInstantiationParater(self, **kwargs)

    def __init__(self, rhs_ast, symbol, function_def_parameter=None, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol = symbol
        self.rhs_ast = rhs_ast
        self._function_def_parameter = function_def_parameter

    def set_function_def_parameter(self, param):
        assert self._function_def_parameter is None
        self._function_def_parameter = param

    def get_function_def_parameter(self):
        assert self._function_def_parameter is not None
        return self._function_def_parameter

    def __repr__(self):
        return '<FunctionDefParameterInstantiation: %s >' % self.symbol


class BinaryOp(ASTExpressionObject):

    def __init__(self, lhs, rhs, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.lhs = lhs
        self.rhs = rhs


class AddOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitAddOp(self, **kwargs)
    def __repr__(self, ):
        return '+'


class SubOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSubOp(self, **kwargs)
    def __repr__(self, ):
        return '-'


class MulOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitMulOp(self, **kwargs)
    def __repr__(self, ):
        return '*'


class DivOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitDivOp(self, **kwargs)
    def __repr__(self, ):
        return '/'


class ExpOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitExpOp(self, **kwargs)


