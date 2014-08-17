import mreorg
from neurounits import NeuroUnitParser

import numpy as np
import pylab









from neurounitscontrib.demo import DemoPluginBase
class Demo7(DemoPluginBase):


    def get_name(self, ):
        return '7'

    def run(self, args):
        test7()








def test7():

    library_manager = NeuroUnitParser.Parse9MLFile("""

        define_component test_random {


                on(t > t_next) {
                    t_next = t +{10ms} # + ~uniform(min=40,max=100)[] * {1ms}
                    emit myspike()
                }

                <=> time t
                initial {
                    t_next = 0ms
                }
                from std.math import pi
                #from std.math import sin
                w = 1/{10ms}
                y1 = std.math.sin(2*pi*w*t)
                y2 = std.math.cos(2*pi*w*t)
                #y3 = std.math.tan(2*pi*w*t)

                #ya1 = std.math.sinh(2*pi*w*t)
                #ya2 = std.math.cosh(2*pi*w*t)
                #ya3 = std.math.tanh(2*pi*w*t)

                yb1 =std.math.sin( std.math.asin(2*pi*w*t) ) 
                yb2 =std.math.cos( std.math.acos(2*pi*w*t) )
                yb3 =std.math.tan( std.math.atan(2*pi*w*t) )
                yb4 =std.math.tan( std.math.atan2(y=2*pi*w*t, x=1) )
                

                s = std.math.sin(w*t)
                yc1 =std.math.sqrt(s)
                yc2 = std.math.ceil(s*3)
                yc3 = std.math.floor(3*s)
                yc4 = std.math.fabs(3*s)

                yd1 =std.math.ln(s)
                yd2 =std.math.log2(s)
                yd3 =std.math.log10(s)
                yd4 = std.math.exp(-t* w )

                ye1 = std.math.max( x=std.math.sin(2*pi*w*t), y=-0.5 )
                ye2 = std.math.min( x=std.math.sin(2*pi*w*t), y=0.5 )

            }
            """)



    res = library_manager.get('test_random').simulate(
        times=np.linspace(0.0, 0.200, 10000),

        )

    res.auto_plot()




if __name__ == '__main__':
    test7()

    pylab.show()

