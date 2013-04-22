#!/usr/bin/python
# -*- coding: utf-8 -*-

import neurounits
import sys
import numpy as np
import itertools

import pylab
from neurounits.nineml import build_compound_component
from neurounits.nineml import simulate_component, auto_plot





from yapsy.IPlugin import IPlugin
class PluginOne(IPlugin):
    def get_name(self):
        return '3'

    def run_demo(self, ):
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


            <=> OUTPUT i:(A)
            <=> PARAMETER i_amp:(A), t_start
            <=> INPUT t:(ms)
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

            <=> OUTPUT i:(A)
            <=> PARAMETER g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
            <=> INPUT V_pre:(V), V_post:(V)
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

            <=> PARAMETER t_on, t_off
            <=> OUTPUT i:(A)
            <=> PARAMETER i_amp:(A)
            <=> INPUT t:(ms)

            }


        define_component std_neuron {


            V' = i_sum / C

            <=> ANALOG_REDUCE_PORT i_sum
            <=> PARAMETER C:(uF)
            <=> OUTPUT     V: mV

        }

        define_component chlstd_leak {


            i = g * (erev-V) *a
            a = 1000 um2
            <=> PARAMETER g:(S/m2), erev
            <=> OUTPUT    i:(mA)
            <=> INPUT     V: mV

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
            <=> INPUT t:(ms)
            
            
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


            on myevent(amp:{S}){
                A = A + 1 + amp/{1mS}
                B = B + 1 + amp/{1mS}
            }

            <=> OUTPUT i:(A)
            <=> PARAMETER g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
            <=> INPUT  V_post:(V)
        }



            define_compoundport std_pt_process {
                    ==>> V : (V)
                    <<== I : (A)
                    #==?> events_in (V:S)
                    #<?== events_out( a:(),b:() )
            }



            define_compound mymeganeuron {
                    instantiate chlstd_leak as lk
                    instantiate std_neuron as nrn 
                    instantiate step_current as i_inj
                    instantiate i_squarewave  as i_square1
                    instantiate i_squarewave  as i_square2

                    connect i_inj/i <==> nrn/i_sum
                    connect lk/i <==> nrn/i_sum
                    connect i_square1/i  <==> nrn/i_sum
                    connect i_square2/i  <==> nrn/i_sum
                    connect nrn/V <==> lk/V

                    rename nrn/V to V
                    rename nrn/i_sum to I_in

                    merge [ i_square1/t_on, i_square1/t_off, i_square2/t_on, i_square2/t_off] as t_in


                    compoundport IO_pt_proc of_type std_pt_process  <out> {
                           V <==> V
                           I_in <==> I
                    }
            }



            define_compound synwrap {

                    instantiate evt_gen as evts
                    instantiate evt_syn as psm

                    connect evts/myevent <==> psm/myevent


                    
                    compoundport IO_post of_type std_pt_process <in> {
                           # Local <==> Coumpound-Port name
                           psm/V_post <==> V
                           psm/i <==> I
                    }

                    

            }
            

            define_compound mymeganeuron_hubby {
                    instantiate mymeganeuron as nrn
                    instantiate synwrap as synin
            
                    # New way!:
                    multiconnect nrn/IO_pt_proc <==> synin/IO_post
                    
                    # Old way:
                    #connect synin/psm/V_post <==> nrn/V
                    #connect synin/psm/i <==> nrn/I_in
                    
                    

            }




    """




    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( test_text )

    s_IO = library_manager.get('std_pt_process')
    s_IO.summarise()



    s_nrn = library_manager.get('mymeganeuron_hubby')
    s_nrn.summarise()


    c = library_manager.get('mymeganeuron_hubby')

    c.summarise()

    #assert False


    parameters = {
            'synin/psm/t_close':'80ms',      #(<MMUnit: (10e0) s 1>)',
            'nrn/i_square2/i_amp':'5pA',    #(<MMUnit: (10e0) A 1>)', 
            'nrn/nrn/C':'0.5pF',               #(<MMUnit: (10e0) m -2 kg -1 s 4 A 2>)',
            'synin/psm/e_syn':'0mV',        #(<MMUnit: (10e0) m 2 kg 1 s -3 A -1>)',
            'nrn/lk/g':'0.1pS/um2',               #(<MMUnit: (10e0) m -4 kg -1 s 3 A 2>)', 
            'synin/psm/t_open':'4ms',       #(<MMUnit: (10e0) s 1>)',
            'nrn/i_square1/i_amp':'5pA',    #(<MMUnit: (10e0) A 1>)',
            'nrn/i_inj/i_amp':'5pA',        #(<MMUnit: (10e0) A 1>)', 
            'nrn/t_in':'300ms',               #(<MMUnit: (10e0) s 1>)', 
            'nrn/lk/erev':'-60mV',            #(<MMUnit: (10e0) m 2 kg 1 s -3 A -1>)',
            'nrn/i_inj/t_start':'5ms',      #(<MMUnit: (10e0) s 1>)',
            'synin/psm/g_bar':'100pS',        #(<MMUnit: (10e0) m -2 kg -1 s 3 A 2>)'
               }
               
    initial_states = {
        'nrn/V':'0mV', 
        'nrn/i_square1/t_last':'0ms', 
        'nrn/i_square2/t_last':'0ms', 
        #'synin/evts/t_last':'0ms', 
        'synin/psm/A':'0', 
        'synin/psm/B':'0'
        }

    res = simulate_component(component=c,
                    times = np.linspace(0, 1,num=1000),
                    close_reduce_ports=True,
                    parameters=parameters,
                    initial_state_values=initial_states,
                    initial_regimes={
                    'nrn/i_inj/':'OFF',
                    
                    }
                    
                    )

    auto_plot(res)



if __name__ == '__main__':
    test3()
    
