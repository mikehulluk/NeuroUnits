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




from neurounitscontrib.demo import DemoPluginBase
class Demo3(DemoPluginBase):


    def get_name(self):
        return '3'

    def run(self, args):
        test3()










def test3():
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
            initial{
                regime sub

            }

            <=> output i:(A)
            <=> parameter g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
            <=> input V_pre:(V), V_post:(V)
        }




        define_component i_squarewave{
            t_last'=0



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
            t_last'=0



            regime std{
                t_last'=0
                on(t > t_last + {100ms}){
                    t_last = t
                    emit myevent(5pS)
                    emit myotherevent(x=5pS, y=6pA)
                }
            }
            <=> time t:(ms)


            initial{
                t_last=0ms
                regime std

            }

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



            define_multiport_type std_pt_process {
                    ==>> V: (V)
                    <<== I: (A)
                    #==?> events_in (V:S)
                    #<?== events_out( a:(),b:() )
            }



            define_compound_component mymeganeuron {
                    instantiate chlstd_leak as lk
                    instantiate std_neuron as nrn
                    instantiate step_current as i_inj
                    instantiate i_squarewave  as i_square1
                    instantiate i_squarewave  as i_square2

                    connect i_inj/i to nrn/i_sum
                    connect lk/i to nrn/i_sum
                    connect i_square1/i  to nrn/i_sum
                    connect i_square2/i  to nrn/i_sum
                    connect nrn/V to lk/V

                    rename nrn/V to V
                    rename nrn/i_sum to I_in

                    merge [ i_square1/t_on, i_square1/t_off, i_square2/t_on, i_square2/t_off] as t_in



                    <=> multiport std_pt_process[out] as IO_pt_proc  {
                           V <==> V
                           I_in <==> I
                    }
            }



            define_compound_component synwrap {

                    instantiate evt_gen as evts
                    instantiate evt_syn as psm

                    connect evts/myevent to psm/myevent



                    <=> multiport std_pt_process[in] as IO_post {
                           # Local <==> Coumpound-Port name
                           psm/V_post <==> V
                           psm/i <==> I
                    }



            }


            define_compound_component mymeganeuron_hubby {
                    instantiate mymeganeuron as nrn
                    instantiate synwrap as synin

                    # New way!:
                    multiconnect nrn/IO_pt_proc to synin/IO_post

                    # Old way:
                    #connect synin/psm/V_post to nrn/V
                    #connect synin/psm/i to  nrn/I_in



            }




    """




    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( test_text )

    s_IO = library_manager.get('std_pt_process')
    s_IO.summarise()



    s_nrn = library_manager.get('mymeganeuron_hubby')
    s_nrn.summarise()


    c = library_manager.get('mymeganeuron_hubby')

    c.summarise()




    parameters = {
            'synin/psm/t_close':'80ms',
            'nrn/i_square2/i_amp':'5pA',
            'nrn/nrn/C':'0.5pF',
            'synin/psm/e_syn':'0mV',
            'nrn/lk/g':'0.1pS/um2',
            'synin/psm/t_open':'4ms',
            'nrn/i_square1/i_amp':'5pA',
            'nrn/i_inj/i_amp':'5pA',
            'nrn/t_in':'300ms',
            'nrn/lk/erev':'-60mV',
            'nrn/i_inj/t_start':'5ms',
            'synin/psm/g_bar':'100pS',
               }

    initial_states = {
        'nrn/V':'0mV',
        'nrn/i_square1/t_last':'0ms',
        'nrn/i_square2/t_last':'0ms',
        'synin/psm/A':'0',
        'synin/psm/B':'0'
        }

    res = c.simulate(
                    times = np.linspace(0, 1,num=1000),
                    close_reduce_ports=True,
                    parameters=parameters,
                    initial_state_values=initial_states,
                    initial_regimes={
                        'nrn/i_inj/':'OFF', 

                    }

                    )

    res.auto_plot()



if __name__ == '__main__':
    test3()
    pylab.show()



"""
define_multiport std_pt_process {
    ==>> V
    <<== I
}


define_component {

    <=> multiport std_pt_process[in] as IO {
        IO/V is V
        IO/I is I_in
    }

}
"""
