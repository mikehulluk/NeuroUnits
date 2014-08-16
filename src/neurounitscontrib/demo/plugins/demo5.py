import mreorg
from neurounits import NeuroUnitParser
#from neurounits.writers.writer_ast_to_simulatable_object import EqnSimulator
import numpy as np
import pylab









from neurounitscontrib.demo import DemoPluginBase
class Demo5(DemoPluginBase):
    
    
    def get_name(self, ):
        return '5'
                
    def run(self, args):
        test5()
        







def test5():

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
             <=> parameter mu
            }
            """)



    res = library_manager.get('van_de_pol').simulate(
        times=np.linspace(0.0, 0.0200, 10000),
        parameters={'mu': "4.0"}
        )

    res.auto_plot()




if __name__ == '__main__':
    test5()
    
    pylab.show()

