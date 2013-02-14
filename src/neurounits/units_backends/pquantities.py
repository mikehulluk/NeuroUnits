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

import sys
import quantities as pq

from .bases import ParsingBackendBase




class PQParsingBackend(ParsingBackendBase):
    @classmethod
    def Quantity(cls, magnitude, unit ):
        return magnitude * unit

    @classmethod
    def Unit(cls,  meter=0, kilogram=0, second=0, ampere=0, kelvin=0 , mole=0, candela=0, powerTen =0):

        pTenDict = {    -12:    pq.pico,
                        -9:     pq.nano,
                        -6:     pq.micro,
                        -3:     pq.milli,
                        -2:     pq.centi,
                         0:     pq.dimensionless,
                         3:     pq.kilo,
                         6:     pq.mega,
                         9:     pq.giga,
                         12:    pq.tera, }
        pTen = pTenDict[powerTen]

        types = [
                  (meter,   pq.m),
                  (kilogram,pq.kg),
                  (second,  pq.s),
                  (ampere,  pq.A),
                  (kelvin,  pq.K),
                  (mole,    pq.mole),
                  (candela, pq.candela) ,
                ]
        o = pTen
        for (i, j) in types:
            if i != 0:
                o = o * j ** i
        return o


    @classmethod
    def unit_as_dimensionless(cls, u1):
        assert u1.rescale('')
        return float(u1.rescale('').magnitude)




