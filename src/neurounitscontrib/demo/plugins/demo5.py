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

