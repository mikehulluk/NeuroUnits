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


import mreorg
from neurounits import NeuroUnitParser

import numpy as np
import pylab









from neurounitscontrib.demo import DemoPluginBase
class Demo7(DemoPluginBase):


    def get_name(self):
        return '7'

    def run(self, args):
        test7()








def test7():

    library_manager = NeuroUnitParser.Parse9MLFile("""

        define_component test_random {

                from std.math import max

                on(t > t_next1) {
                    t_next1 = t +  ~uniform(min=4,max=10)[] * {1ms}
                    emit myspike()
                }

                on(t > t_next2) {
                    t_next2 = t +  max(x=~normal(loc=10,scale=3)[], y=0) * {1ms}
                    emit myspike()
                }
                #on(t > t_next3) {
                #    t_next3 = t +  max(x=~poisson(lod=10,scale=3)[], y=0) * {1ms}
                #    emit myspike()
                #}


                <=> time t
                initial {
                    t_next1 = 0ms
                    t_next2 = 0ms

                }


                #from std.math import pi
                ##from std.math import sin
                #w = 1/{10ms}
                #y1 = std.math.sin(2*pi*w*t)
                #y2 = std.math.cos(2*pi*w*t)
                ##y3 = std.math.tan(2*pi*w*t)

                ##ya1 = std.math.sinh(2*pi*w*t)
                ##ya2 = std.math.cosh(2*pi*w*t)
                ##ya3 = std.math.tanh(2*pi*w*t)

                #yb1 =std.math.sin( std.math.asin(2*pi*w*t) )
                #yb2 =std.math.cos( std.math.acos(2*pi*w*t) )
                #yb3 =std.math.tan( std.math.atan(2*pi*w*t) )
                #yb4 =std.math.tan( std.math.atan2(y=2*pi*w*t, x=1) )
                #

                #s = std.math.sin(w*t)
                #yc1 =std.math.sqrt(s)
                #yc2 = std.math.ceil(s*3)
                #yc3 = std.math.floor(3*s)
                #yc4 = std.math.fabs(3*s)

                #yd1 =std.math.ln(s)
                #yd2 =std.math.log2(s)
                #yd3 =std.math.log10(s)
                #yd4 = std.math.exp(-t* w )

                #ye1 = std.math.max( x=std.math.sin(2*pi*w*t), y=-0.5 )
                #ye2 = std.math.min( x=std.math.sin(2*pi*w*t), y=0.5 )

            }
            """)



    res = library_manager.get('test_random').simulate(
        times=np.linspace(0.0, 0.200, 10000),

        )

    res.auto_plot()




if __name__ == '__main__':
    test7()

    pylab.show()

