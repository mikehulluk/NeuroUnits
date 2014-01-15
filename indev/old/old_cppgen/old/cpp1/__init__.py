


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


    #analog_blks = evt_blk.analog_blks


    state_variables = evt_blk.state_variables
    assigned_variables = evt_blk.assigned_variables
    rt_graphs = evt_blk.rt_graphs


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

                if isinstance(transition, ast.OnConditionTriggerTransition):
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









import mako




header1 = r"""

#include <stdlib.h>
#include <stdio.h>



/* Header files with a description of contents used */

#include <cvode/cvode.h>             /* prototypes for CVODE fcts., consts. */
#include <nvector/nvector_serial.h>  /* serial N_Vector types, fcts., macros */
#include <cvode/cvode_dense.h>       /* prototype for CVDense */
#include <sundials/sundials_dense.h> /* definitions DlsMat DENSE_ELEM */
#include <sundials/sundials_types.h> /* definition of type realtype */

#include <assert.h>





/*
 * Check function return value...
 *   opt == 0 means SUNDIALS function allocates memory so check if
 *            returned NULL pointer
 *   opt == 1 means SUNDIALS function returns a flag so check if
 *            flag >= 0
 *   opt == 2 means function allocates memory so check if returned
 *            NULL pointer
 */

static int check_flag(void *flagvalue, char *funcname, int opt)
{
  int *errflag;

  /* Check if SUNDIALS function returned NULL pointer - no memory allocated */
  if (opt == 0 && flagvalue == NULL) {
    fprintf(stderr, "\nSUNDIALS_ERROR: %s() failed - returned NULL pointer\n\n",
	    funcname);
    return(1); }

  /* Check if flag < 0 */
  else if (opt == 1) {
    errflag = (int *) flagvalue;
    if (*errflag < 0) {
      fprintf(stderr, "\nSUNDIALS_ERROR: %s() failed with flag = %d\n\n",
	      funcname, *errflag);
      return(1); }}

  /* Check if function returned NULL pointer - no memory allocated */
  else if (opt == 2 && flagvalue == NULL) {
    fprintf(stderr, "\nMEMORY_ERROR: %s() failed - returned NULL pointer\n\n",
	    funcname);
    return(1); }

  return(0);
}



"""


header2 = """


// CUSTOM CONFIG:

    //typedef REAL double;


#define RTOL  RCONST(1.0e-4)


    class EventManager {


    };

    //#class DataManager {
    //#};

    class RTGraphManager {
    };


class DataStore {
public:
    EventManager event_mgr;
    DataManager data_mgr;
    RTGraphManager rtgraph_mgr;


};


"""




solver_function = """

int solve_system()
{


    // Setup control data structures:
    DataStore data_store = DataStore();
    // Call each function to solve the blocks:
    %for name in ev_blk_func_names:
        ${name}(data_store);
    %endfor




}



int main(int argc, char* argv[] )
{

    solve_system();


    return 0;
}
"""



from mako.template  import Template
from mako.template import Template
from mako.runtime import Context
from StringIO import StringIO


class DataMgrBuilder(object):
    def __init__(self, ev_blks, cpp_builddata, component):
    #def __init__(self,  evt_blks):
        self.evt_blks = ev_blks
        self.cpp_builddata = cpp_builddata
        self.component = component



    def get_text(self):

        templ = """
        class DataManager {
        public:

        %for evt_blk in ev_blks:
            //Evt Block: ${evt_blk}
            %for sv in evt_blk.state_variables:
                inline float set_${sv.symbol.replace("/","__")}(float* time, float* data){
                    printf("Setting data for: ${sv.symbol}");
                    printf("Build cublic interpolator...");

                    printf("OK!");
                }

                inline float get_${sv.symbol.replace("/","__")}(float time)
                {
                    return 0.0000001;
                }



            %endfor
        %endfor


        };

        """

        mytemplate = Template(templ)
        buf = StringIO()
        ctx = Context(buf, ev_blks=self.evt_blks)
        mytemplate.render_context(ctx)
        res = buf.getvalue() + ('\n' * 3)
        return res

        #return templ















