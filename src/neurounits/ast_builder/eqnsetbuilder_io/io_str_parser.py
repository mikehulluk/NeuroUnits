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

from neurounits.ast_builder.io_types import IOType
from neurounits.units_misc import read_json
from neurounits.errors import ParsingError

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
    # Unpack the line:
    mode, params, metadata = line

    metadata = read_json(metadata)


    if mode not in ('summed_input', 'input', 'output', 'parameter', 'time'):
        raise ParsingError('Unexpected Mode: %s' % mode)


    defs = []
    for (param, dimension) in params:
        io_data = IODataDimensionSpec(symbol=param.strip(), iotype=IOType.LUT[mode], dimension=dimension, metadata=metadata)
        defs.append(io_data)
    return defs





