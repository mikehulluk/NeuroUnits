
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


from .astobjects import ASTObject, ASTExpressionObject


class EqnAssignmentByRegime(ASTObject):
    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnAssignmentByRegime(self, **kwargs)

    def __init__(self,lhs,rhs_map,**kwargs):
        assert isinstance(rhs_map,EqnRegimeDispatchMap)
        self.lhs = lhs
        self.rhs_map = rhs_map


class EqnTimeDerivativeByRegime(ASTObject):
    def accept_visitor(self, v, **kwargs):
        return v.VisitTimeDerivativeByRegime(self, **kwargs)
    def __init__(self,lhs,rhs_map,**kwargs):
        self.lhs = lhs
        assert isinstance(rhs_map,EqnRegimeDispatchMap)
        self.rhs_map = rhs_map


    def set_rhs_map(self, o):
        assert o is not None
        self._rhs_map = o

    def get_rhs_map(self):
        return self._rhs_map
    rhs_map = property(get_rhs_map, set_rhs_map)



class EqnRegimeDispatchMap(ASTExpressionObject):
    def accept_visitor(self, v, **kwargs):
        return v.VisitRegimeDispatchMap(self, **kwargs)

    def __init__(self, rhs_map):
        super(EqnRegimeDispatchMap, self).__init__()
        assert isinstance(rhs_map, dict)
        self.rhs_map = rhs_map

    def set_rhs_map(self, o):
        assert o is not None
        self._rhs_map = o

    def get_rhs_map(self):
        return self._rhs_map
    rhs_map = property(get_rhs_map, set_rhs_map)






class EqnTimeDerivativePerRegime(ASTObject):
    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnTimeDerivativePerRegime(self, **kwargs)

    def __init__(self,lhs,rhs, regime_name, **kwargs):
        self.lhs = lhs
        self.rhs = rhs
        self.regime_name = regime_name

class EqnAssignmentPerRegime(ASTObject):
    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnAssignmentPerRegime(self, **kwargs)

    def __init__(self,lhs,rhs, regime_name, **kwargs):
        self.lhs = lhs
        self.rhs = rhs
        self.regime_name = regime_name