ev_blk_function = r"""

<%def name="print_list(listname, lst, attr='symbol')">
%if len(lst) != 0:
    // ${listname} (${len(lst)})
    %for sv in lst:
    //       - ${getattr(sv, attr) }
    %endfor
%endif
</%def>









// Event Block Evaluation: ${ev_blk_index}
// ============================
<% evt_blk_user_data_typename = 'EvtBlkUserInfo%d' % ev_blk_index  %>
<% evt_blk_regime_typename = 'EvtBlkRTStates%d' % ev_blk_index  %>
<% trigger_transition_count = len(bd.tr_index_by_evt_blk[ev_blk]) %>

// A structure that hold the possible states of the current regime graphs:
struct ${evt_blk_regime_typename} {
    public:
    %for rt_graph in ev_blk.rt_graphs:
    <% rt_name = bd.rt_graph_name(rt_graph) %>
    enum States_${rt_name} {
        %for regime in bd.rt_graph_regimes(rt_graph):
            ${bd.regime_name(regime)},
        %endfor
    };
    %endfor

    %for rt_graph in ev_blk.rt_graphs:
    <% rt_name = bd.rt_graph_name(rt_graph) %>
    enum States_${rt_name}  ${rt_name} ;
    %endfor
};

struct ${evt_blk_user_data_typename} {

    ${evt_blk_user_data_typename}(DataStore* pDS, ${evt_blk_regime_typename}* pRegimes  )
    : pDS(pDS), pRegimes(pRegimes)
    {
    }

    ${evt_blk_regime_typename}* pRegimes;
    DataStore* pDS;

};


// Triggers:
// -----------
%for rt_graph in ev_blk.rt_graphs:
    %for tr in bd.rt_graph_trigger_map[rt_graph]:
        <%
        fn = bd.func_def_tr_triggers[tr]
        %>
//Transistion: ${repr(tr)}
${fn.signature}
{
    ${fn.body}
}
    %endfor
%endfor



// Large function that covers all the functions:
int trig_${ev_blk_index}(realtype t, N_Vector y, realtype *gout, void *user_data )
{
//printf("Evaluating Root function!\n");
%for tr,i in bd.tr_index_by_evt_blk[ev_blk].items():
    gout[${i}] = ${bd.func_def_tr_triggers[tr].name} (t, y, gout, user_data) ;
    //printf("%f\n",  gout[${i}]  );
%endfor
return (0);

}

// Gradient function:
int f_block_${ev_blk_index}(realtype t, N_Vector y, N_Vector ydot, void *user_data)
{
    //DataStore* pDS = (DataStore*) user_data;
    ${evt_blk_user_data_typename} * pD = (${evt_blk_user_data_typename} *) user_data;

    return(0);
}


int evaluate_event_block_${ev_blk_index}(DataStore& ds )
{
    printf("Starting to evaluate EvtBlock: ${ev_blk_index}");


    // Dependancies:
    // ------------
    ${print_list("State Variables", ev_blk.depends_state_variables) }
    ${print_list("Assigned Variables", ev_blk.depends_assigned_variables) }
    ${print_list("RT-Graphs", ev_blk.depends_rt_graphs, attr='name') }

    // Resolves:
    // ---------
    ${print_list("State Variables", ev_blk.state_variables) }
    ${print_list("Assigned Variables", ev_blk.assigned_variables) }
    ${print_list("RT-Graphs", ev_blk.rt_graphs, attr='name') }

    const int n_states = ${len(ev_blk.state_variables)} + 1;
    const int NEQ = n_states;

    const float t_start = 0.0f;




    // Setup CVODE:
    // -------------
    printf("\n  - Setting Up CVODE...");
    realtype reltol, t;
    N_Vector y, abstol;
    void *cvode_mem;
    int flag, flagr, iout;


    y = abstol = NULL;
    cvode_mem = NULL;

    /* Create serial vector of length NEQ for I.C. and abstol */
    y = N_VNew_Serial(NEQ);
    if (check_flag((void *)y, "N_VNew_Serial", 0)) return(1);
    abstol = N_VNew_Serial(NEQ);
    if (check_flag((void *)abstol, "N_VNew_Serial", 0)) return(1);


    // Setup the initial values:
    % for i, sv, in enumerate(ev_blk.state_variables):
    NV_Ith_S(y,${i}) = 0.0; // TODO - use real values not zero!
    %endfor

    // Setup the tolerances:
    reltol = RTOL;
    % for i, sv, in enumerate(ev_blk.state_variables):
    NV_Ith_S(abstol,${i}) = RCONST(1.0e-8);
    %endfor
    // Dodgy last variable:
    NV_Ith_S(abstol,n_states-1) = RCONST(1.0e-8);


  /* Call CVodeCreate to create the solver memory and specify the
   * Backward Differentiation Formula and the use of a Newton iteration */
  cvode_mem = CVodeCreate(CV_BDF, CV_NEWTON);
  if (check_flag((void *)cvode_mem, "CVodeCreate", 0)) return(1);



/* Call CVodeInit to initialize the integrator memory and specify the
   * user's right hand side function in y'=f(t,y), the inital time T0, and
   * the initial dependent variable vector y. */
  flag = CVodeInit(cvode_mem, f_block_${ev_blk_index}, t_start, y);
  if (check_flag(&flag, "CVodeInit", 1)) return(1);

  /* Call CVodeSVtolerances to specify the scalar relative tolerance
   * and vector absolute tolerances */
  flag = CVodeSVtolerances(cvode_mem, reltol, abstol);
  if (check_flag(&flag, "CVodeSVtolerances", 1)) return(1);


  /* Call CVDense to specify the CVDENSE dense linear solver */
  flag = CVDense(cvode_mem, NEQ);
  if (check_flag(&flag, "CVDense", 1)) return(1);


  /* Set the Jacobian routine to Jac (user-supplied) */
  //flag = CVDlsSetDenseJacFn(cvode_mem, Jac);
  //if (check_flag(&flag, "CVDlsSetDenseJacFn", 1)) return(1);


  // Setup the transitions:
    %if trigger_transition_count:
    flag = CVodeRootInit(cvode_mem, ${trigger_transition_count}, trig_${ev_blk_index});
    if (check_flag(&flag, "CVodeRootFind", 1)) return(1);
    %endif



    // Structure containing the current regime_state:
    ${evt_blk_regime_typename}  current_regimes;
    // TODO - set initial states!
    %for rt_graph in ev_blk.rt_graphs:
    <% rt_name = bd.rt_graph_name(rt_graph) %>
    current_regimes.${rt_name} = 0; // ERROR!
    %endfor

    // Construct the object that contains a pointer to the local regime states,
    // as well as the global datastore:
    ${evt_blk_user_data_typename} user_data = ${evt_blk_user_data_typename} (&ds, &current_regimes);



  /* In loop, call CVode, print results, and test for error.*/
  printf("OK");


    // Point to user data:
    CVodeSetUserData(cvode_mem, &user_data);








    // CORE LOOP:
    // ------------

    // The core loop proceeds as:
    // A. Integrate forward one time-step, (but stop on transitions)
    // B. While not done:
        // B1. Resolve any events that are emitted, and add to output queues:
        // B2. Work out which transitions are triggered, and
        //     update all the regime graphs, state-variables appropriately
        //   , and output events.


    printf("\nCore Loop:\n");
    iout = 0;
    float t_stop = 0.3;
    int n_points = 200;



    // Active transition changes:
    // These transitions tell us what transions are triggered on this round!
    bool triggered_transitions_conditiontriggers[${trigger_transition_count}];
    <%event_transition_count = 0 %>
    bool triggered_transitions_events[${event_transition_count}]; //TODO


    FILE* fp = fopen("op/res_evt_blk_${ev_blk_index}.txt","w");
    fprintf(fp, "\t t");
    % for i, sv, in enumerate(ev_blk.state_variables):
    fprintf(fp, "\t ${sv.symbol}");
    % endfor



    int i=0;
    for(i=1;i< n_points; i++)
    {
        // Reset all the transitions:
         // Triggers:
         for(int itr=0;itr < ${trigger_transition_count}; itr++)
         {
             triggered_transitions_conditiontriggers[itr] = false;
         }
          // Events::
         for(int itr=0;itr < ${event_transition_count}; itr++)
         {
             triggered_transitions_events[itr] = false;
         }




      float t_next = t_start + (t_stop-t_start)/n_points * i;
      printf("\r   Advancing to: %f", t_next);

      // Advance to the next stopping point:
      flag = CVode(cvode_mem, t_next, y, &t, CV_NORMAL);

      bool possible_transition = false;
      if( flag == CV_ROOT_RETURN){


         printf("\n     Root Found at: %f\n",t_next);

         // Which transitions occured:
         int found_roots[${trigger_transition_count}] ;
         CVodeGetRootInfo(cvode_mem, found_roots);
         if (check_flag(&flag, "Error with finding roots", 1)) return(1);

         // Resolve the roots and see what transions are triggered::
         %for tr,i in bd.tr_index_by_evt_blk[ev_blk].items():
         <% rt_graph = tr.rt_graph %>
         <%rt_name = bd.rt_graph_name(rt_graph) %>
         // Is the trigger met, and are we in the corect regime?
         //Transition: ${repr(tr)}
         if(
            (current_regimes.${bd.rt_graph_name(rt_graph)} == ${evt_blk_regime_typename}::States_${rt_name}::${bd.regime_name(tr.src_regime )})
            &&
            (found_roots[ ${bd.tr_index_by_evt_blk[ev_blk][tr]} ] )
            )
         {
            //printf("\nTransition triggered! ${repr(tr)} \n");
            possible_transition = true;
            triggered_transitions_conditiontriggers[ ${bd.tr_index_by_evt_blk[ev_blk][tr]} ] = true;
         }
         %endfor


      }
      else if(flag == CV_TSTOP_RETURN) {
         printf("Hard stop found!: %f\n",t_next);
        assert(0);

      }
      else if(flag == CV_SUCCESS) {
      }
      else {
      assert(0);
      }



      // Resolve the transitions:
      if(possible_transition){

        ${evt_blk_regime_typename}  new_regimes;
        %for rt_graph in ev_blk.rt_graphs:
        <% rt_name = bd.rt_graph_name(rt_graph) %>
        new_regimes.${rt_name} = -1;
        %endfor

        realtype new_states[n_states];
        bool state_changes[n_states] = {false};

         // Triggers:
         ###%for tr,i in range(trigger_transition_count):
         %for tr,i in bd.tr_index_by_evt_blk[ev_blk].items():
         if( triggered_transitions_conditiontriggers[${i}] ){
            printf("\nTransition triggered! ${repr(tr)} \n");
            // ${repr(tr)}
            // Events:
            // == Todo! ===

            // Set StateVariables:
            %for (state_assignment, state_ass_gen) in bd.state_variable_updates_for_transition(tr):
            //state_assignment.lhs.symbol = ${state_ass_gen.visit((state_assignment.rhs)) };
            <% sv_index = bd.sv_index_by_evt_blk[ev_blk][state_assignment.lhs] %>
            assert( state_changes[ ${sv_index} ] == false);
            new_states[ ${sv_index} ] =  ${state_ass_gen.visit((state_assignment.rhs)) };
            state_changes[ ${sv_index} ] =  true;
            %endfor


            // Target Regime:
            // ---------------
            <% rt_graph = tr.rt_graph %>
            <% rt_name = bd.rt_graph_name(rt_graph) %>
            if( new_regimes.${bd.rt_graph_name(rt_graph)} == -1 ) {
                new_regimes.${bd.rt_graph_name(rt_graph)} = ${evt_blk_regime_typename}::States_${rt_name}::${bd.regime_name(tr.target_regime)}; 
                printf("At A\n");
            }
            else if (new_regimes.${bd.rt_graph_name(rt_graph)} == ${evt_blk_regime_typename}::States_${rt_name}::${bd.regime_name(tr.target_regime)}) {
                // Pass, no need to do anything:
                printf("At B\n");
            }
            else {
                assert(false); // Double set!
            }



         }
         %endfor


         // OK, now lets update the current data:
         //Regimes:
        %for rt_graph in ev_blk.rt_graphs:
        <% rt_name = bd.rt_graph_name(rt_graph) %>
        if( new_regimes.${rt_name} != -1){
            current_regimes.${rt_name} = new_regimes.${rt_name};
            printf("Regime Change: ${rt_name} to %d\n", new_regimes.${rt_name} );
            fprintf(fp,"\nRegime Change: ${rt_name} to %d\n", new_regimes.${rt_name} );
        }
        %endfor

         // State-Variables:
         % for i, sv, in enumerate(ev_blk.state_variables):
         if( state_changes[ ${i} ])  NV_Ith_S(y,${i}) = new_states[ ${i} ];
         %endfor


        // OK, we have made changes, so lets reinitialise cv_ode:
        flag = CVodeReInit(cvode_mem, t, y);
        if (check_flag(&flag, "CVodeReInit", 1)) return(1);


        }








      // Write the output to a file:
      fprintf(fp,"\n");
      fprintf(fp,"%f", t);
      % for i, sv, in enumerate(ev_blk.state_variables):
      fprintf(fp, "\t%f" , NV_Ith_S(y,${i}) );
      % endfor



      //loop_function(t,y);


      //PrintOutput(t, Ith(y,1), Ith(y,2), Ith(y,3));

      //printf("MH: %d %f",iout,t_next);


      if (check_flag(&flag, "CVode", 1)) break;
     //assert(flag==CV_SUCCESS);
    }












    // Write to file:
    fclose(fp);


    // SHUTDOWN CVODE:
    // ------------------
  /* Free y and abstol vectors */
      N_VDestroy_Serial(y);
      N_VDestroy_Serial(abstol);

      /* Free integrator memory */
      CVodeFree(&cvode_mem);





    printf("\nFinished evaluatinge EvtBlock: ${ev_blk_index}\n\n");
}
// (End Event Block Evaluation: ${ev_blk_index} )
// ============================

"""

