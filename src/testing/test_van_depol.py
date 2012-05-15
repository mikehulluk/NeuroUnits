

from neurounits import NeuroUnitParser
import quantities as pq
from neurounits.writers.writer_ast_to_simulatable_object import SimulateEquations, EqnSimulator


es = NeuroUnitParser.EqnSet("""
        EQNSET van_de_pol {
        a = 1um
        m' = -m/{100ms}
        
        n = m +{1}
        
        }
        """, backend=neurounits.)

#SimulateEquations(es)

import numpy as np
evaluator = EqnSimulator(es, )

res = evaluator(time_data = np.linspace(0,100, 1000), params=(), state0In={'m':1 * pq.dimensionless} )
print res
#res = evaluator(state0In=(), params=()s.params,time_data=s.t)

