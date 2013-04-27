

import neurounits
import neurounits.codegen.utils as utils

import numpy as np
import sys
import scipy
import pylab

from itertools import chain
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator, SimulationStateData
from neurounits.ast.nineml.simulate_component import  EventManager

import neurounits.ast as ast






class TraceResult(object):
    def __init__(self, variable, data):
        self.variable = variable
        self.data = data


class RTGraphRegimeChange(object):
    def __init__(self, time, new_regime):
        self.time = time
        self.new_regime = new_regime

class RTGraphResult(object):
    def __init__(self, rt_graph, regime_changes=None):
        self.rt_graph = rt_graph
        self.regime_changes = regime_changes if regime_changes else []

    def add_regime_change(self, rt_change):
        self.regime_changes.append(rt_change)


    def get_regime_at_time(self, time):
        i = bisect.bisect_left([ rtchange.time for rtchange in self.regime_changes], time)
        lst_rt_change = self.regime_changes[i-1]
        return lst_rt_change.new_regime

        
        #assert False


class AvailableData(object):
    def __init__(self, dt, time_pts):
        self.events = {}
        self.traces = {}
        self.rt_results = {}
        self.time_pts = time_pts
        self.dt = dt

    def get_events_in_timestep(self, portname, tstart, tstop):
        return []

    def add_result(self, trace_result):
        assert not trace_result.variable.symbol in self.traces
        self.traces[trace_result.variable.symbol] = trace_result

    def trace_dict_at_timeindex(self, time_index):
        results = {}
        for tr,res in self.traces.items():
            results[tr] = res.data[time_index]
        return results

    def add_regime_results(self, rt_result):
        assert not rt_result.rt_graph in self.rt_results
        self.rt_results[rt_result.rt_graph] = rt_result









def do_transition_change(tr, evt, state_data, functor_gen):

    functor = functor_gen.transitions_actions[tr]
    functor(state_data=state_data, evt=evt)

    # Copy the changes
    return (state_data.states_out, tr.target_regime)


import bisect
from collections import defaultdict

#def find_lt(a, x):
#    'Find rightmost value less than x'
#    i = bisect.bisect_left(a, x)
#    if i:
#        return a[i-1]
#    raise ValueError