from neurounits.visitors import ASTVisitorBase

class VariableSrcs:
    PreCalculated = 'PreCalculated'
    InProgress = 'InProgress'

class TriggerConditionGenerator(ASTVisitorBase):
    def __init__(self, variable_srcs, evt_blk, cpp_builddata):
        self.variable_srcs = variable_srcs
        self.evt_blk = evt_blk
        self.cpp_builddata = cpp_builddata

    def VisitInEquality(self, o, **kwargs):
        return '(%s) - (%s)'  % ( self.visit(o.lesser_than), self.visit(o.greater_than) )


    def VisitStateVariable(self, o, **kwargs):
        if self.variable_srcs[o] == VariableSrcs.PreCalculated:
            fname = "get_%s"%( o.symbol.replace("/","__") )
            return 'pDS->data_mgr.%s(t)' % fname
        if self.variable_srcs[o] == VariableSrcs.InProgress:
            print self.evt_blk
            index = self.cpp_builddata.sv_index_by_evt_blk[self.evt_blk][o]
            return "NV_Ith_S(y, %d)" %(index)

    def VisitSymbolicConstant(self, o, **kwargs):
        return '%f' % o.value.float_in_si()
    def VisitConstant(self, o, **kwargs):
        return '%f' % o.value.float_in_si()

    def VisitAddOp(self, o, **kwargs):
        return ' ( %s + %s ) ' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitSuppliedValue(self, o, **kwargs):
        if(o.symbol=='t'):
            return 't'
        else:
            assert False


