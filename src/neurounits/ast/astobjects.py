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

        # Sanity check:
        assert isinstance(predicate, ASTBooleanExpression)
        assert predicate._is_allowed_in_ifthenelse()




class ASTBooleanExpression(ASTObject):
    def _is_allowed_in_ifthenelse(self):
        raise NotImplementedError()


class InEquality(ASTBooleanExpression):

    def accept_visitor(self, v, **kwargs):
        return v.VisitInEquality(self, **kwargs)

    def __init__(self, lesser_than, greater_than, **kwargs):
        ASTObject.__init__(self, **kwargs)
        self.lesser_than = lesser_than
        self.greater_than = greater_than

    def _is_allowed_in_ifthenelse(self):
        return True


class OnConditionCrossing(ASTBooleanExpression):
    def __init__(self, crosses_lhs, crosses_rhs, on_rising=True, on_falling=True, **kwargs):
        super(OnConditionCrossing, self).__init__()
        self.crosses_lhs = crosses_lhs
        self.crosses_rhs = crosses_rhs
        self.on_rising = on_rising
        self.on_falling = on_falling

    def accept_visitor(self, v, **kwargs):
        return v.VisitOnConditionCrossing(self, **kwargs)

    def _is_allowed_in_ifthenelse(self):
        return False

    def _summarise_node_short(self):
        return 'crosses'





class BoolAnd(ASTBooleanExpression):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolAnd(self, **kwargs)

    def __init__(self, lhs, rhs, **kwargs):
        super(BoolAnd, self).__init__(**kwargs)
        self.lhs = lhs
        self.rhs = rhs

    def _is_allowed_in_ifthenelse(self):
        return self.lhs._is_allowed_in_ifthenelse() \
            and self.rhs._is_allowed_in_ifthenelse()

class BoolOr(ASTBooleanExpression):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolOr(self, **kwargs)

    def __init__(self, lhs, rhs, **kwargs):
        super(BoolOr, self).__init__(**kwargs)
        self.lhs = lhs
        self.rhs = rhs

    def _is_allowed_in_ifthenelse(self):
        return self.lhs._is_allowed_in_ifthenelse() \
            and self.rhs._is_allowed_in_ifthenelse()

class BoolNot(ASTBooleanExpression):

    def accept_visitor(self, v, **kwargs):
        return v.VisitBoolNot(self, **kwargs)

    def __init__(self, lhs, **kwargs):
        super(BoolNot, self).__init__(**kwargs)
        self.lhs = lhs

    def _is_allowed_in_ifthenelse(self):
        return self.lhs._is_allowed_in_ifthenelse()




# Base class:
# ===============
class ASTSymbolNode(ASTExpressionObject):
    def __init__(self, symbol, **kwargs):
        super(ASTSymbolNode, self).__init__(**kwargs)
        self.symbol = symbol

    def _summarise_node_full(self):
        return "Symbol: '%s'" % self.symbol

    def _summarise_node_short(self, use_latex=False):
        return self.symbol

class ASTConstNode(ASTExpressionObject):
    def __init__(self, value, **kwargs):
        super(ASTConstNode, self).__init__(**kwargs)
        self.value = value
        self.set_dimensionality(value.units.with_no_powerten())

    def _summarise_node_full(self):
        return "Value: '%s'" % self.value

    def _summarise_node_short(self, use_latex=False):
        return self.value









