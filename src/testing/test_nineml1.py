#!/usr/bin/python
# -*- coding: utf-8 -*-

import neurounits
import sys
import numpy as np

from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree
import neurounits.ast as ast
from neurounits.ast_builder.eqnsetbuilder import BuildData
from neurounits.ast_builder.eqnsetbuilder import SingleSetDict
from neurounits.ast import NineMLComponent
from neurounits.ast import SuppliedValue
from neurounits.ast.astobjects_nineml import AnalogReducePort
from neurounits.visitors.common.ast_replace_node import ReplaceNode

import pylab
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator, SimulationStateData



src_files = [
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ,
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/more_components.9ml" ,
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/complex_component.9ml" ,
]

src_files = [s.replace('libs/','') for s in src_files]


library_manager = None
for s in src_files:
    text = open(s).read()
    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( text, library_manager=library_manager)
    #print library_manager





#print library_manager.components



#def summarise_component(comp):
#    print comp
#    for k,v in comp.__dict__.items():
#        if k[0] == '_':
#            #continue
#            pass
#        print '  ', k,v
#    print comp.__dict__
#
#    params = inspect.getmembers(comp)
#    for k in params:
#        if k[0][0] == '_':
#            continue
#        try:
#            print '  ', k
#        except:
#            pass
#
#    for tr in comp.transitions:
#        print tr
#        for a in tr.actions:
#
#            print ' ', a
#
#for comp in library_manager.components:
#    print
#    summarise_component(comp)



#print 'Components Loaded:'
#for comp in library_manager.components:
#    print comp.name






test_text = """
module test {
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


    define_component std_neuron2 {


        V' = i_sum / C

        <=> ANALOG_REDUCE_PORT i_sum
        <=> PARAMETER C:(uF)
        <=> OUTPUT     V: mV

    }

    define_component chlstd_leak2 {


        i = g * (erev-V) *a
        a = 1000 um2
        <=> PARAMETER g:(S/m2), erev
        <=> OUTPUT    i:(mA)
        <=> INPUT     V: mV

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


}
"""


library_manager = neurounits.NeuroUnitParser.Parse9MLFile( test_text )

#for component in library_manager.components:
#    print component















def build_compound_component(name, instantiate,  analog_connections, event_connections=None,  remap_ports=None, prefix='/', auto_remap_time=True):

    





    lib_mgrs = list(set( [comp.library_manager for comp in instantiate.values()]) )
    assert len( lib_mgrs ) == 1 and lib_mgrs[0] is not None
    lib_mgr = lib_mgrs[0]


    #First step, lets build a new component, by cloning all the components:
    # Cloned Components:
    #for (name, component) in instantiate.items():
    #    c = CloneObject().visit(


    symbols_not_to_rename = []
    if auto_remap_time:
        time_node = SuppliedValue(symbol='t')
        symbols_not_to_rename.append(time_node)

        for (component_name, component) in instantiate.items():
            print component.terminal_symbols
            if component.has_terminal_obj('t'):
                ReplaceNode(srcObj=component.get_terminal_obj('t'), dstObj=time_node).visit(component)

                component._cache_nodes()

    # 2. Rename all the internal names of the objects:
    for (component_name, component) in instantiate.items():
        # Symbols:
        for obj in component.terminal_symbols:
            if obj in symbols_not_to_rename:
                continue
            obj.symbol = component_name + prefix + obj.symbol


        # RT Graphs names (not the names of the regimes!):
        for rtname, obj in component.rt_graphs.items():
            obj.name = component_name + prefix + (obj.name if obj.name else '')







    # 3. Copy the relevant parts of the AST tree into a new build-data object:
    builddata = BuildData()
    builddata.eqnset_name = name

    builddata.timederivatives = SingleSetDict()
    builddata.assignments = SingleSetDict()
    builddata.rt_graphs = SingleSetDict()

    for c in instantiate.values():
        for td in c.timederivatives:
            builddata.timederivatives[td.lhs] = td
        for ass in c.assignments:
            builddata.assignments[ass.lhs] = ass

        for symconst in c.symbolicconstants:
            builddata.symbolicconstants[symconst.symbol] = symconst

        for rt_graph in c.rt_graphs.values():
            builddata.rt_graphs[rt_graph.name] = rt_graph

        builddata.transitions_triggers.extend(c._transitions_triggers)
        builddata.transitions_events.extend(c._transitions_events)

    # 4. Build the object:
    comp = NineMLComponent(library_manager = lib_mgr,
                    builder = None,
                    builddata = builddata,
                    io_data = [],
                    )



    # 5. Connect the relevant ports internally:
    for (src, dst) in analog_connections:

        src_obj = comp.get_terminal_obj(src)
        dst_obj = comp.get_terminal_obj(dst)

        if isinstance(dst_obj, AnalogReducePort):
            dst_obj.rhses.append(src_obj)
        elif isinstance(dst_obj, SuppliedValue):
            ReplaceNode(srcObj=dst_obj, dstObj=src_obj).visit(comp)
        else:
            assert False, 'Unexpected node type: %s' % dst_obj
        comp._cache_nodes()

    # 6. Map relevant ports externally:
    if remap_ports:
        for (src, dst) in remap_ports:
            assert not dst in [s.symbol for s in comp.terminal_symbols]
            comp._cache_nodes()

    comp._cache_nodes()

    # Ensure all the units are propogated ok, because we might have added new
    # nodes:
    PropogateDimensions.propogate_dimensions(comp)
    VerifyUnitsInTree(comp, unknown_ok=False)

    # Return the new component:
    return comp







