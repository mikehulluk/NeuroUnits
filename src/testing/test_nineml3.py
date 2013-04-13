#!/usr/bin/python
# -*- coding: utf-8 -*-

import neurounits
import sys
import numpy as np
import itertools

import pylab
from neurounits.nineml import build_compound_component
from neurounits.nineml import simulate_component

#pylab.ion()



def test0():
    src_files = [
        "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ,
        "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/more_components.9ml" ,
        "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/complex_component.9ml" ,
    ]

    #src_files = [s.replace('libs/','') for s in src_files]


    library_manager = None
    for s in src_files:
        text = open(s).read()
        library_manager = neurounits.NeuroUnitParser.Parse9MLFile( text, library_manager=library_manager)










test_text = """
namespace test {
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
        regime init{
            on(0<1){
                transition_to sub
            }
        }

        #init_with {
        #    A = 0
        #    B = 0
        #    transition_to sub
        #}

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

        <=> OUTPUT i:(A)
        <=> PARAMETER g_bar:(uS), t_open:(ms), t_close:(ms), e_syn:(V)
        <=> INPUT V_pre:(V), V_post:(V)
    }




    define_component i_squarewave{
        t_last'=0
        i=0nA
        regime init{
            i=0A
            on(0<1){
                t_last = 0s
                transition_to OFF
                }
        }

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

        regime init{
            t_last'=0
            on(0<1){
                t_last = 0s
            transition_to std
            }
        }

        regime std{
            t_last'=0
            on(t > t_last + {100ms}){
                t_last = t
                emit myevent(5pS)
                emit myotherevent(x=5pS, y=6pA)
            }
        }
        <=> INPUT t:(ms)
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
    'synin/evts/t_last':'0ms', 
    'synin/psm/A':'0', 
    'synin/psm/B':'0'
    }
#Inputs: ['t']
#  Outputs: ['nrn/i_inj/i (<MMUnit: (10e0) A 1>)', 'nrn/i_square1/i (<MMUnit: (10e0) A 1>)', 'nrn/i_square2/i (<MMUnit: (10e0) A 1>)', 'nrn/lk/i (<MMUnit: (10e0) A 1>)', 'synin/psm/g (<MMUnit: (10e0) m -2 kg -1 s 3 A 2>)', 'synin/psm/i (<MMUnit: (10e0) A 1>)']
#  ReducePorts: ['nrn/I_in (<MMUnit: (10e0) A 1>)'] 


res = simulate_component(component=c,
                times = np.linspace(0, 1,num=1000),
                close_reduce_ports=True,
                parameters=parameters,
                initial_state_values=initial_states,
                initial_regimes={
                'nrn/i_inj/':'OFF',
                
                }
                
                )




def auto_plot(res):
    plot_objs = list( itertools.chain( res.state_variables.items(), res.assignments.items(), res.rt_regimes.items() ) )
    n_axes = len(plot_objs)
    f = pylab.figure()    
    axes = [f.add_subplot(n_axes, 1, i+1) for i in range(len(plot_objs))]
    
    
    for (plot_name,plot_obj), ax in zip( plot_objs, axes):
        #print ax, plot_obj
        ax.plot(res.get_time(), plot_obj)
        ax.set_ylabel(plot_name + '   ',rotation=0, horizontalalignment='right' )
        ax.set_yticks([])
        ax.set_yticklabels([])

    print 
    print 'Transitions:'
    for tr in res.transitions:
        print tr
    #f.tight_layout()
    pylab.show()
    assert False


auto_plot(res)






















f = pylab.figure()
ax1 = f.add_subplot(3,1,1)
ax2 = f.add_subplot(3,1,2)
ax3 = f.add_subplot(3,1,3)
ax1.set_ylim((-70e-3,50e-3))
ax1.plot( res.get_time(), res.state_variables['nrn/V'] )
ax1.set_ylabel('nrn1/V %s' %('??'))

ax2.plot( res.get_time(), res.assignments['synin/psm/i'] )
ax3.plot( res.get_time(), res.assignments['synin/psm/g'] )
#synin/psm/i
#ax2.plot( res.get_time(), res.state_variables['nrn1/i_square/t_last'] )
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/nrn/']+0.0 , label='nrn1/nrn')
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_inj/']+0.1, label='nrn1/i_inj')
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_square/']+0.2,label='nrn1/i_square' )
ax3.legend()
pylab.show()





assert False






res = simulate_component(component=c,
                times = np.linspace(0,1,num=1000),
                close_reduce_ports=True,
                parameters={
                        'nrn/i_inj/t_start' : '5ms',
                        'synin/psm/e_syn': '0mV',
                        'nrn/lk/g': '0.1pS/um2',
                        'nrn/i_inj/i_amp': '5pA',
                        'synin/psm/t_close':'10ms',
                        'nrn/lk/erev': '-55mV',
                        'synin/psm/t_open': '3ms',
                        'synin/psm/g_bar': '100pS',
                        'nrn/i_square2/i_amp': '2pA',
                        'nrn/i_square1/i_amp': '2pA',
                        'nrn/nrn/C':  '0.5pF',
                        'nrn/t_in': '300ms',
                    },
                initial_state_values={


                         'nrn/V':'-50mV',
                         'nrn/i_square1/t_last':'0ms',
                         'nrn/i_square2/t_last':'0ms',
                         'synin/evts/t_last':'0ms',
                         'synin/psm/A':'0',
                         'synin/psm/B':'0',

                },
                initial_regimes={
                    'nrn/i_inj/':'OFF',
                }
    )



f = pylab.figure()
ax1 = f.add_subplot(3,1,1)
ax2 = f.add_subplot(3,1,2)
ax3 = f.add_subplot(3,1,3)
ax1.set_ylim((-70e-3,50e-3))
ax1.plot( res.get_time(), res.state_variables['nrn/V'] )
ax1.set_ylabel('nrn1/nrn/V %s' %('??'))

ax2.plot( res.get_time(), res.assignments['synin/psm/i'] )
ax3.plot( res.get_time(), res.assignments['synin/psm/g'] )
#synin/psm/i
#ax2.plot( res.get_time(), res.state_variables['nrn1/i_square/t_last'] )
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/nrn/']+0.0 , label='nrn1/nrn')
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_inj/']+0.1, label='nrn1/i_inj')
#ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_square/']+0.2,label='nrn1/i_square' )
ax3.legend()
pylab.show()





assert False







"""
    c1 = build_compound_component(
          name = 'Neuron1',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron, 'i_inj':step_current, 'i_square':square_current },
          event_connections = [],
          analog_connections = [
            ('i_inj/i', 'nrn/i_sum'),
            ('lk/i', 'nrn/i_sum'),
            ('i_square/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c2 = build_compound_component(
          name = 'Neuron2',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron,},
          event_connections = [],
          analog_connections = [
            ('lk/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c3 = build_compound_component(
          name = 'driven_synapse',
          instantiate = { 'spike_gen': evt_gen, 'syn': evt_syn,},
          event_connections = [
            ('spike_gen/myevent', 'syn/myevent' ), 
            ],
          analog_connections = [
            #('lk/i', 'nrn/i_sum'),
            #('nrn/V', 'lk/V'),
          ],
    )


    
    c = build_compound_component(
          name = 'network',
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
"""
































t = """
define_compound mymeganeuron {
        instantiate mynrn as N
        instantiate mysyn as S1
        instantiate mysyn as S2

        connect interfaces N <=> S1
        connect interfaces N <=> S2

        

        
    }
"""




















def test1():
    #def merge_components( components
    library_manager =  neurounits.NeuroUnitParser.Parse9MLFile( test_text )
    chlstd_leak = library_manager.get('chlstd_leak')
    std_neuron = library_manager.get('std_neuron')
    step_current = library_manager.get('step_current')
    square_current = library_manager.get('i_squarewave')
    simple_syn1 = library_manager.get('simple_syn')
    simple_syn2 = library_manager.get('simple_syn')

    evt_gen = library_manager.get('evt_gen')
    evt_syn = library_manager.get('evt_syn')
    
    

    c1 = build_compound_component(
          name = 'Neuron1',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron, 'i_inj':step_current, 'i_square':square_current },
          event_connections = [],
          analog_connections = [
            ('i_inj/i', 'nrn/i_sum'),
            ('lk/i', 'nrn/i_sum'),
            ('i_square/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c2 = build_compound_component(
          name = 'Neuron2',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron,},
          event_connections = [],
          analog_connections = [
            ('lk/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )


    c3 = build_compound_component(
          name = 'driven_synapse',
          instantiate = { 'spike_gen': evt_gen, 'syn': evt_syn,},
          event_connections = [
            ('spike_gen/myevent', 'syn/myevent' ), 
            ],
          analog_connections = [
            #('lk/i', 'nrn/i_sum'),
            #('nrn/V', 'lk/V'),
          ],
    )


    
    c = build_compound_component(
          name = 'network',
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

    res = simulate_component(component=c,
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
                            'nrn1/i_square/t_last': '0ms',
                            'syn1/A':'0',
                            'syn1/B':'0',
                            
                            'syn2/syn/A':'0',
                            'syn2/syn/B':'0',
                            'syn2/spike_gen/t_last':'0ms',
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
    ax1.plot( res.get_time(), res.state_variables['nrn1/nrn/V'] )
    ax1.plot( res.get_time(), res.state_variables['nrn2/nrn/V'] )
    ax1.set_ylabel('nrn1/nrn/V %s' %('??'))
    ax2.plot( res.get_time(), res.state_variables['nrn1/i_square/t_last'] )
    ax3.plot( res.get_time(), res.rt_regimes['nrn1/nrn/']+0.0 , label='nrn1/nrn')
    ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_inj/']+0.1, label='nrn1/i_inj')
    ax3.plot( res.get_time(), res.rt_regimes['nrn1/i_square/']+0.2,label='nrn1/i_square' )
    ax3.legend()




from logbook import FileHandler
log_handler = FileHandler('application.log')
log_handler.push_application()

from neurounits.logging import logbook as lb

def main():
    test0()
    test1()
    pylab.show()
main()