class AssignedVariable(ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitAssignedVariable(self, **kwargs)

    def __init__(self, **kwargs):
        super(AssignedVariable, self).__init__(**kwargs)


class SuppliedValue(ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSuppliedValue(self, **kwargs)

    def __init__(self, **kwargs):
        super(SuppliedValue, self).__init__(**kwargs)


class StateVariable(ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitStateVariable(self, **kwargs)

    def __init__(self, **kwargs):
        super(StateVariable, self).__init__(**kwargs)
        self.initial_value = None

    @property
    def default(self):
        return self.initial_value


class Parameter(ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitParameter(self, **kwargs)

    def __init__(self, **kwargs):
        super(Parameter, self).__init__(**kwargs)


class TimeVariable(ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitTimeVariable(self, **kwargs)

    def __init__(self, **kwargs):
        import neurounits
        s = neurounits.units_backends.mh.MMUnit(second=1)
        super(TimeVariable, self).__init__(dimension=s, **kwargs)




class ConstValue(ASTConstNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitConstant(self, **kwargs)

    def __init__(self, **kwargs):
        super(ConstValue, self).__init__(**kwargs)


class ConstValueZero(ASTExpressionObject):
    def __init__(self, **kwargs):
        super(ConstValueZero, self).__init__(**kwargs)

    def accept_visitor(self, v, **kwargs):
        return v.VisitConstantZero(self, **kwargs)



class SymbolicConstant(ASTConstNode, ASTSymbolNode):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSymbolicConstant(self, **kwargs)

    def __init__(self, **kwargs):
        super(SymbolicConstant, self).__init__(**kwargs)

    def _summarise_node_full(self):
        return '%s %s' % (ASTConstNode._summarise_node_full(self),
                          ASTSymbolNode._summarise_node_full(self))










class FunctionDefBuiltIn(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefBuiltIn(self, **kwargs)

    def __init__(self, funcname, parameters, dimension=None, **kwargs):
        super(FunctionDefBuiltIn, self).__init__(**kwargs)
        self.funcname = funcname
        self.parameters = parameters
        if dimension is not None:
            self.set_dimensionality(dimension)
    def __repr__(self):
        return '<BuiltinFunction: %s>' % self.funcname

    def is_builtin(self):
        return True

    def accept_func_visitor(self, v, **kwargs):
        print "Missing 'accept_func_visitor' for type: %s (%s)" % (type(self), self.funcname)
        assert False






class FunctionDefUser(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefUser(self, **kwargs)

    def __init__(self, funcname, parameters, rhs, **kwargs):
        super(FunctionDefUser, self).__init__(**kwargs)
        self.funcname = funcname
        self.parameters = parameters
        self.rhs = rhs

    def __repr__(self):
        return '<FunctionDefUser: %s>' % self.funcname

    def is_builtin(self):
        return False

class FunctionDefParameter(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefParameter(self, **kwargs)

    def __init__(self, symbol=None, dimension=None, **kwargs):
        super(FunctionDefParameter,self).__init__(**kwargs)
        self.symbol = symbol
        if dimension is not None:
            self.set_dimensionality(dimension)

    def __repr__(self):
        return "<FunctionDefParameter '%s'>" % self.symbol


class FunctionDefUserInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefUserInstantiation(self, **kwargs)

    def __init__(self, parameters, function_def, **kwargs):
        super(FunctionDefUserInstantiation,self).__init__(**kwargs)
        self.function_def = function_def
        self.parameters = parameters
        assert not function_def.is_builtin()

    def __repr__(self):
        #TODO-minor
        return "<FunctionDefUserInstantiation: '%s(%s)'>" % (self.function_def.funcname, "...")


class FunctionDefBuiltInInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefBuiltInInstantiation(self, **kwargs)

    def __init__(self, parameters, function_def, **kwargs):
        super(FunctionDefBuiltInInstantiation,self).__init__(**kwargs)
        self.function_def = function_def
        self.parameters = parameters
        assert function_def.is_builtin()


    def _summarise_node_full(self):
        #TODO-minor
        print "params:", self.parameters
        return '{%s( <id:%s>)}' % (self.function_def.funcname, ','.join( ['%s:%s' % (k, id(v)) for (k,v) in self.parameters.items() ] ) )





class FunctionDefParameterInstantiation(ASTExpressionObject):

    def accept_visitor(self, v, **kwargs):
        return v.VisitFunctionDefInstantiationParameter(self, **kwargs)

    def __init__(self, rhs_ast, symbol, function_def_parameter=None, **kwargs):
        super(FunctionDefParameterInstantiation, self).__init__(**kwargs)
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
        super(BinaryOp, self).__init__(**kwargs)
        self.lhs = lhs
        self.rhs = rhs


class AddOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitAddOp(self, **kwargs)
    def _summarise_node_short(self):
        return '+'
    def _summarise_node_full(self):
        return ''


class SubOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitSubOp(self, **kwargs)
    def _summarise_node_short(self):
        return '-'
    def _summarise_node_full(self):
        return ''


class MulOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitMulOp(self, **kwargs)
    def _summarise_node_short(self):
        return '*'
    def _summarise_node_full(self):
        return ''


class DivOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitDivOp(self, **kwargs)
    def _summarise_node_short(self):
        return '/'
    def _summarise_node_full(self):
        return ''


class ExpOp(BinaryOp):

    def accept_visitor(self, v, **kwargs):
        return v.VisitExpOp(self, **kwargs)