def close_analog_port(ap, comp):
    new_node = None
    if len(ap.rhses) == 1:
        new_node = ap.rhses[0]
    if len(ap.rhses) == 2:
        new_node = ast.AddOp(ap.rhses[0], ap.rhses[1])
    if len(ap.rhses) == 3:
        new_node = ast.AddOp(ap.rhses[0], ast.AddOp(ap.rhses[1],
                             ap.rhses[2]))

    assert new_node is not None
    ReplaceNode(srcObj=ap, dstObj=new_node).visit(comp)
    comp._cache_nodes()
    PropogateDimensions.propogate_dimensions(comp)


def close_all_analog_reduce_ports(component):
    for ap in component.analog_reduce_ports:
        print 'Closing', ap
        close_analog_port(ap, component)


class SimulationResultsData(object):
    def __init__(self, times, state_variables, assignments, transitions, rt_regimes):
        self.times = times
        self.state_variables = state_variables
        self.assignments = assignments
        self.transitions = transitions
        self.rt_regimes = rt_regimes

    def get_time(self):
        return self.times


def do_transition_change(tr, state_data, functor_gen):
    print 'Transition Triggered!',
    # State assignments & events:
    functor = functor_gen.transitions_actions[tr]
    functor(state_data=state_data)

    # Copy the changes
    return (state_data.states_out, tr.target_regime)


