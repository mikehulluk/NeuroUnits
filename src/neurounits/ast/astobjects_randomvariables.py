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

from .astobjects import ASTExpressionObject
from neurounits.units_misc import LookUpDict
from neurounits.units_backends.mh import MMUnit

from neurounits.errors import InvalidParametersError


class RandomVariable(ASTExpressionObject):

    def __init__(self, parameters, modes):
        super(RandomVariable, self).__init__()

        self.functionname = self.Meta._name
        self.parameters = LookUpDict(parameters)
        self.modes = modes

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality(MMUnit())

        # Check that the parameter-names match the expected names:
        p_found = set([p.name for p in parameters])
        p_expected = set(self.Meta.expected_parameters)
        if p_found != p_expected:
            msg = '[Expected: %s, Found:%s]' %(p_expected, p_found)
            raise InvalidParametersError('For RandomVariable: %s %s'%(self.functionname, msg)  )

    def accept_visitor(self, v, XX_mhchecked=False, **kwargs):
        return v.VisitRandomVariable(self, **kwargs)


class RandomVariableParameter(ASTExpressionObject):

    def __init__(self, name, rhs_ast):
        super(RandomVariableParameter, self).__init__()
        self.name = name
        self.rhs_ast = rhs_ast

        # Assume that the parameters and random variables are dimensionless
        self.set_dimensionality(MMUnit())

    def accept_visitor(self, v, **kwargs):
        return v.VisitRandomVariableParameter(self, **kwargs)


class AutoRegressiveModel(ASTExpressionObject):

    def __init__(self, coefficients):
        super(AutoRegressiveModel, self).__init__()
        self.coefficients = coefficients

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality(MMUnit())

    def accept_visitor(self, v, **kwargs):
        return v.VisitAutoRegressiveModel(self, **kwargs)


