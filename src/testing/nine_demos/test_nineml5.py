
from neurounits import NeuroUnitParser
from neurounits.writers.writer_ast_to_simulatable_object import EqnSimulator


es = NeuroUnitParser.EqnSet("""
        eqnset van_de_pol {
            x' = mu * (x-(x**3)/3 - y)  * {10ms-1}
            y' = x/mu * {10ms-1}
            #mu = 6.0
         <=> PARAMETER mu
         <=> INITIAL x:0
         <=> INITIAL y:0
        }
        """)

# SimulateEquations(es)

# es.to_redoc().to_pdf(filename="/home/michael/Desktop//out1.pdf")

import numpy as np
evaluator = EqnSimulator(es)

one = es.library_manager.backend.Quantity(1.0,
        es.library_manager.backend.Unit())
six = es.library_manager.backend.Quantity(6.0,
        es.library_manager.backend.Unit())
print 'Simulating'
res = evaluator(time_data=np.linspace(0.0, 0.0200, 1000),
                params={'mu': 4.0}, state0In={'x': 1.0, 'y': six})
print 'Done Simulating'
print res
print res.keys()
# res = evaluator(state0In=(), params=()s.params,time_data=s.t)
import pylab
print res['t'].shape
# print res['m'].shape
# pylab.plot(res['t'], res['m'])
pylab.figure()
pylab.plot(res['x'], res['y'])

pylab.figure()
pylab.plot(res['t'], res['x'])
pylab.plot(res['t'], res['y'])
# pylab.plot(res['t'], res['n'])
pylab.show()