def simulate_component(component, times, parameters,initial_state_values, initial_regimes, close_reduce_ports):
    verbose=False

    # Before we start, check the dimensions of the AST tree
    VerifyUnitsInTree(component, unknown_ok=False)

    # Close all the open analog ports:
    if close_reduce_ports:
        close_all_analog_reduce_ports(component)

    # Sort out the parameters and initial_state_variables:
    # =====================================================
    neurounits.Q1 = neurounits.NeuroUnitParser.QuantitySimple
    parameters = dict( (k, neurounits.Q1(v)) for (k,v) in parameters.items() )
    initial_state_values = dict( (k, neurounits.Q1(v)) for (k,v) in initial_state_values.items() )

    # Sanity check, are the parameters and initial state_variable values in teh right units:
    for (k, v) in parameters.items() + initial_state_values.items():
        print k, v
        terminal_obj = component.get_terminal_obj(k)
        assert terminal_obj.get_dimension().is_compatible(v.get_units())
    # =======================================================

    # Resolve initial regimes:
    # ========================
    # i. Initial, make initial regimes 'None', then lets try and work it out:
    current_regimes = dict( [ (rt, None) for rt in component.rt_graphs.values()] )

    # ii. Is there just a single regime?
    for (rt_graph, regime) in current_regimes.items():
        if len(rt_graph.regimes) == 1:
            current_regimes[rt_graph] = rt_graph.regimes.values()[0]

    # iii. Do the transion graphs have a 'init' block?
    for rt_graph in component.rt_graphs.values():
        if rt_graph.has_regime(name='init'):
            current_regimes[rt_graph] = rt_graph.get_regime(name='init')

    # iv. Explicitly provided:
    for (rt_name, regime_name) in initial_regimes.items():
        rt_graph = component.rt_graphs[rt_name]
        assert current_regimes[rt_graph] is None, "Initial state for '%s' set twice " % rt_graph.name
        current_regimes[rt_graph]  = rt_graph.get_regime( name=regime_name )

    # v. Check everything is hooked up OK:
    for rt_graph, regime in current_regimes.items():
        assert regime is not None, " Start regime for '%s' not set! " % (rt_graph.name)
        assert regime in rt_graph.regimes.values()

    print 'Initial_regimes', current_regimes



    # ======================





    #state = safe_dict_merge( parameters, initial_state_values, current_regimes)
    #event_handler = EventHandler()

    f = FunctorGenerator(component)

    reses_new = []
    print 'Running Simulation:'
    print

    state_values = initial_state_values.copy()
    for i in range(len(times) - 1):

        t = times[i]
        if verbose:
            print 'Time:', t
            print '---------'
            print state_values
        print '\rTime: %s' % str('%2.2f' % t).ljust(5),
        sys.stdout.flush()




        t_unit = t * neurounits.NeuroUnitParser.QuantitySimple('1s')
        supplied_values = {'t': t_unit}

        # Build the data for this loop:
        state_data = SimulationStateData(
            parameters=parameters,
            suppliedvalues=supplied_values,
            states_in=state_values,
            states_out={},
            rt_regimes=current_regimes,
        )

        # Save the state data:
        reses_new.append(state_data.copy())

        # Compute the derivatives at each point:
        deltas = {}
        for td in component.timederivatives:
            td_eval = f.timederivative_evaluators[td.lhs.symbol]
            res = td_eval(state_data=state_data)
            deltas[td.lhs.symbol] = res

        # Update the states:
        for (d, dS) in deltas.items():
            assert d in state_values
            state_values[d] += dS * (times[i+1] - times[i] ) * neurounits.NeuroUnitParser.QuantitySimple('1s')

       
        # Check for transitions:
        #print 'Checking for transitions:'
        for rt_graph in component.rt_graphs.values():
            current_regime = current_regimes[rt_graph]
            #print '  ', rt_graph, '(in %s)' % current_regime
            for transition in component.transitions_from_regime(current_regime):
                #print '       Checking',  transition
                res = f.transition_triggers_evals[transition]( state_data=state_data)

                if res:
                    (state_changes, new_regime) = do_transition_change(tr=transition, state_data=state_data, functor_gen = f)
                    state_values.update(state_changes)
                    current_regimes[rt_graph] = new_regime




    # Build the results:
    # ------------------


    # A. Times:
    #times = np.array( [t for (t,states) in reses] )
    times = np.array( [time_pt_data.suppliedvalues['t'].float_in_si() for time_pt_data in reses_new] )

    # B. State variables:
    state_names = [s.symbol for s in component.states]

    state_data_dict = {}
    for state_name in state_names:
        states_data = [time_pt_data.states_in[state_name].float_in_si() for time_pt_data in reses_new]
        states_data = np.array(states_data)
        state_data_dict[state_name] = states_data

    # C. Assigned Values:
    # TODO:

    # D. RT-gragh Regimes:
    # Build a dictionary mapping regimes -> Regimes, to make plotting easier:
    regimes_to_ints_map = {}
    for rt_graph in component.rt_graphs.values():
        regimes_to_ints_map[rt_graph] = dict( zip(  rt_graph.regimes.values(),range(len(rt_graph.regimes)),) )

    rt_graph_data = {}
    for rt_graph in component.rt_graphs.values():
        regimes = [ time_pt_data.rt_regimes[rt_graph] for time_pt_data in reses_new]
        regimes_ints = np.array([ regimes_to_ints_map[rt_graph][r] for r in regimes])
        rt_graph_data[rt_graph.name] = (regimes_ints) 





    # Hook it all up:
    res = SimulationResultsData(times=times,
                                state_variables=state_data_dict,
                                rt_regimes=rt_graph_data,
                                assignments={}, transitions=[])

    return res


