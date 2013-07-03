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

import re
from neurounits.io_types import IOType
from neurounits.units_misc import read_json


class IOData(object):

    def __init__(self, symbol, iotype, metadata={}):
        self.symbol = symbol
        self.iotype = iotype
        self.metadata = metadata


class IODataDimensionSpec(IOData):

    def __init__(self, symbol, iotype, dimension=None, **kwargs):
        IOData.__init__(self, symbol=symbol, iotype=iotype, **kwargs)
        self.dimension = dimension


class IODataInitialCondition(IOData):
    def __init__(self, symbol, value, **kwargs):
        IOData.__init__(self, symbol=symbol, iotype=IOType.InitialCondition, **kwargs)
        self.value = value


def parse_io_line(line):
    from neurounits import NeuroUnitParser
    from neurounits.unit_errors import ParsingError
    assert isinstance(line, basestring)

    metadata = {}
    if 'METADATA' in line:
        (line, metadata) = line.split('METADATA')
        metadata = read_json(metadata)


    r = re.compile(r"""<=> \s* (?P<MODE>[a-zA-Z][a-zA-Z_]*) \s* (?P<DEFS>.*) $""", re.VERBOSE)
    m = r.match(line)

    if not m:
        raise ParsingError('Unable to parse line: "%s"' % line)
    g = m.groupdict()

    mode = g['MODE']

    if mode in ('INPUT', 'OUTPUT', 'PARAMETER', 'ANALOG_REDUCE_PORT'):
        defs = []

        data = g['DEFS']
        for d in data.split(','):
            pDef = d.split(':')
            if len(pDef) == 1:
                (symbol, dimension_str) = (pDef[0], None)
            elif len(pDef) == 2:
                (symbol, dimension_str) = pDef
            else:
                raise ParsingError("Can't interpret line: %s" % line)

            symbol = symbol.strip()
            dimension_str = (dimension_str.strip() if dimension_str else dimension_str)

            # Allow units to be specified in '{' '}' too. This is hacky and should be better
            # integrated.
            if dimension_str:
                if dimension_str[0] == '{' and dimension_str[-1] == '}':
                    dimension_str = '(' + dimension_str[1:-1] + ')'

            dimension = NeuroUnitParser.Unit(dimension_str) if dimension_str is not None else None
            dimension = dimension.with_no_powerten() if dimension is not None else dimension

            io_data = IODataDimensionSpec(symbol=symbol.strip(),
                    iotype=IOType.LUT[mode], dimension=dimension,
                    metadata=metadata)
            defs.append(io_data)
        return defs

    # REMOVED, now use """initial {a=1, b=1, c=14mV, etc}"""
#    elif mode == 'INITIAL':
#        defs = []
#        data = g['DEFS']
#        for d in data.split(','):
#            pDef = d.split(':')
#
#            ic = IODataInitialCondition(symbol=pDef[0], value=pDef[1])
#            defs.append(ic)
#        return defs
    else:
        raise ParsingError('Unexpected Mode: %s' % mode)