def solve_eventblock(component, evt_blk, datastore,):
    print
    print
    print '  Solving Event Block:', evt_blk
    print '  ---------------------'


    print '    Analog Blocks:'
    for analog_blk in evt_blk.analog_blks:
        print '    ', repr(analog_blk )


    analog_blks = evt_blk.analog_blks


    state_variables = sorted( list(chain(* [analog_blk.state_variables for analog_blk in analog_blks] )) )
    assigned_variables = sorted( list(chain(* [analog_blk.assigned_variables for analog_blk in analog_blks] )) )
    rt_graphs = list(chain(* [analog_blk.rt_graphs for analog_blk in analog_blks] ))


    sv_symbol_to_index = dict( [(sv.symbol,i) for i,sv in enumerate(state_variables)] )
    ass_symbol_to_index = dict( [(ass.symbol,i) for i,ass in enumerate(assigned_variables)] )


    # Setup depandancy info:
    #print 'Block Dependancies:', evt_blk.dependancies



    #time_derivatives = [ component._eqn_time_derivatives.get_single_obj_by(lhs=sv) for sv in state_variables ]
    #n_sv = len(state_variables)
    #n_ass = len(assigned_variables)

    f = FunctorGenerator(component, as_float_in_si=True, fully_calculate_assignments=False)



    # Build the integration function:
    def int_func(y,t0, state_data):
        funcs =  [f.timederivative_evaluators[sv.symbol] for sv in state_variables ]
        func_vals = [ func(state_data=state_data) for func in funcs]
        
        res =  np.array( func_vals )

        if len(y):
            #print res, [sv.symbol for sv in state_variables]
            assert not np.isnan(np.min(res))
        return res




    time_pts = datastore.time_pts 

    # Initial state-variable values: start values are all set to zero # TODO !
    # ===========================================
    # Resolve the inital values of the states:
    initial_state_values = {}
    # Check initial state_values defined in the 'initial {...}' block: :
    for sv in state_variables:
        if sv.initial_value:
            assert isinstance(sv.initial_value, ast.ConstValue)
            initial_state_values[sv.symbol] = sv.initial_value.value.float_in_si()
        else:
            assert False, 'No initial value found for: %s'% repr(sv)

    initial_state_values_in = {}
    for (k,v) in initial_state_values_in.items():
        assert not k in initial_state_values, 'Double set intial values: %s' % k
        assert k in [td.lhs.symbol for td in component.timederivatives]
        initial_state_values[k]= v

    s = np.array([ initial_state_values[s.symbol] for s in state_variables ] )

    # Current regimes:
    print 'Starting regimes'
    from neurounits.ast.nineml.simulate_component import get_initial_regimes
    current_regimes = get_initial_regimes(rt_graphs=rt_graphs,)
    regime_results = dict( [(rt, RTGraphResult(rt) ) for (rt) in rt_graphs] )
    for rt,reg in current_regimes.items():
        regime_results[rt].add_regime_change( RTGraphRegimeChange(time=0, new_regime=reg))




    evt_manager = EventManager()

    # Load in event times from over events:
    # HORRIFIC!:
    #in_event_ports = set()
    #for rtgraph in rt_graphs:
    #    for tr in component.transitions:
    #        if not tr.parent_rt_graph == rt_graph:
    #            continue
    #        if not isinstance(tr, OnEventTransition):
    #            continue
    #        in_event_ports.add(port)

    #for in_port in in_event_ports:
        # Aggregate all sources:
        
        
    all_events = sorted(list( set(chain(*datastore.events.values()  ) ) ) )
    evt_manager.outstanding_event_list.extend(all_events)
    #for port, evts in datastore.events.items():
        



    # For calculating assignements:
    f_no_ass_dep = FunctorGenerator(component, as_float_in_si=True)





    all_sv_data = np.ones( (len(state_variables), len(time_pts)) ) * -1.
    all_ass_data = np.ones( (len(assigned_variables), len(time_pts)) ) * -0.888888e-10

    print 'Solving for SVs:', state_variables
    print 'Solving for Asses:', assigned_variables
    print 'Solving for RTs:', rt_graphs
    print 'Available traces:', datastore.traces.keys()
    print 'Available RT graphs:', datastore.rt_results.keys()
    
    print 'Depends Assigned:', evt_blk.depends_assigned_variables

    
    output_events = defaultdict(list)

    #t_prev=0.
    for t_index, t in enumerate(time_pts):
        print '\rEvaluating at %2.3f' % t,
        #print 
        sys.stdout.flush()


        evt_manager.set_time(t)

        # Build the data for this loop:
        # =================================

        # State-Variables:
        # ~~~~~~~~~~~~~~~~~
        active_state_variables = dict( zip([sv.symbol for sv in state_variables], s) )
        all_state_data = active_state_variables
        # HORRIFIC:
        all_state_data.update( datastore.trace_dict_at_timeindex(time_index=t_index) )

        # Regime:
        # ~~~~~~~
        rt_regimes = {}
        for rt_block in evt_blk.depends_rt_graphs:
            rt_data = datastore.rt_results[rt_block]
            rt_regimes[rt_block] = rt_data.get_regime_at_time(time = t)
        rt_regimes.update(current_regimes)

        # SuppliedValues:
        # ~~~~~~~~~~~~~~~~
        supplied_values = {'t': t}


        # Assignments:
        # ~~~~~~~~~~~~
        # HORRIFIC (I) (copy everything in from outside!):
        external_assignedvalues =  datastore.trace_dict_at_timeindex(time_index=t_index) 
        state_data_tmp = SimulationStateData(
            parameters=[],
            suppliedvalues=supplied_values,
            states_in= all_state_data,
            states_out={},
            rt_regimes=rt_regimes,
            assignedvalues={},
            event_manager = None,
        )
        # HORRIFIC (II)(copy everything in from outside!):

        internal_assignedvalues = {}
        for ass in assigned_variables:
            assignment_rhs = f_no_ass_dep.assignment_evaluators[ass.symbol]
            res = assignment_rhs(state_data=state_data_tmp)
            internal_assignedvalues[ass.symbol] = res
            ass_ind = ass_symbol_to_index[ass.symbol]
            all_ass_data[ ass_ind, t_index] = res

        assignedvalues = internal_assignedvalues.copy()
        assignedvalues.update(external_assignedvalues)
        #print 'Assigned VAls'
        #for (k,v) in sorted(assignedvalues.items()):
        #    print  ' -- ', k, v



        # OK, now build the data object:
        state_data = SimulationStateData(
            parameters=[], #parameters,
            suppliedvalues=supplied_values,
            states_in= all_state_data,#state_values.copy(),
            states_out={},
            rt_regimes=rt_regimes,
            assignedvalues=assignedvalues,
            event_manager = evt_manager,
        )


        # A. Update states (forward euler):
        # ==================================
        delta_s = int_func( s, t, state_data=state_data)
        
        #print 'prev s:', s
        s = s + delta_s * datastore.dt
        #print 'next s:', s


        all_sv_data[:,t_index] = s




        # B. Get all the events and forward them to appropriate ports:
        # =============================================================
        # Get all the events, and forward them to the approprate input ports:
        active_events = evt_manager.get_events_for_delivery()
        ports_with_events = {}
        for evt in active_events:
            #print evt
            output_events[evt.port].append(evt)
            #assert False
            #assert False 
            if evt.port in f.transition_event_forwarding:
                for input_port in f.transition_event_forwarding[evt.port]:
                    ports_with_events[input_port] = evt

        #get_events_in_timestep(self, portname, tstart, tstop)


        # C. Check for transitions:
        # =========================
        triggered_transitions = []
        for rt_graph in rt_graphs:
            current_regime = current_regimes[rt_graph]

            for transition in component.transitions_from_regime(current_regime):

                if isinstance(transition, ast.OnTriggerTransition):
                    res = f.transition_triggers_evals[transition]( state_data=state_data)
                    if res:
                        triggered_transitions.append((transition,None, rt_graph))
                elif isinstance(transition, ast.OnEventTransition):
                    for (port,evt) in ports_with_events.items():
                        if transition in f.transition_port_handlers[port]:
                            triggered_transitions.append((transition,evt, rt_graph))
                else:
                    assert False

        # D. Resolve the transitions:
        # ===========================
        #assert triggered_transitions == []

        if triggered_transitions:
            # Check that all transitions resolve back to this state:
            rt_graphs = set([ rt_graph for ( tr, evt, rt_graph) in triggered_transitions ])
            for rt_graph in rt_graphs:
                rt_trig_trans = ( [ tr for ( tr, evt, rt_graph_) in triggered_transitions if rt_graph_ == rt_graph ])
                target_regimes = set( [tr.target_regime for tr in rt_trig_trans] )
                assert len(target_regimes) == 1

            updated_states = set()
            for (tr,evt,rt_graph) in triggered_transitions:
                state_data.clear_states_out()
                (state_changes, new_regime) = do_transition_change(tr=tr, evt=evt, state_data=state_data, functor_gen = f)
                current_regimes[rt_graph] = new_regime

                # Save the regime change:
                chg = RTGraphRegimeChange(time = t, new_regime=new_regime)
                regime_results[rt].add_regime_change(chg)



                # Make sure that we are not changing a single state in two different transitions:
                for sv in state_changes:
                    assert not sv in updated_states, 'Multiple changes detected for: %s' % sv
                    updated_states.add(sv)
                #print state_changes

                # Make the updates:
                for symbol, new_value in state_changes.items():
                    s[ sv_symbol_to_index[symbol] ] = new_value
                # Index of that st
                #state_values.update(state_changes)



        # Mark the events as done
        for evt in active_events:
            evt_manager.marked_event_as_processed(evt)



    print
    print 'Simulation Complete'
    # Simulation complete:
    # A. Back-calculate the assignments:

    for i,sv in enumerate(state_variables):
        res = TraceResult(variable=sv, data=all_sv_data[i,:])
        datastore.add_result(res)
    
    for i,ass in enumerate(assigned_variables):
        res = TraceResult(variable=ass, data=all_ass_data[i,:])
        datastore.add_result(res)

    for rt_res in regime_results.values():
        datastore.add_regime_results(rt_res)


    if output_events:
        #print output_events
        for port, evts in output_events.items():
            datastore.events[port].extend(evts)
            print '%d events on port: %s' % (len(evts), port.symbol)


    print 'Done solving Event Block'
    print 
    print







