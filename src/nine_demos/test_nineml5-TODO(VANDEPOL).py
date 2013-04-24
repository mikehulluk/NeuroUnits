
from neurounits import NeuroUnitParser
from neurounits.writers.writer_ast_to_simulatable_object import EqnSimulator
import numpy as np
import pylab

library_manager = NeuroUnitParser.Parse9MLFile("""
    define_component van_de_pol {
            x' = mu * (x-(x*x*x)/3 - y)  * {10ms-1}
            #x' = mu * (x-(x**3)/3 - y)  * {10ms-1}
            
            y' = x/mu * {10ms-1}
            #mu = 6.0
            
            initial {
                x=1.0
                y=6.0
            }
         <=> PARAMETER mu
         <=> INITIAL x:0
         <=> INITIAL y:0
        }
        """)

# SimulateEquations(es)

# es.to_redoc().to_pdf(filename="/home/michael/Desktop//out1.pdf")

res = library_manager.get('van_de_pol').simulate(
    times=np.linspace(0.0, 0.0200, 10000),
    parameters={'mu': "4.0"}
    )

res.auto_plot()
pylab.show()

