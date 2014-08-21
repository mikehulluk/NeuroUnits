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
import neurounits
import numpy as np


import pylab
from neurounits import NineMLComponent



from neurounitscontrib.demo import DemoPluginBase


class Demo1(DemoPluginBase):


    def get_name(self, ):
        return '1'

    def run(self, args):
        test1()














test_text = """
    define_component step_current{
        regime OFF{
            i=0A
            on (t>t_start) {
                transition_to ON;
            }
        }

        regime ON{
            i = i_amp
        }


        <=> output i:(A)
        <=> parameter i_amp:(A), t_start
        <=> time t:(ms)
    }

    define_component simple_syn{
        A' = -A/t_open
        B' = -B/t_close

        g = g_bar * (B-A)
        i = g * (e_syn-V_post)



        regime sub{
            on(V_pre>0mV){
                A = A + 1
                B = B + 1
                transition_to super
            }
        }

        regime super{
            on(V_pre<-10mV){
                transition_to sub
            }

        }

        initial {
                regime sub
        }

        <=> output i:(A)
        <=> parameter g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
        <=> input V_pre:(V), V_post:(V)
    }




    define_component i_squarewave{
        i=0nA


        regime OFF{
            i=0A
            on (t>t_last + t_off) {
                t_last = t
                transition_to ON;
                }
            }

        regime ON{
            i = i_amp
            on (t>t_last + t_on) {
                t_last = t
                transition_to OFF;
                }
        }
        initial{
            t_last = 0s
            regime OFF
        }

        <=> parameter t_on, t_off
        <=> output i:(A)
        <=> parameter i_amp:(A)
        <=> time t:(ms)

        }


    define_component std_neuron {


        V' = i_sum / C

        <=> summed_input i_sum
        <=> parameter C:(uF)
        <=> output     V: mV

    }

    define_component chlstd_leak {


        i = g * (erev-V) *a
        a = 1000 um2
        <=> parameter g:(S/m2), erev
        <=> output    i:(mA)
        <=> input     V: mV

    }

    define_component evt_gen {


        regime std{
            t_last'=0
            on(t > t_last + {100ms}){
                t_last = t
                emit myevent(5pS)
                emit myotherevent(x=5pS, y=6pA)
            }
        }

        initial{
            t_last = 0s
            regime std
            }

        <=> time t:(ms)
    }


    define_component evt_syn{
        A' = -A/t_open
        B' = -B/t_close

        g = g_bar * (B-A)
        i = g * (e_syn-V_post)


        on myevent(amp:(S)){
            A = A + 1 + amp/{1mS}
            B = B + 1 + amp/{1mS}
        }

        <=> output i:(A)
        <=> parameter g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
        <=> input  V_post:(V)
    }



"""




























def test1():
    library_manager =  neurounits.NeuroUnitParser.Parse9MLFile(test_text )
    chlstd_leak = library_manager.get('chlstd_leak')
    std_neuron = library_manager.get('std_neuron')
    step_current = library_manager.get('step_current')
    square_current = library_manager.get('i_squarewave')
    simple_syn1 = library_manager.get('simple_syn')

    evt_gen = library_manager.get('evt_gen')
    evt_syn = library_manager.get('evt_syn')



    c1 = NineMLComponent.build_compound_component(
          component_name = 'Neuron1',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron, 'i_inj':step_current, 'i_square':square_current },
          event_connections = [],
          analog_connections = [
            ('i_inj/i', 'nrn/i_sum'),
            ('lk/i', 'nrn/i_sum'),
            ('i_square/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c2 = NineMLComponent.build_compound_component(
          component_name = 'Neuron2',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron,},
          event_connections = [],
          analog_connections = [
            ('lk/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c3 = NineMLComponent.build_compound_component(
          component_name = 'driven_synapse',
          instantiate = { 'spike_gen': evt_gen, 'syn': evt_syn,},
          event_connections = [
            ('spike_gen/myevent', 'syn/myevent' ),
            ],
          analog_connections = [
          ],
    )



    c = NineMLComponent.build_compound_component(
          component_name = 'network',
          instantiate = { 'nrn1': c1, 'nrn2': c2, 'syn1':simple_syn1, 'syn2':c3},
          event_connections = [],
          analog_connections = [
            ('syn1/i','nrn2/nrn/i_sum'),
            ('nrn1/nrn/V','syn1/V_pre'),
            ('nrn2/nrn/V','syn1/V_post'),

            ('syn2/syn/i','nrn2/nrn/i_sum'),
            ('nrn2/nrn/V','syn2/syn/V_post'),
          ],
          )

    res = c.simulate(
                        times = np.linspace(0,1,num=1000),
                        close_reduce_ports=True,
                        parameters={
                            'nrn1/i_inj/i_amp':'5pA',
                            'nrn1/lk/g': '0.1pS/um2',
                            'nrn1/nrn/C': '0.5pF',
                            'nrn1/lk/erev': '-60mV',
                            'nrn1/i_inj/t_start': '500ms',
                            'nrn1/i_square/t_on': '100ms',
                            'nrn1/i_square/t_off': '50ms',
                            'nrn1/i_square/i_amp': '2pA',

                            'nrn2/lk/g': '0.1pS/um2',
                            'nrn2/nrn/C': '0.5pF',
                            'nrn2/lk/erev': '-55mV',

                            'syn1/t_open': '3ms',
                            'syn1/t_close': '10ms',
                            'syn1/g_bar': '100pS',
                            'syn1/e_syn': '0mV',

                            'syn2/syn/t_close':'80ms',
                            'syn2/syn/t_open':'4ms',
                            'syn2/syn/g_bar': '10pS',
                            'syn2/syn/e_syn': '0mV',

                            },
                        initial_state_values={
                            'nrn1/nrn/V': '-50mV',
                            'nrn2/nrn/V': '-60mV',
                            'syn1/A':'0',
                            'syn1/B':'0',

                            'syn2/syn/A':'0',
                            'syn2/syn/B':'0',
                        },
                        initial_regimes={
                            'nrn1/i_inj/':'OFF',
                        }
            )

    f = pylab.figure()
    ax1 = f.add_subplot(3,1,1)
    ax2 = f.add_subplot(3,1,2)
    ax3 = f.add_subplot(3,1,3)
    ax1.set_ylim((-70e-3,50e-3))
    ax1.plot(res.get_time(), res.state_variables['nrn1/nrn/V'] )
    ax1.plot(res.get_time(), res.state_variables['nrn2/nrn/V'] )
    ax1.set_ylabel('nrn1/nrn/V %s' %('??'))
    ax2.plot(res.get_time(), res.state_variables['nrn1/i_square/t_last'] )
    ax3.plot(res.get_time(), res.rt_regimes['nrn1/nrn/']+0.0 , label='nrn1/nrn')
    ax3.plot(res.get_time(), res.rt_regimes['nrn1/i_inj/']+0.1, label='nrn1/i_inj')
    ax3.plot(res.get_time(), res.rt_regimes['nrn1/i_square/']+0.2, label='nrn1/i_square' )
    ax3.legend()





def main():
    test1()
    pylab.show()


if __name__ == '__main__':
    main()