def simulate( component, times ):
    print 'Python Simulation'
    print 'Component', component

    ev_blks = utils.separate_integration_blocks(component)





    print
    print
    print 'So, I am planning to solve:'
    for ev_blk in ev_blks:
        print '<As an event block>:'
        for analog_blk in ev_blk.analog_blks:
            print '    As a group:'
            for obj in analog_blk.objects:
                print '      -', repr(obj)
            print
        print 'then'


    print
    print
    print 'Simulating'
    tstop=0.305
    #tstop=0.010
    dt=0.01e-3
    datastore = AvailableData(
        time_pts = np.arange( dt, tstop, dt),
        dt=dt
        )

    print 'Initialising empty event queues'
    for port in component.input_event_port_lut:
        print '  Port:', repr(port)
        datastore.events[port] = []
    for port in component.output_event_port_lut:
        print '  Port:', repr(port)
        datastore.events[port] = []

    print
    print 'Solving Event Blocks:'
    for ev_blk in ev_blks:
        solve_eventblock(component=component, evt_blk=ev_blk, datastore=datastore)


    import pylab as plt

    plt.figure()
    for d in datastore.traces.values():
        print d.variable.symbol, np.min(d.data), np.max(d.data)
        sym = d.variable.symbol
        if sym == 'o1/nrn/nrn/V':
            plt.plot( datastore.time_pts, d.data, 'x-', label=d.variable.symbol)

    plt.figure()
    for d in datastore.traces.values():
        print d.variable.symbol, np.min(d.data), np.max(d.data)
        sym = d.variable.symbol
        if sym == 'o1/nrn/syn_inhib/i':
            plt.plot( datastore.time_pts, d.data, 'x-', label=d.variable.symbol)
            plt.legend()
    
    plt.figure()
    for d in datastore.traces.values():
        print d.variable.symbol, np.min(d.data), np.max(d.data)
        sym = d.variable.symbol
        if sym == 'o1/nrn/syn_inhib/A':
            plt.plot( datastore.time_pts, d.data, 'x-', label=d.variable.symbol)
            plt.legend()


    plt.figure()
    for d in datastore.traces.values():
        print d.variable.symbol, np.min(d.data), np.max(d.data)

        plt.plot( datastore.time_pts, d.data,'x', label=d.variable.symbol)

    pylab.legend()

    import itertools
    from collections import defaultdict

    si_base_units = defaultdict(list)
    plot_objs = list( itertools.chain( *[datastore.traces.values()] ) )
    for plt_obj in plot_objs:
        print plt_obj
        #terminal_obj = component.get_terminal_obj(plt_obj)
        dimension = plt_obj.variable.get_dimension()

        found = False
        for k,v in si_base_units.items():
            if k.is_compatible( dimension):
                si_base_units[k].append(plt_obj.variable)
                found = True
                break
        if not found:
            si_base_units[ dimension.with_no_powerten()].append(plt_obj.variable)

    print si_base_units
    print len(si_base_units)
    n_axes = len(si_base_units)

    f = pylab.figure()
    axes = [f.add_subplot(n_axes, 1, i+1) for i in range(n_axes)]


    print 'datastore.traces', datastore.traces

    for ((unit,objs),ax) in zip(si_base_units.items(), axes):
        ax.set_ylabel(str(unit))
        ax.margins(0.1)
        for o in sorted(objs):
            ax.plot( datastore.time_pts[1:], datastore.traces[o.symbol].data[1:], label=repr(o))
        ax.legend()



    pylab.show()






    #print
    #print
    #assert False
