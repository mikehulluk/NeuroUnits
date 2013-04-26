

import neurounits
import neurounits.codegen.utils as utils

import numpy as np
import sys
import scipy
import pylab

from itertools import chain
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator, SimulationStateData






class TraceResult(object):
    def __init__(self, variable, data):
        self.variable = variable
        self.data = data

class AvailableData(object):
    def __init__(self,):
        self.events = {}
        self.traces = {}

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












def solve_eventblock(component, evt_blk, datastore, tstop=0.500, dt=0.1e-3):
    print
    print '  Solving Event Block:', evt_blk

    print '    Analog Blocks:'
    for analog_blk in evt_blk.analog_blks:
        print '    ', repr(analog_blk )


    analog_blks = evt_blk.analog_blks


    state_variables = list(chain(* [analog_blk.state_variables for analog_blk in analog_blks] ))
    assigned_variables = list(chain(* [analog_blk.assigned_variables for analog_blk in analog_blks] ))
    rt_graphs = list(chain(* [analog_blk.rt_graphs for analog_blk in analog_blks] ))


    # Setup depandancy info:
    print 'Block Dependancies:', evt_blk.dependancies

    #print rt_graphs
    #assert False


    time_derivatives = [ component._eqn_time_derivatives.get_single_obj_by(lhs=sv) for sv in state_variables ]

    n_sv = len(state_variables)
    n_ass = len(assigned_variables)

    f = FunctorGenerator(component, as_float_in_si=True)



    # Build the integration function:
    def int_func(y,t0, state_data):
        funcs =  [f.timederivative_evaluators[sv.symbol] for sv in state_variables ]
        func_vals = [ func(state_data=state_data) for func in funcs]
        return np.array( func_vals )




    time_pts = np.arange( dt, tstop, dt)

    # Initial values: start values are all set to zero # TODO !
    # ===========================================
    s = np.array([ 0. for s in state_variables ] )
    from neurounits.ast.nineml.simulate_component import get_initial_regimes

    current_regimes = get_initial_regimes(rt_graphs=rt_graphs,)

    









    all_data = np.ones( (len(state_variables), len(time_pts)) ) * -1.

    print 'Solving for SVs:', state_variables
    print 'Solving for RTs:', rt_graphs
    print 'Available traces:', datastore.traces.keys()


    t_prev=0.
    for t_index, t in enumerate(time_pts):
        print '\rEvaluating at %2.3f' % t,
        sys.stdout.flush()


        # Build the data for this loop:
        active_state_variables = dict( zip([sv.symbol for sv in state_variables], s) )
        all_state_data = active_state_variables
        all_state_data.update( datastore.trace_dict_at_timeindex(time_index=t_index) )



        state_data = SimulationStateData(
            parameters=[], #parameters,
            suppliedvalues= [], #supplied_values,
            states_in= all_state_data,#state_values.copy(),
            states_out={},
            rt_regimes={}, #current_regimes,
            event_manager = None,# evt_manager,
        )


        # A. Update states (forward euler):
        # ==================================
        delta_s = int_func( s, t, state_data=state_data)
        s_next = s + delta_s * dt
        all_data[:,t_index] = s_next




        # B. Get all the events and forward them to appropriate ports:
        # =============================================================

        #get_events_in_timestep(self, portname, tstart, tstop)


        # C. Check for transitions:
        # =========================
        for rt_graph in rt_graphs:
            print 'Updating RT_graph:', rt_graph
            #assert False

        # D. Resolve the transitions:
        # ===========================




    # Simulation complete:
    # A. Back-calculate the assignments:

    for i,sv in enumerate(state_variables):
        res = TraceResult(variable=sv, data=all_data[i,:])
        datastore.add_result(res)




    pylab.figure()
    #pylab.plot(time_pts, all_data[0,:], '-')
    #pylab.show()

    #print
    #print
    #assert False








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
    datastore = AvailableData()

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






    print
    print
    assert False
