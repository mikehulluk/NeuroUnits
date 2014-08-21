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

from astobjects import FunctionDefBuiltIn, FunctionDefParameter


class FunctionDefBuiltInSingleArg(FunctionDefBuiltIn):

    def __init__(self, backend, funcname, **kwargs):
        super(FunctionDefBuiltInSingleArg, self).__init__(
                funcname=funcname,
                parameters={'x': FunctionDefParameter(symbol='x' , dimension=backend.Unit())},
                dimension=backend.Unit(), **kwargs)






class FunctionDefBuiltInSin(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInSin, self).__init__(funcname='__sin__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFsin(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: sin()>'

class FunctionDefBuiltInCos(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInCos, self).__init__(funcname='__cos__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFcos(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: cos()>'

class FunctionDefBuiltInTan(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInTan, self).__init__(funcname='__tan__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFtan(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: tan()>'


class FunctionDefBuiltInSinh(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInSinh, self).__init__(funcname='__sinh__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFsinh(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: sinh()>'

class FunctionDefBuiltInCosh(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInCosh, self).__init__(funcname='__cosh__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFcosh(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: cos()>'

class FunctionDefBuiltInTanh(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInTanh, self).__init__(funcname='__tanh__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFtanh(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: tanh()>'



class FunctionDefBuiltInASin(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInASin, self).__init__(funcname='__asin__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFasin(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: asin()>'

class FunctionDefBuiltInACos(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInACos, self).__init__(funcname='__acos__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFacos(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: acos()>'

class FunctionDefBuiltInATan(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInATan, self).__init__(funcname='__atan__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFatan(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: atan()>'




class FunctionDefBuiltInLn(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInLn, self).__init__(funcname='__ln__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFln(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: ln()>'


class FunctionDefBuiltInLog2(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInLog2, self).__init__(funcname='__log2__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFlog2(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: log2()>'


class FunctionDefBuiltInLog10(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInLog10, self).__init__(funcname='__log10__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFlog10(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: log10()>'


class FunctionDefBuiltInExp(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInExp, self).__init__(funcname='__exp__', backend=backend, **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFexp(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: exp()>'



class FunctionDefBuiltInCeil(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInCeil, self).__init__(funcname='__ceil__', backend=backend, **kwargs)

    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFceil(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: ceil()>'

class FunctionDefBuiltInFloor(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInFloor, self).__init__(funcname='__floor__', backend=backend, **kwargs)

    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFfloor(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: floor()>'

class FunctionDefBuiltInFabs(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInFabs, self).__init__(funcname='__fabs__', backend=backend, **kwargs)

    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFfabs(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: fabs()>'

class FunctionDefBuiltInSqrt(FunctionDefBuiltInSingleArg):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInSqrt, self).__init__(funcname='__sqrt__', backend=backend, **kwargs)

    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFsqrt(self, **kwargs)
    def __repr__(self):
        return '<BuiltinFunction: sqrt()>'



class FunctionDefBuiltInMin(FunctionDefBuiltIn):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInMin, self).__init__(
                funcname='__min__',
                parameters={
                    'x': FunctionDefParameter(symbol='x' , dimension=backend.Unit()),
                    'y': FunctionDefParameter(symbol='y' , dimension=backend.Unit())
                    },
                dimension=backend.Unit(), **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFmin(self, **kwargs)

class FunctionDefBuiltInMax(FunctionDefBuiltIn):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInMax, self).__init__(
                funcname='__max__',
                parameters={
                    'x': FunctionDefParameter(symbol='x' , dimension=backend.Unit()),
                    'y': FunctionDefParameter(symbol='y' , dimension=backend.Unit())
                    },
                dimension=backend.Unit(), **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFmax(self, **kwargs)


class FunctionDefBuiltInPow(FunctionDefBuiltIn):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInPow, self).__init__(
                funcname='__pow__',
                parameters={
                    'base': FunctionDefParameter(symbol='base' , dimension=backend.Unit()),
                    'exp': FunctionDefParameter(symbol='exp' , dimension=backend.Unit())
                    },
                dimension=backend.Unit(), **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFpow(self, **kwargs)

class FunctionDefBuiltInAtan2(FunctionDefBuiltIn):
    def __init__(self, backend, **kwargs):
        super(FunctionDefBuiltInAtan2, self).__init__(
                funcname='__atan2__',
                parameters={
                    'x': FunctionDefParameter(symbol='x' , dimension=backend.Unit()),
                    'y': FunctionDefParameter(symbol='y' , dimension=backend.Unit())
                    },
                dimension=backend.Unit(), **kwargs)
    def accept_func_visitor(self, v, **kwargs):
        return v.VisitBIFatan2(self, **kwargs)
