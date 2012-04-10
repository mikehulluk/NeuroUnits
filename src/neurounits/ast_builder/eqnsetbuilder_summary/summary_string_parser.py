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
from neurounits.units_misc import read_json
from neurounits.units_wrapper import NeuroUnitParser

import numpy as np

class SummaryPlotData(object):
    def __init__(self, x, y, t_start, t_end, dt, params, y0, backend):
        self.x = x
        self.y = y
        
        self.t_start = NeuroUnitParser.QuantityExpr( t_start )
        self.t_end = NeuroUnitParser.QuantityExpr(t_end)
        self.dt = NeuroUnitParser.QuantityExpr(dt)
        
        
        #from neurounits.units_backends.default import ParsingBackend
        ParsingBackend = backend
        tSecStart = (self.t_start / ParsingBackend.Quantity(1.0, ParsingBackend.Unit(second=1) )).dimensionless()
        tSecEnd   = (self.t_end / ParsingBackend.Quantity(1.0, ParsingBackend.Unit(second=1) )).dimensionless()
        tSecDt    = (self.dt / ParsingBackend.Quantity(1.0, ParsingBackend.Unit(second=1) )).dimensionless()
        
        self.t = np.arange(tSecStart,tSecEnd,tSecDt)
        
        
        
        self.params = {}
        for k,v in params.iteritems():
            self.params[k] = NeuroUnitParser.Expr(v)
            
        self.y0 = {}
        for k,v in y0.iteritems():
            self.y0[k] = NeuroUnitParser.Expr(v)
        
        




def parse_string(s):
    
    # Trim the start:
    s = s[19:]
    
    print "parsing string", s
    
    kw = read_json(s)
    
    
    #return SummaryPlotData( x=d['x'], y=d['y'], t_start=d['t_start'],t_end=d['t_end'], params=d['params'])
    return SummaryPlotData( **kw)
    
    #print data
    #assert False