class StateAssigmentGenerator(TriggerConditionGenerator):
    pass





class FuncDef(object):
    def __init__(self, name, signature, body):
        self.name=name
        self.body=body
        self.signature = signature


class CPPBuildData(object):
    def __init__(self, component, ev_blks):
        self.component = component
        self.ev_blks = ev_blks

        self.sv_index_by_evt_blk = None
        self.tr_index_by_evt_blk = None
        self.func_def_tr_triggers = None
        self.rt_graph_trigger_map = None

        #
        self.build_sv_index_by_evt_blk()
        self.build_tr_index_by_evt_blk()
        self.build_transition_trigger_functions()
        self.build_rt_to_transition_map()


    # Naming things in the CPP file:
    def rt_graph_name(self, rt_graph):
        if rt_graph.name[-1] == '/':
            return rt_graph.name.replace("/","__")[:-2]
        else:
            return rt_graph.name.replace("/","__")
    def rt_graph_regimes(self, rt_graph):
        return [reg for reg in rt_graph.regimes if reg.name is not None]
    def regime_name(self, regime):
        return self.rt_graph_name(regime.parent_rt_graph) + "_" + regime.name.replace("/","__")


    def state_variable_updates_for_transition(self, tr):
        sas = []
        for a in tr.actions:
            if isinstance(a, ast.OnEventStateAssignment):
                evt_blk_transition = self.get_evt_blk_which_solves( tr.rt_graph )
                srcs = self.get_variable_srcs_dict(evt_blk_transition)
                gen = StateAssigmentGenerator( variable_srcs=srcs, evt_blk=evt_blk_transition, cpp_builddata=self)
                sas.append((a, gen))
        return sas



    def build_tr_index_by_evt_blk(self):
        self.tr_index_by_evt_blk = dict()
        for evt_blk in self.ev_blks:
            self.tr_index_by_evt_blk[evt_blk] = {}
            print 'For evt_block:', repr(evt_blk)
            trs = [tr for tr in self.component._transitions_conditiontriggers if tr.rt_graph in evt_blk.rt_graphs]
            for i,tr in enumerate(trs):
                self.tr_index_by_evt_blk[evt_blk][tr] = i

    def build_sv_index_by_evt_blk(self):
        self.sv_index_by_evt_blk = defaultdict(dict)
        for evt_blk in self.ev_blks:
            print 'For evt_block:', repr(evt_blk)
            for i,state_variable in enumerate(evt_blk.state_variables):
                print '  SV index for: %s is %d' % (repr(state_variable), i)
                self.sv_index_by_evt_blk[evt_blk][state_variable] = i





    def build_rt_to_transition_map(self):
        self.rt_graph_trigger_map = defaultdict(list)
        for tr in self.component._transitions_conditiontriggers:
            self.rt_graph_trigger_map[tr.rt_graph].append(tr)


    def get_evt_blk_which_solves(self, obj):
        assert isinstance(obj, (ast.StateVariable, ast.AssignedVariable, ast.RTBlock))
        ev_blks = [ev_blk for ev_blk in self.ev_blks if obj in ev_blk.objects]
        assert len(ev_blks) == 1
        return ev_blks[0]


    def get_variable_srcs_dict(self,evt_blk):
            srcs = {}
            for sv in self.component.state_variables + self.component.assignedvalues:
                if self.get_evt_blk_which_solves(sv) == evt_blk:
                    srcs[sv] = VariableSrcs.InProgress
                else:
                    srcs[sv] = VariableSrcs.PreCalculated
            return srcs



    def build_transition_trigger_functions(self):




        self.func_def_tr_triggers = {}
        for i,tr in enumerate(self.component._transitions_conditiontriggers):

            # Which event block solves this transition:
            evt_blk_transition = self.get_evt_blk_which_solves( tr.rt_graph )

            # Build the dictionary, telling us where state variables come from:
            srcs = self.get_variable_srcs_dict(evt_blk = evt_blk_transition)
            #srcs = {}
            #for sv in self.component.state_variables + self.component.assignedvalues:
            #    if self.get_evt_blk_which_solves(sv) == evt_blk_transition:
            #        srcs[sv] = VariableSrcs.InProgress
            #    else:
            #        srcs[sv] = VariableSrcs.PreCalculated



            tr_gen = TriggerConditionGenerator(variable_srcs=srcs, evt_blk=evt_blk_transition, cpp_builddata=self )


            # OK, where do we get the value from? are they calculated in this funciton, or were they calculated before?
            name='func_trig_%d'%i


            l1 = """DataStore* pDS = (DataStore*) user_data;"""
            l2 = 'return ' + tr_gen.visit(tr.trigger) + ';'
            body = "\n".join( [l1 , l2 ] )
            fn = FuncDef(name=name,
                         signature ="float %s (realtype t, N_Vector y, realtype *gout,void *user_data)" %name,
                         body=body )
            self.func_def_tr_triggers[tr] = fn




