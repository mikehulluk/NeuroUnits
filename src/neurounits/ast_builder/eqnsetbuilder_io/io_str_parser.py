#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
#import json
import re
from neurounits.io_types import IOType
from neurounits.units_misc import read_json

class IOData(object):
    def __init__(self, symbol, iotype, dimension=None, metadata={}):
        self.symbol = symbol
        self.iotype = iotype
        self.dimension = dimension
        self.metadata = metadata
        

def parse_io_line(line):
    from neurounits import NeuroUnitParser
    from neurounits.unit_errors import ParsingError

    metadata = {}
    if 'METADATA' in line:
        line, metadata = line.split('METADATA')
        metadata = read_json(metadata)


    #r = re.compile( r"""<=> \s* (?P<MODE>[a-zA-Z]+) \s* (?P<SYMBOL>[a-zA-Z][a-zA-Z0-9_]*) \s* ([:] \s* (?P<UNIT>[a-zA-Z0-9/()]*) )? """, re.VERBOSE)
    r = re.compile( r"""<=> \s* (?P<MODE>[a-zA-Z]+) \s* (?P<DEFS>.*) $""", re.VERBOSE)
    m = r.match(line)

    if not m:
        raise ParsingError('Unable to parse line: "%s"'%line)
    g = m.groupdict()

    mode = g['MODE']
    if not mode in ("INPUT","OUTPUT","PARAMETER"):
        raise ParsingError("Unexpected Mode: %s"%mode)


    defs = []

    data = g['DEFS']
    for d in data.split(","):
        pDef = d.split(":")
        if len(pDef) == 1:
            symbol,dimension_str=pDef[0], None
        elif len(pDef) == 2:
            symbol,dimension_str=pDef
        else:
            raise ParsingError("Can't interpret line: %s"%line)

        symbol=symbol.strip()
        dimension_str=dimension_str.strip()if dimension_str else dimension_str

        print 'Parsing: Symbol: "%s" Unit:"%s"'%(symbol, dimension_str)
        print
        dimension = NeuroUnitParser.Unit(dimension_str) if dimension_str is not None else None
        dimension = dimension.with_no_powerten() if dimension is not None else dimension

        io_data =  IOData(  symbol = symbol.strip(), iotype = IOType.LUT[mode], dimension = dimension, metadata = metadata)
        defs.append(io_data)
    return defs

#    print 'U:', u
#    u = NeuroUnitParser.Unit(u) if u is not None else None
#    
#    return IOData(  symbol = g.get('SYMBOL'), 
#                    iotype = IOType.LUT[g.get('MODE')],
#                    unit = u,
#                    metadata = metadata
#                    )
