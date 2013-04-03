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

# from units_backends.default import ParsingBackend

from units_misc import safe_dict_merge


class UnitTermData(object):

    @classmethod
    def _getMultipliers(cls):
        multipliers = (
            ('giga', 'G', lambda backend: backend.Unit(powerTen=9)),
            ('mega', 'M', lambda backend: backend.Unit(powerTen=6)),
            ('kilo', 'k', lambda backend: backend.Unit(powerTen=3)),
            ('centi', 'c', lambda backend: backend.Unit(powerTen=-2)),
            ('milli', 'm', lambda backend: backend.Unit(powerTen=-3)),
            ('micro', 'u', lambda backend: backend.Unit(powerTen=-6)),
            ('nano', 'n', lambda backend: backend.Unit(powerTen=-9)),
            ('pico', 'p', lambda backend: backend.Unit(powerTen=-12)),
            )
        return multipliers

    @classmethod
    def getMultipliers(cls, backend):
        return [(u1, u2, u3(backend=backend)) for (u1, u2, u3) in
                cls._getMultipliers()]

    @classmethod
    def getMultiplierKeys(cls):
        return [(u1, u2) for (u1, u2, u3) in cls._getMultipliers()]

    @classmethod
    def getMultiplierLUTLong(cls, backend):
        return dict([(u[0], u[2](backend=backend)) for u in
                    cls._getMultipliers()])

    @classmethod
    def getMultiplierLUTShort(cls, backend):
        return dict([(u[1], u[2](backend=backend)) for u in
                    cls._getMultipliers()])

    @classmethod
    def getMultiplierLUT(cls, backend):
        return safe_dict_merge(cls.getMultiplierLUTShort(backend=backend),
                               cls.getMultiplierLUTLong(backend=backend))

    @classmethod
    def _getUnits(cls):
        units = (
            ('meter', 'm', lambda backend: backend.Unit(meter=1)),
            ('gram', 'g', lambda backend: backend.Unit(kilogram=1, powerTen=-3)),
            ('second', 's', lambda backend: backend.Unit(second=1)),
            ('amp', 'A', lambda backend: backend.Unit(ampere=1)),
            ('kelvin', 'K', lambda backend: backend.Unit(kelvin=1)),
            ('mole', 'mol', lambda backend: backend.Unit(mole=1)),
            ('candela', 'cd', lambda backend: backend.Unit(candela=1)),
            ('volt', 'V', lambda backend: backend.Unit(meter=2, kilogram=1, second=-3, ampere=-1)),
            ('siemen', 'S', lambda backend: backend.Unit(meter=-2, kilogram=-1, second=3, ampere=2)),
            ('farad', 'F', lambda backend: backend.Unit(meter=-2, kilogram=-1, second=4, ampere=2)),
            ('ohm', 'Ohm', lambda backend: backend.Unit(meter=2, kilogram=1, second=-3, ampere=-2)),
            ('coulomb', 'C', lambda backend: backend.Unit(second=1, ampere=1)),
            ('hertz', 'Hz', lambda backend: backend.Unit(second=-1)),
            ('watt', 'W', lambda backend: backend.Unit(kilogram=1, meter=2, second=-3)),
            ('joule', 'J', lambda backend: backend.Unit(kilogram=1, meter=2, second=-2)),
            ('newton', 'N', lambda backend: backend.Unit(kilogram=1, meter=1, second=-2)),
            ('liter', 'L', lambda backend: backend.Unit(powerTen=-3, meter=3)),
            ('molar', 'M', lambda backend: backend.Unit(mole=1, powerTen=3, meter=-3)),
            )
        return units

    @classmethod
    def getUnits(cls, backend):
        return [(u1, u2, u3(backend=backend)) for (u1, u2, u3) in cls._getUnits()]

    @classmethod
    def getUnitKeys(cls):
        return [(u1, u2) for (u1, u2, u3) in cls._getUnits()]

    @classmethod
    def getUnitLUTLong(cls, backend):
        return dict([(u[0], u[2]) for u in
                    cls.getUnits(backend=backend)])

    @classmethod
    def getUnitLUTShort(cls, backend):
        return dict([(u[1], u[2]) for u in
                    cls.getUnits(backend=backend)])

    @classmethod
    def getUnitLUT(cls, backend):
        return safe_dict_merge(cls.getUnitLUTShort(backend=backend),
                               cls.getUnitLUTLong(backend=backend))

   