def build_code_for_ev_blk(component, ev_blk, ev_blk_index, build_data):
    func_name = "evaluate_event_block_%d" % (ev_blk_index)  #${ev_blk_index}
    mytemplate = Template(ev_blk_function)
    buf = StringIO()
    ctx = Context(buf, ev_blk_index=ev_blk_index, ev_blk=ev_blk, component=component, bd=build_data)
    mytemplate.render_context(ctx)
    res = buf.getvalue() + ('\n' * 3)
    return res, func_name


def build_simulation(component):
    print 'C++ Simulation'
    print 'Component', component

    ev_blks = utils.separate_integration_blocks(component)
    build_data = CPPBuildData(component, ev_blks)

    print ev_blks


    op_blks= ''
    func_names = []
    for i, ev_blk in enumerate(ev_blks):
        blk, func_name = build_code_for_ev_blk(component=component, ev_blk=ev_blk, ev_blk_index=i, build_data=build_data)
        op_blks = op_blks + blk
        func_names.append(func_name)


    mytemplate = Template(solver_function)
    buf = StringIO()
    ctx = Context(buf, ev_blk_func_names=func_names, component=component)

    mytemplate.render_context(ctx)
    res = buf.getvalue() + ('\n' * 3)

    data_mgr_txt = DataMgrBuilder(ev_blks=ev_blks, cpp_builddata=build_data, component=component).get_text()


    op_file = 'out1.c'
    with open(op_file,'w') as fout:
        fout.write(header1)
        fout.write(data_mgr_txt)
        fout.write(header2)
        fout.write(op_blks)
        fout.write(res)

    print 'File written to:', op_file
    print



    print
    print
    #mytemplate = Template("hello world!")
    #print mytemplate.render()



    assert False











def simulate( component, times ):
    build_simulation(component)

    #print 'Python Simulation'
    #print 'Component', component

    #ev_blks = utils.separate_integration_blocks(component)





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
        if sym == 'o2/nrn/syn_excit/i':
            plt.plot( datastore.time_pts, d.data, 'x-', label=d.variable.symbol)
            plt.legend()

    plt.figure()
    for d in datastore.traces.values():
        print d.variable.symbol, np.min(d.data), np.max(d.data)
        sym = d.variable.symbol
        if sym == 'o2/nrn/syn_excit/A':
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