def test1():
    #def merge_components( components
    library_manager =  neurounits.NeuroUnitParser.Parse9MLFile( test_text )
    chlstd_leak = library_manager.get('chlstd_leak')
    std_neuron = library_manager.get('std_neuron')
    step_current = library_manager.get('step_current')
    square_current = library_manager.get('i_squarewave')
    simple_syn1 = library_manager.get('simple_syn')
    simple_syn2 = library_manager.get('simple_syn')

    chlstd_leak2 = library_manager.get('chlstd_leak2')
    std_neuron2 = library_manager.get('std_neuron2')

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
          instantiate = { 'lk': chlstd_leak2, 'nrn': std_neuron2,},
          event_connections = [],
          analog_connections = [
            ('lk/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
    )

    
    c = build_compound_component(
          name = 'network',
          instantiate = { 'nrn1': c1, 'nrn2': c2, 'syn1':simple_syn1},
          event_connections = [],
          analog_connections = [
            ('syn1/i','nrn2/nrn/i_sum'),
            ('nrn1/nrn/V','syn1/V_pre'),
            ('nrn2/nrn/V','syn1/V_post'),
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

                            },
                        initial_state_values={
                            'nrn1/nrn/V': '-50mV',
                            'nrn2/nrn/V': '-60mV',
                            'nrn1/i_square/t_last': '0ms',
                            'syn1/A':'0',
                            'syn1/B':'0',
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
    pylab.show()








    #res = simulate_component(component=c,
    #                    times = np.linspace(0,1,num=1000),
    #                    close_reduce_ports=True,
    #                    parameters={
    #                        'i_inj/i_amp':'5pA',
    #                        'lk/g': '0.1pS/um2',
    #                        'nrn/C': '0.5pF',
    #                        'lk/erev': '-60mV',
    #                        'i_inj/t_start': '500ms',
    #                        'i_square/t_on': '100ms',
    #                        'i_square/t_off': '50ms',
    #                        'i_square/i_amp': '2pA',


    #                        },
    #                    initial_state_values={
    #                        'nrn/V': '-50mV',
    #                        'i_square/t_last': '0ms'
    #                    },
    #                    initial_regimes={
    #                        'i_inj/':'OFF',
    #                        #'i_square/':'OFF'
    #                    }
    #        )


    #f = pylab.figure()
    #ax1 = f.add_subplot(3,1,1)
    #ax2 = f.add_subplot(3,1,2)
    #ax3 = f.add_subplot(3,1,3)
    #ax1.set_ylim((-70e-3,50e-3))
    #ax1.plot( res.get_time(), res.state_variables['nrn/V'] )
    #ax1.set_ylabel('nrn/V %s' %('??'))
    #ax2.plot( res.get_time(), res.state_variables['i_square/t_last'] )
    #ax3.plot( res.get_time(), res.rt_regimes['nrn/']+0.0 , label='nrn')
    #ax3.plot( res.get_time(), res.rt_regimes['i_inj/']+0.1, label='i_inj')
    #ax3.plot( res.get_time(), res.rt_regimes['i_square/']+0.2,label='i_square' )
    #ax3.legend()
    #pylab.show()



#test2()
test1()

