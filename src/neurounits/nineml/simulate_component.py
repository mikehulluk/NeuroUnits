
from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree
import neurounits.ast as ast
#from neurounits.ast_builder.eqnsetbuilder import BuildData
#from neurounits.ast import NineMLComponent
#from neurounits.ast import SuppliedValue
#from neurounits.ast.astobjects_nineml import AnalogReducePort
from neurounits.visitors.common.ast_replace_node import ReplaceNode

#import pylab
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator, SimulationStateData

import neurounits
import sys
import numpy as np

from collections import defaultdict


def _build_ADD_ast(nodes):
    assert len(nodes) > 0
    if len(nodes) == 1:
        return nodes[0]
    if len(nodes) == 2:
        return ast.AddOp( nodes[0], nodes[1] )
    else:
        return ast.AddOp( nodes[0], _build_ADD_ast(nodes[1:]))

def close_analog_port(ap, comp):
    new_node = None
    if len(ap.rhses) == 0:
        assert False, 'No input found for reduce port? (maybe this is OK!)'

    new_node = _build_ADD_ast(ap.rhses)

    assert new_node is not None
    ReplaceNode.replace_and_check(srcObj=ap, dstObj=new_node, root=comp)

    PropogateDimensions.propogate_dimensions(comp)


def close_all_analog_reduce_ports(component):
    for ap in component.analog_reduce_ports:
        close_analog_port(ap, component)


class SimulationResultsData(object):
    def __init__(self, times, state_variables, assignments, transitions, rt_regimes, events, component):
        self.times = times
        self.state_variables = state_variables
        self.assignments = assignments
        self.transitions = transitions
        self.rt_regimes = rt_regimes

        self.events = events
        self.component = component

    def get_time(self):
        return self.times


    def get_data(self, name):
        assert isinstance(name, basestring)
        if name in self.state_variables:
            return self.state_variables[name]
        elif name in self.assignments:
            return self.assignments[name]
        else:
            assert False, 'Could not find: %s' % name


def do_transition_change(tr, evt, state_data, functor_gen):
    #print 'Doing transition change', tr
    #print 'Transition Triggered!',
    # State assignments & events:
    #assert evt==None


    functor = functor_gen.transitions_actions[tr]
    functor(state_data=state_data, evt=evt)

    # Copy the changes
    return (state_data.states_out, tr.target_regime)



class Event(object):
    def __init__(self, port, parameter_values, time):
        self.port = port
        self.parameter_values = parameter_values
        self.time = time

    def __repr__(self):
        return '<Event at %s on Port:%s (Parameters: %s)>' % (self.time, self.port, self.parameter_values)



class EventManager(object):
    def __init__(self, ):
        self.previous_time = None
        self.current_time = None

        self.outstanding_event_list = []
        self.processed_event_list = []

    def emit_event(self, port, parameter_values):

        submit_time = self.current_time + neurounits.NeuroUnitParser.QuantitySimple('10ms')
        self.outstanding_event_list.append( Event( port=port, parameter_values=parameter_values, time=submit_time) )

    def set_time(self, t):
        self.previous_time = self.current_time
        self.current_time = t


    def get_events_for_delivery(self):
        events = [ evt for evt in self.outstanding_event_list if evt.time > self.previous_time and evt.time <= self.current_time ]
        return events

    def marked_event_as_processed(self, event):
        assert event in self.outstanding_event_list
        assert not event in self.processed_event_list
        self.outstanding_event_list.remove(event)
        self.processed_event_list.append(event)




import itertools
import pylab

def auto_plot(res):


    si_base_units = defaultdict(list)
    plot_objs = list( itertools.chain( res.state_variables.keys(), res.assignments.keys(),) )
    for plt_obj in plot_objs:
        print plt_obj
        terminal_obj = res.component.get_terminal_obj(plt_obj)
        dimension = terminal_obj.get_dimension()

        found = False
        for k,v in si_base_units.items():
            if k.is_compatible( dimension):
                si_base_units[k].append(plt_obj)
                found = True
                break
        if not found:
            si_base_units[ dimension.with_no_powerten()].append(plt_obj)



    print si_base_units
    print len(si_base_units)
    n_axes = len(si_base_units)

    f = pylab.figure()
    axes = [f.add_subplot(n_axes, 1, i+1) for i in range(n_axes)]


    for ((unit,objs),ax) in zip(si_base_units.items(), axes):
        ax.set_ylabel(str(unit))
        ax.margins(0.1)
        for o in sorted(objs):
            ax.plot( res.get_time(), res.get_data(o), label=o)
        ax.legend()


    #pylab.show()

    #assert False


    #plot_objs = list( itertools.chain( res.state_variables.items(), res.assignments.items(),) )# res.rt_regimes.items() ) )
    #n_axes = len(plot_objs)
    #f = pylab.figure()
    #axes = [f.add_subplot(n_axes, 1, i+1) for i in range(len(plot_objs))]


    #for (plot_name,plot_obj), ax in zip( plot_objs, axes):
    #    ax.plot(res.get_time(), plot_obj)
    #    ax.set_ylabel(plot_name + '   ',rotation=0, horizontalalignment='right' )


    #print
    #print 'Transitions:'
    #for tr in res.transitions:
    #    print tr
    ##f.tight_layout()
    #pylab.show()
    #assert False





