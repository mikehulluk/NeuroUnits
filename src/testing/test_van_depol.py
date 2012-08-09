#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------


from neurounits import NeuroUnitParser
import quantities as pq
from neurounits.writers.writer_ast_to_simulatable_object import EqnSimulator


es = NeuroUnitParser.EqnSet("""
        EQNSET van_de_pol {
            x' = mu * (x-(x**3)/3 - y)  * {10ms-1}
            y' = x/mu * {10ms-1}
            #mu = 6.0
         <=> PARAMETER mu
         <=> INITIAL x:0
         <=> INITIAL y:0
        }
        """)

#SimulateEquations(es)

#es.to_redoc().to_pdf(filename="/home/michael/Desktop//out1.pdf")

import numpy as np
evaluator = EqnSimulator(es, )


one = es.library_manager.backend.Quantity( 1.0, es.library_manager.backend.Unit() )
six = es.library_manager.backend.Quantity( 6.0, es.library_manager.backend.Unit() )
print 'Simulating'
res = evaluator(time_data = np.linspace(0.0,0.0200, 1000), params={'mu':4.0}, state0In={'x':1.0, 'y':six} )
print 'Done Simulating'
print res
print res.keys()
#res = evaluator(state0In=(), params=()s.params,time_data=s.t)
import pylab
print res['t'].shape
#print res['m'].shape
#pylab.plot(res['t'], res['m'])
pylab.figure()
pylab.plot(res['x'], res['y'])

pylab.figure()
pylab.plot(res['t'], res['x'])
pylab.plot(res['t'], res['y'])
#pylab.plot(res['t'], res['n'])
pylab.show()
