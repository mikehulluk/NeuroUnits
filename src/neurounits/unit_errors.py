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


class UnitError(ValueError):

    pass


class DuplicateKeyError(RuntimeError):

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return 'Duplicate Key Found: %s' % str(self.key)


class ParsingError(RuntimeError):

    pass


class InternalError(RuntimeError):

    pass


def panic():
    raise InternalError()


class UnitMismatchError(ValueError):
    def __init__(self, unitA, unitB, objA=None, objB=None,):
        self.unitA = unitA
        self.unitB = unitB
        self.objA = objA
        self.objB = objB

    def __str__(self):

        objA_name = str(self.objA)
        objB_name = str(self.objB)
        return 'Unit Imcompatibility: (%s) <-> (%s) [%s %s]' % (self.unitA, self.unitB, objA_name, objB_name)


class NeuroUnitParsingError(ValueError):

    pass


class InvalidUnitTermError(ValueError):
    pass