def simulate_component(component, times, parameters=None,initial_state_value=None, initial_regimes=None, close_reduce_ports=True):

    parameters = parameters if parameters is not None else {}
    initial_regimes = initial_regimes if initial_regimes is not None else {}
    initial_state_values = initial_state_value if initial_state_value is not None else {}
    verbose=False

    # Before we start, check the dimensions of the AST tree
    VerifyUnitsInTree(component, unknown_ok=False)
    component.propagate_and_check_dimensions()

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
        #print k, v
        terminal_obj = component.get_terminal_obj(k)
        assert terminal_obj.get_dimension().is_compatible(v.get_units())
    # =======================================================



    # Sanity Check:
    for rt_graph in component.rt_graphs:
        if rt_graph.default_regime:
            assert rt_graph.default_regime in rt_graph.regimes
    # Resolve initial regimes:
    # ========================
    # i. Initial, make initial regimes 'None', then lets try and work it out:
    current_regimes = dict( [ (rt, None) for rt in component.rt_graphs] )

    # ii. Is there just a single regime?
    for (rt_graph, regime) in current_regimes.items():
        if len(rt_graph.regimes) == 1:
            current_regimes[rt_graph] = rt_graph.regimes.get_single_obj_by()

    # iii. Do the transion graphs have a 'init' block?
    #for rt_graph in component.rt_graphs:
    #    if rt_graph.has_regime(name='init'):
    #        current_regimes[rt_graph] = rt_graph.get_regime(name='init')
    for rt_graph in component.rt_graphs:
        if rt_graph.default_regime is not None:
            current_regimes[rt_graph] = rt_graph.default_regime


    # iv. Explicitly provided:
    for (rt_name, regime_name) in initial_regimes.items():
        rt_graph = component.rt_graphs.get_single_obj_by(name=rt_name)
        assert current_regimes[rt_graph] is None, "Initial state for '%s' set twice " % rt_graph.name
        current_regimes[rt_graph]  = rt_graph.get_regime( name=regime_name )

    # v. Check everything is hooked up OK:
    for rt_graph, regime in current_regimes.items():
        assert regime is not None, " Start regime for '%s' not set! " % (rt_graph.name)
        assert regime in rt_graph.regimes, 'regime: %s [%s]' % (repr(regime), rt_graph.regimes  )



    
    #print
    #print 'Initial_regimes'
    #for k,v in current_regimes.items():
    #    print repr(k), repr(v)
    #print

    # Check we have all the nodes:
    #from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
    #nodes = EqnsetVisitorNodeCollector(component).nodes
    #for n in nodes[ast.RTBlock]:
    #    print repr(n)
    #assert False


    # Resolve the inital values of the states:
    state_values = {}
    # Check initial state_values defined in the 'initial {...}' block: :
    for td in component.timederivatives:
        sv = td.lhs
        #print repr(sv), sv.initial_value
        if sv.initial_value:
            assert isinstance(sv.initial_value, ast.ConstValue)
            state_values[sv.symbol] = sv.initial_value.value

    for (k,v) in initial_state_values.items():
        assert not k in state_values, 'Double set intial values: %s' % k
        assert k in [td.lhs.symbol for td in component.timederivatives]
        state_values[k]= v


    #assert False





    # ======================



    one_second =  neurounits.NeuroUnitParser.QuantitySimple('1s')




    f = FunctorGenerator(component)

    evt_manager = EventManager()

    reses_new = []
    print 'Running Simulation:'
    print

    #state_values = initial_state_values.copy()
    for i in range(len(times) - 1):

        t = times[i]
        if verbose:
            print 'Time:', t
            print '---------'
            print state_values
        print '\rTime: %s' % str('%2.3f' % t).ljust(5),
        sys.stdout.flush()




        t_unit = t * one_second
        supplied_values = {'t': t_unit}
        evt_manager.set_time(t_unit)

        # Build the data for this loop:
        state_data = SimulationStateData(
            parameters=parameters,
            suppliedvalues=supplied_values,
            states_in=state_values,
            states_out={},
            rt_regimes=current_regimes,
            event_manager = evt_manager,
        )

        # Save the state data:
        reses_new.append(state_data.copy())

        # Compute the derivatives at each point:
        deltas = {}
        for td in component.timederivatives:
            #print 'Evaluating:', td.lhs.symbol
            td_eval = f.timederivative_evaluators[td.lhs.symbol]
            res = td_eval(state_data=state_data)
            deltas[td.lhs.symbol] = res

        # Update the states:
        for (d, dS) in deltas.items():
            assert d in state_values, "Found unexpected delta: %s " %( d )
            #print 'State Var:', d,state_values[d], dS
            state_values[d] += dS * (times[i+1] - times[i] ) * one_second


        # Get all the events, and forward them to the approprate input ports:
        active_events = evt_manager.get_events_for_delivery()
        #print '\nEvents:', active_events
        ports_with_events = {}
        for evt in active_events:
            #print 'Evt!', evt
            if evt.port in f.transition_event_forwarding:
                for input_port in f.transition_event_forwarding[evt.port]:
                    ports_with_events[input_port] = evt




        # Check for transitions:
        #print 'Checking for transitions:'
        for rt_graph in component.rt_graphs:
            current_regime = current_regimes[rt_graph]
            #print '  ', rt_graph, '(in %s)' % current_regime

            triggered_transitions = []
            for transition in component.transitions_from_regime(current_regime):
                print '       Checking',  repr(transition)

                if isinstance(transition, ast.OnTriggerTransition):
                    res = f.transition_triggers_evals[transition]( state_data=state_data)
                    if res:
                        triggered_transitions.append((transition,None))
                elif isinstance(transition, ast.OnEventTransition):
                    for (port,evt) in ports_with_events.items():
                        if transition in f.transition_port_handlers[port]:
                            triggered_transitions.append((transition,evt))
                else:
                    assert False

            allow_double_transition_only_action_first = False
            if not allow_double_transition_only_action_first:
                assert len(triggered_transitions) in (0,1)
            assert len(triggered_transitions) in (0,1)
            if triggered_transitions:
                tr, evt = triggered_transitions[0]

                (state_changes, new_regime) = do_transition_change(tr=tr, evt=evt, state_data=state_data, functor_gen = f)
                state_values.update(state_changes)
                current_regimes[rt_graph] = new_regime

        # Mark the events as done
        for evt in active_events:
            evt_manager.marked_event_as_processed(evt)

        #assert False



    # Build the results:
    # ------------------


    # A. Times:
    #times = np.array( [t for (t,states) in reses] )
    times = np.array( [time_pt_data.suppliedvalues['t'].float_in_si() for time_pt_data in reses_new] )

    # B. State variables:
    state_names = [s.symbol for s in component.state_variables]

    state_data_dict = {}
    for state_name in state_names:
        states_data = [time_pt_data.states_in[state_name].float_in_si() for time_pt_data in reses_new]
        states_data = np.array(states_data)
        state_data_dict[state_name] = states_data
        print 'State:', state_name
        print '  (Min:', np.min( states_data), ', Max:', np.max( states_data), ')'

    # C. Assigned Values:

    # TODO:
    assignments ={}
    for ass in component.assignedvalues:
        ass_res = []
        for time_pt_data in reses_new:
            print "\r%s %2.3f" % (ass.symbol, time_pt_data.suppliedvalues['t'].float_in_si()),
            td_eval = f.assignment_evaluators[ass.symbol]
            res = td_eval(state_data=time_pt_data)
            ass_res.append(res.float_in_si())
        #print ass_res
        assignments[ass.symbol] = np.array(ass_res)
        print
        print '  (Min:', np.min( assignments[ass.symbol]), ', Max:', np.max( assignments[ass.symbol]), ')'


    # D. RT-gragh Regimes:
    # Build a dictionary mapping regimes -> Regimes, to make plotting easier:
    regimes_to_ints_map = {}
    for rt_graph in component.rt_graphs:
        regimes_to_ints_map[rt_graph] = dict( zip(  iter(rt_graph.regimes),range(len(rt_graph.regimes)),) )

    rt_graph_data = {}
    for rt_graph in component.rt_graphs:
        regimes = [ time_pt_data.rt_regimes[rt_graph] for time_pt_data in reses_new]
        regimes_ints = np.array([ regimes_to_ints_map[rt_graph][r] for r in regimes])
        rt_graph_data[rt_graph.name] = (regimes_ints)


    # Print the events:
    for evt in evt_manager.processed_event_list:
        print evt



    # Hook it all up:
    res = SimulationResultsData(times=times,
                                state_variables=state_data_dict,
                                rt_regimes=rt_graph_data,
                                assignments=assignments, transitions=[],
                                events = evt_manager.processed_event_list[:],
                                component = component
                                )

    return res

