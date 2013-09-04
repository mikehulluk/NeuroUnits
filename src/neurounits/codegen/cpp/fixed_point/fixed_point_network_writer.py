


import mako
from mako.template import Template

#import subprocess
#from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np

import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from mako import exceptions
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator




c_prog_header_tmpl = r"""



//#define _GLIBCXX_DEBUG true

/* Set or unset this variable: */

#ifndef ON_NIOS
#define ON_NIOS false
#endif
#define DISPLAY_LOOP_INFO true



#include "basic_types.h"





#define PC_DEBUG  false




//#define ON_NIOS

#if ON_NIOS
#define CALCULATE_FLOAT false
#define USE_HDF false
#define SAVE_HDF5_FLOAT false
#define SAVE_HDF5_INT false
#define SAFEINT true

#else


#if PC_DEBUG
#define CALCULATE_FLOAT true
#define USE_HDF true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT false
#define SAFEINT true

#else
#define CALCULATE_FLOAT false
#define USE_HDF true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT false
#define SAFEINT false
#endif // (PC_DEBUG)



#endif





//#define NSIM_REPS 200




/* ------- General  ----------- */
#define CHECK_INT_FLOAT_COMPARISON true
#define CHECK_INT_FLOAT_COMPARISON_FOR_EXP false

const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT = 100;
const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT_FOR_EXP = 300;

const int nsim_steps = ${nsim_steps};


// Define how often to record values:
const int record_rate = 100;


const int n_results_total = nsim_steps / record_rate;
int n_results_written = 0;




#include <list>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <iomanip>
#include <sstream>
#include <assert.h>
#include <climits>
#include <stdint.h>

// Headers to use when we are not on the NIOS:
#if ON_NIOS
#else
#include <boost/format.hpp>
#include <cinttypes>
#include <fenv.h>
#include <gmpxx.h>
#endif




#if USE_HDF
#include <unordered_map>
// For Saving the data to HDF5:
#include "hdfjive.h"
const string output_filename = "${output_filename}";

// Data types used for storing in HDF5:
const hid_t hdf5_type_int = H5T_NATIVE_INT;
const hid_t hdf5_type_float = H5T_NATIVE_DOUBLE;

typedef int T_hdf5_type_int;
typedef double T_hdf5_type_float;
#endif






#include "float_utils.h"
const int VAR_NBITS = ${nbits};
typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
using mh::auto_shift;
using mh::auto_shift64;










#if SAFEINT
#include "safe_int.h"
#include "safe_int_utils.h"
#endif


#include "safe_int_proxying.h"
#include "lut.h"





struct LookUpTables
{
    LookUpTables()
        : exponential(5, 4)    // (nbits, upscale)
        //: exponential(5, 3)    // (nbits, upscale)
    { }

    LookUpTableExpPower2<VAR_NBITS, IntType> exponential;
};



LookUpTables lookuptables;




#include "fixed_point_operations.h"

inline IntType do_add_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
    return tmpl_fp_ops::do_add_op(v1, up1, v2, up2, up_local, expr_id);
}
inline IntType do_sub_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
   return tmpl_fp_ops::do_sub_op(v1, up1, v2, up2, up_local, expr_id);
}

inline IntType do_mul_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
    return tmpl_fp_ops::do_mul_op(v1, up1, v2, up2, up_local, expr_id);
}

inline IntType do_div_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
    return tmpl_fp_ops::do_div_op(v1, up1, v2, up2, up_local, expr_id);
}

inline IntType int_exp(IntType v1, IntType up1, IntType up_local, IntType expr_id) {
    return tmpl_fp_ops::int_exp(v1, up1, up_local, expr_id, lookuptables.exponential);
}



const IntType dt_int = IntType(${dt_int});
const IntType dt_upscale = IntType(${dt_upscale});
const IntType time_upscale = IntType(${time_upscale});

struct TimeInfo
{
    const IntType time_step;
    const IntType time_int;
    TimeInfo(IntType time_step)
        : time_step(time_step), time_int( inttype32_from_inttype64<IntType>( auto_shift64( get_value64(dt_int) * get_value64(time_step), get_value64(dt_upscale- time_upscale) )) )
    {

    }

};




struct SpikeEmission
{
    const IntType time;
    SpikeEmission(const IntType& time) : time(time) {}
};

void record_event(IntType global_buffer, const SpikeEmission& evt );








namespace rnd
{

    double rand_in_range(double min, double max)
    {
        double r = (double)rand() / INT_MAX;
        return r * (max-min) + min;
    }

    IntType uniform(IntType up, IntType min, IntType min_scale, IntType max, IntType max_scale)
    {
        return IntType( FixedFloatConversion::from_float(
            rand_in_range(FixedFloatConversion::to_float(min, min_scale), FixedFloatConversion::to_float(max, max_scale)),
            up) );

        //return IntType(1);
    }
}




IntType check_in_range(IntType val, IntType upscale, double min, double max, const std::string& description)
{
    //cout << "\n";
    //cout << "\nFor: " << description;
    //cout << "\n Checking: " << std::flush;
    double value_float = FixedFloatConversion::to_float(val, upscale);


    //double diff_max = max-value_float;
    //double diff_min = min-value_float;
    //cout << "\n diff_max: " << diff_max;
    //cout << "\n diff_min: " << diff_min;

    // Addsmall tolerance, to account for constants:
    if(max > 0) max *= 1.01;
    else max /= 1.01;
    if(min < 0) min *= 1.01;
    else min /= 1.01;




    if(!( value_float <= max))
    {
        cout << "\ncheck_in_range: (min):" << min << std::flush;
        cout << "\ncheck_in_range: (max):" << max << std::flush;

        double pc_out = (value_float - max) / (max-min) * 100.;

        if(pc_out > 1)
        {
            cout << "\n\nOverflow on:" << description;
            cout << "\nvalue_float= " << value_float << " between(" << min << "," << max << ")?" << std::flush;
            cout << "\n  --> Amount out: " << pc_out << "%";
            cout << "\n";

            //assert(0);

        }

    }
    if( !( value_float >= min || min >0))
    {

        cout << "\ncheck_in_range: (min):" << min  << std::flush;
        cout << "\ncheck_in_range: (max):" << max  << std::flush;

        double pc_out = (min - value_float) / (max-min) * 100.;

        if(pc_out > 1)
        {
            cout << "\n\nOverflow on:" << description;
            cout << "\nvalue_float= " << value_float << " between(" << min << "," << max << ")?" << std::flush;
            cout << "\n  --> Amount out: " << pc_out << "%";
            cout << "\n";
            //assert(0);
        }
    }

    //cout << "\nOK!";
    return val;
}









// Declarations:
%for projection in network.event_port_connectors:
// Event Coupling:
namespace NS_eventcoupling_${projection.name}
{
    void dispatch_event(IntType src_neuron);
}
%endfor

"""



c_population_details_tmpl = r"""



namespace NS_${population.name}
{





    // Input event types:
    namespace input_event_types
    {
    %for in_port in population.component.input_event_port_lut:
        struct Event_${in_port.symbol}
        {

            %for param in in_port.parameters:
            IntType ${param.symbol};
            %endfor
            IntType delivery_time;

            Event_${in_port.symbol}(
                IntType delivery_time
                %for param in in_port.parameters:
                , IntType ${param.symbol},
                %endfor
            )
            :
              %for param in in_port.parameters:
              ${param.symbol}(${param.symbol}),
              %endfor
              delivery_time(delivery_time)
            { }


        };
    %endfor
    }




// Define the data-structures:
struct NrnPopData
{
    static const int size = ${population.get_size()};

    // Parameters:
% for p in population.component.parameters:
    IntType ${p.symbol}[size];      // Upscale: ${p.annotations['fixed-point-format'].upscale}
% endfor

    // Assignments:
% for ass in population.component.assignedvalues:
    IntType ${ass.symbol}[size];      // Upscale: ${ass.annotations['fixed-point-format'].upscale}
% endfor

    // States:
% for sv_def in population.component.state_variables:
    IntType ${sv_def.symbol}[size];    // Upscale: ${sv_def.annotations['fixed-point-format'].upscale}
    IntType d_${sv_def.symbol}[size];
% endfor


    // Supplied:
% for sv_def in population.component.suppliedvalues:
% if sv_def.symbol != 't':
    IntType ${sv_def.symbol}[size];    // Upscale: ${sv_def.annotations['fixed-point-format'].upscale}
% endif
% endfor


    // Random Variable nodes
%for rv, _pstring in rv_per_population:
    IntType RV${rv.annotations['node-id']};
%endfor
%for rv, _pstring in rv_per_neuron:
    IntType RV${rv.annotations['node-id']}[size];
%endfor


    // Regimes:
    %for rtgraph in population.component.rt_graphs:
    %if len(rtgraph.regimes) > 1:
    enum RegimeType${rtgraph.name} {
    %for regime in rtgraph.regimes:
        ${rtgraph.name}${regime.name},
    %endfor
        NO_CHANGE
    };
    RegimeType${rtgraph.name} current_regime_${rtgraph.name}[size];
    %endif
    %endfor


    // Incoming event queues:
    %for in_port in population.component.input_event_port_lut:
    typedef std::list<input_event_types::Event_${in_port.symbol}>  EventQueueType_${in_port.symbol};
    EventQueueType_${in_port.symbol} incoming_events_${in_port.symbol}[size];
    %endfor

};



void set_supplied_values_to_zero(NrnPopData& d)
{
% for sv_def in population.component.suppliedvalues:
    % if sv_def.symbol != 't':
    for(int i=0;i<NrnPopData::size;i++) d.${sv_def.symbol}[i] = IntType(0);
    % endif
% endfor
}





void initialise_randomvariables(NrnPopData& d)
{
    // Random Variable nodes
    %for rv, rv_param_string in rv_per_population:
    d.RV${rv.annotations['node-id']} = rnd::${rv.functionname}(IntType(${rv.annotations['fixed-point-format'].upscale}), ${rv_param_string});
    %endfor

    for(int i=0;i<NrnPopData::size;i++)
    {
        %for rv, rv_param_string in rv_per_neuron:
        d.RV${rv.annotations['node-id']}[i] = rnd::${rv.functionname}( IntType(${rv.annotations['fixed-point-format'].upscale}), ${rv_param_string});
        %endfor
    }
}





void initialise_statevars(NrnPopData& d)
{
    for(int i=0;i<NrnPopData::size;i++)
    {
        % for sv_def in population.component.state_variables:
        d.${sv_def.symbol}[i] = auto_shift( IntType(${sv_def.initial_value.annotations['fixed-point-format'].const_value_as_int}),  IntType(${sv_def.initial_value.annotations['fixed-point-format'].upscale} - ${sv_def.annotations['fixed-point-format'].upscale} ) );
        % endfor

        // Initial regimes:
        %for rtgraph in population.component.rt_graphs:
        %if len(rtgraph.regimes) > 1:
        d.current_regime_${rtgraph.name}[i] = NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${rtgraph.default_regime.name};;
        %endif
        %endfor
    }



}



namespace event_handlers
{
%for out_event_port in population.component.output_event_port_lut:

    //Events emitted from: ${population.name}
    void on_${out_event_port.symbol}(IntType index, const TimeInfo& time_info /*Params*/)
    {
        //std::cout << "\n on_${out_event_port.symbol}: " <<  index;

        %if (population,out_event_port) in evt_src_to_evtportconns:
        %for conn in evt_src_to_evtportconns[(population,out_event_port)]:
        // Via ${conn.name} -> ${conn.dst_population.name}
        NS_eventcoupling_${conn.name}::dispatch_event(index);
        %endfor
        %endif


        //And lets see what to record from these:
        %for poprec in network.all_output_event_recordings:
        %if poprec.src_population == population:
        // Lets records!
        if( (index >= ${poprec.src_pop_start_index}) && (index < ${poprec.src_pop_end_index}))
        {
            record_event( ${poprec.global_offset} + index - ${poprec.src_pop_start_index} , SpikeEmission(time_info.time_int) );
        }
        %endif
        %endfor

    }
%endfor
}







## Template functions:
## ===================
<%def name="trigger_transition_block(tr, rtgraph)">
            if(${writer.to_c(tr.trigger)})
            {
                // Actions ...
                %for action in tr.actions:
                ${writer.to_c(action)};
                %endfor

                // Switch regime?
                %if tr.changes_regime():
                if(next_regime != NrnPopData::RegimeType${rtgraph.name}::NO_CHANGE &&
                   next_regime != NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${tr.target_regime.name})
                {
                    assert(0); //Multiple transitions detected.
                }
                next_regime = NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${tr.target_regime.name};
                %endif
            }
</%def>







<%def name="trigger_event_block(tr, rtgraph)">
            while(true)
            {
                if( d.incoming_events_${tr.port.symbol}[i].size() == 0 ) break;
                IntType evt_time = d.incoming_events_${tr.port.symbol}[i].front().delivery_time;
                if(evt_time < time_info.time_int )
                {
                    // Handle the event:
                    //std::cout << "\n **** HANDLING EVENT (on ${tr.port.symbol}) *****";

                     // Actions ...
                    %for action in tr.actions:
                    ${writer.to_c(action)};
                    %endfor

                    // Switch regime?
                    %if tr.changes_regime():
                    if(next_regime != NrnPopData::RegimeType${rtgraph.name}::NO_CHANGE &&
                       next_regime != NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${tr.target_regime.name})
                    {
                        assert(0); //Multiple transitions detected.
                    }
                    next_regime = NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${tr.target_regime.name};
                    %endif

                    d.incoming_events_${tr.port.symbol}[i].pop_front();
                }
                else
                {
                    cout << "\nEvents to handle, but delivery time not yet met: " << evt_time << " Now:" << time_info.time_int;
                    break;
                }
            }
</%def>











// Update-function
void sim_step(NrnPopData& d, TimeInfo time_info)
{

    const IntType t = time_info.time_int;

//#pragma omp parallel for default(shared) 
    for(int i=0;i<NrnPopData::size;i++)
    {
        //cout << "\n";
        //cout << "\nFor ${population.name} " << i;
        //cout << "\nStarting State Variables:";
        //cout << "\n-------------------------";
        //// Calculate delta's for all state-variables:
        % for eqn in eqns_timederivatives:
        //cout << "\n d.${eqn.node.lhs.symbol}: " << d.${eqn.node.lhs.symbol}[i]  << " (" << FixedFloatConversion::to_float(d.${eqn.node.lhs.symbol}[i], ${eqn.node.lhs.annotations['fixed-point-format'].upscale})  << ")" << std::flush;
        % endfor
        //cout << "\nUpdates:";

        // Calculate assignments:
        % for eqn in eqns_assignments:
        d.${eqn.node.lhs.symbol}[i] = ${eqn.rhs_cstr} ;
        //cout << "\n d.${eqn.node.lhs.symbol}: " << d.${eqn.node.lhs.symbol}[i]  << " (" << FixedFloatConversion::to_float(d.${eqn.node.lhs.symbol}[i], ${eqn.node.lhs.annotations['fixed-point-format'].upscale})  << ")" << std::flush;
        % endfor

        // Calculate delta's for all state-variables:
        % for eqn in eqns_timederivatives:
        IntType d_${eqn.node.lhs.symbol} = ${eqn.rhs_cstr[0]} ;
        d.${eqn.node.lhs.symbol}[i] = d.${eqn.node.lhs.symbol}[i] + ${eqn.rhs_cstr[1]} ;
        //cout << "\n d.${eqn.node.lhs.symbol}: " << d.${eqn.node.lhs.symbol}[i]  << " (" << FixedFloatConversion::to_float(d.${eqn.node.lhs.symbol}[i], ${eqn.node.lhs.annotations['fixed-point-format'].upscale})  << ")" << std::flush;
        % endfor
    }




    for(int i=0;i<NrnPopData::size;i++)
    {
    // Resolve transitions for each rt-graph:
    %for rtgraph in population.component.rt_graphs:


        %if len(rtgraph.regimes) > 1:
        
        NrnPopData::RegimeType${rtgraph.name} next_regime = NrnPopData::RegimeType${rtgraph.name}::NO_CHANGE;

        // Non-trivial RT-graph
        switch(d.current_regime_${rtgraph.name}[get_value32(i)])
        {
        case NrnPopData::RegimeType${rtgraph.name}::NO_CHANGE:
            assert(0); // This is an internal error - this regime is only used as a flag internally.

        // Handle the transitions per regime:
        %for regime in rtgraph.regimes:
        case NrnPopData::RegimeType${rtgraph.name}::${rtgraph.name}${regime.name}:
            % if len(rtgraph.regimes) > 1 and regime.name is None:
            assert(0); // Should not be here - we should switch into a 'real' regime before we begin
            %endif

            // ==== Triggered Transitions: ====
            %for tr in population.component.triggertransitions_from_regime(regime):
            ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
            %endfor

            // ==== Event Transitions: ====
            %for tr in population.component.eventtransitions_from_regime(regime):
            ${trigger_event_block(tr, rtgraph)}
            %endfor

            break;
        %endfor

        }

        // And the transitions from the 'global namespace':
        // ==== Triggered Transitions: ====
        %for tr in population.component.triggertransitions_from_regime(rtgraph.get_regime(None)):
        ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
        %endfor

        // ==== Event Transitions: ====
        %for tr in population.component.eventtransitions_from_regime(rtgraph.get_regime(None)):
        ${trigger_event_block(tr, rtgraph)}
        %endfor




        %else:
            // And the transitions from the 'global namespace':
            // ==== Triggered Transitions: ====
            %for tr in population.component.triggertransitions_from_regime(rtgraph.get_regime(None)):
            ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
            %endfor

            // ==== Event Transitions: ====
            %for tr in population.component.eventtransitions_from_regime(rtgraph.get_regime(None)):
            ${trigger_event_block(tr, rtgraph)}
            %endfor
            
        %endif:

        // Update the next state:
        %if len(rtgraph.regimes) > 1:

        if( next_regime != NrnPopData::RegimeType${rtgraph.name}::NO_CHANGE)
        {
            ##cout << "\nSWitching into Regime:" << next_regime;
            d.current_regime_${rtgraph.name}[i] = next_regime;
        }
        %endif
    %endfor
    }
}





void print_results_from_NIOS(NrnPopData* d)
{
    // Assignments + states:
    % for ass in population.component.assignedvalues + population.component.state_variables:
    cout << "\n#!DATA{ 'name':'${ass.symbol}' } {'size': ${nsim_steps},  'fixed_point': {'upscale':${ass.annotations['fixed-point-format'].upscale}, 'nbits':${nbits}} } [";
    for(IntType i=IntType(0);i<nsim_steps;i++) cout << d[ get_value32(i)].${ass.symbol} << " ";
    cout << "]\n";
    % endfor
    cout << "\n#! FINISHED\n";
}




} // End of population namespace

"""














c_main_loop_tmpl = r"""



#include <ctime>

int main()
{

    // Start the clock:
    clock_t begin_main = clock();


    // Enable floating point exception trapping:
    //feenableexcept(-1);
    #if !ON_NIOS
    feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    #endif //!ON_NIOS


    // Setup the variables:
    %for pop in network.populations:
    NS_${pop.name}::initialise_statevars(data_${pop.name});
    NS_${pop.name}::initialise_randomvariables(data_${pop.name});
    %endfor

    // Setup the electical coupling:
    %for proj in network.electrical_synapse_projections:
    NS_${proj.name}::setup_electrical_coupling();
    %endfor

    // Setup the event connections:
    %for evt_conn in network.event_port_connectors:
    NS_eventcoupling_${evt_conn.name}::setup_connections();
    %endfor






    clock_t begin_sim = clock();


    #if NSIM_REPS
    for(int k=0;k<NSIM_REPS;k++)
    {
        if(k%100==0) cout << "Loop: " << k << "\n" << flush;
    #endif

        n_results_written=0;
        for(IntType time_step=IntType(0);time_step<nsim_steps;time_step++)
        {

            TimeInfo time_info(time_step);
            //cout << "\n\nTIME:" << time_step << "\n";



            #if DISPLAY_LOOP_INFO
            if(get_value32(time_step)%100 == 0)
            {
                std::cout << "Loop: " << time_step << "\n";
                std::cout << "t: " << time_info.time_int << "\n";
                std::cout << "(t: " << FixedFloatConversion::to_float(time_info.time_int, time_upscale) * 1000 << "ms)\n";
            }
            #endif


            // 0. Reset the injected currents:
            %for pop in network.populations:
            NS_${pop.name}::set_supplied_values_to_zero(data_${pop.name});
            %endfor



            // A. Electrical coupling:
            %for proj in network.electrical_synapse_projections:
            NS_${proj.name}::calculate_electrical_coupling( data_${proj.src_population.population.name}, data_${proj.dst_population.population.name} );
            %endfor



            // B. Integrate all the state_variables of all the neurons:
            %for pop in network.populations:
            NS_${pop.name}::sim_step( data_${pop.name}, time_info);
            %endfor




            // C. Save the recorded values:
            if(get_value32(time_info.time_step) % get_value32(record_rate)==0)
            {
                // Save time:
                global_data.recordings_new.time_buffer[n_results_written] = get_value32(time_info.time_int);
                //write_time_to_hdf5(time_info);
                %for poprec in network.all_trace_recordings:
                // Record: ${poprec}
                for(int i=0;i<${poprec.size};i++) global_data.recordings_new.data_buffers[n_results_written][${poprec.global_offset}+i] = data_${poprec.src_population.name}.${poprec.node.symbol}[i + ${poprec.src_pop_start_index} ];
                %endfor

                n_results_written++;
            }


        }

    #if NSIM_REPS
    }
    #endif


    clock_t end_sim = clock();


    // Dump to HDF5
    cout << "\nWriting HDF5 output" << std::flush;
    global_data.recordings_new.write_all_traces_to_hdf();
    global_data.recordings_new.write_all_output_events_to_hdf();


    #if ON_NIOS
    %for pop in network.populations:
    ##NS_${pop.name}::print_results_from_NIOS(global_data.recordings.${pop.name}_recorded_output_data_OLD);
    %endfor
    #endif


    clock_t end_data_write = clock();


    printf("Simulation Complete\n");

    double elapsed_secs_total = double(end_data_write - begin_main) / CLOCKS_PER_SEC;
    double elapsed_secs_sim = double(end_sim - begin_sim) / CLOCKS_PER_SEC;
    double elapsed_secs_hdf = double(end_data_write - end_sim) / CLOCKS_PER_SEC;
    double elapsed_secs_setup = double(begin_sim - begin_main) / CLOCKS_PER_SEC;

    cout << "\nTime taken (setup):" << elapsed_secs_setup;
    cout << "\nTime taken (sim-total):"<< elapsed_secs_sim;
    cout << "\nTime taken (hdf):"<< elapsed_secs_hdf;
    cout << "\nTime taken (combined):"<< elapsed_secs_total;

}




"""









c_electrical_projection_tmpl = r"""

// Electrical Coupling

namespace NS_${projection.name}
{


    struct GapJunction
    {
        IntType i,j;
        IntType strength;

        GapJunction(IntType i, IntType j, IntType strength)
         : i(i), j(j), strength(strength)
        {


        }

    };



    typedef std::vector<GapJunction>  GJList;
    GJList gap_junctions;


    void setup_electrical_coupling()
    {

        ${projection.connector.build_c( src_pop_size_expr=projection.src_population.get_size(),
                                        dst_pop_size_expr=projection.dst_population.get_size(),
                                        add_connection_functor=lambda i,j: "gap_junctions.push_back( GapJunction(IntType(%s), IntType(%s), IntType(%s)) );" % (i,j, projection.strength_ohm),
                                        add_connection_set_functor=None
                                        ) }
    }

    void calculate_electrical_coupling( NS_${projection.src_population.population.name}::NrnPopData& src, NS_${projection.dst_population.population.name}::NrnPopData& dst)
    {
        <%
        pre_V_node = projection.src_population.component.get_terminal_obj_or_port('V')
        post_V_node = projection.dst_population.component.get_terminal_obj_or_port('V')
        pre_iinj_node = projection.src_population.component.get_terminal_obj_or_port(projection.injected_port_name)
        post_iinj_node = projection.dst_population.component.get_terminal_obj_or_port(projection.injected_port_name)
        %>
        IntType upscale_V_pre = IntType( ${pre_V_node.annotations['fixed-point-format'].upscale} );
        IntType upscale_V_post = IntType(${pre_V_node.annotations['fixed-point-format'].upscale} );

        IntType upscale_iinj_pre = IntType(${pre_iinj_node.annotations['fixed-point-format'].upscale} );
        IntType upscale_iinj_post = IntType(${post_iinj_node.annotations['fixed-point-format'].upscale} );

        for(GJList::iterator it = gap_junctions.begin(); it != gap_junctions.end();it++)
        {
            double V_float_pre  = FixedFloatConversion::to_float( src.V[get_value32(it->i)], upscale_V_pre);
            double V_float_post = FixedFloatConversion::to_float( dst.V[get_value32(it->j)], upscale_V_post);
            double i_fl = (V_float_post - V_float_pre) / ${projection.strength_ohm};
            src.${post_iinj_node.symbol}[get_value32(it->i)] = src.${post_iinj_node.symbol}[get_value32(it->i)] + FixedFloatConversion::from_float(i_fl, upscale_iinj_pre);
            src.${post_iinj_node.symbol}[get_value32(it->j)] = src.${post_iinj_node.symbol}[get_value32(it->j)] + FixedFloatConversion::from_float(-i_fl, upscale_iinj_post);
        }
    }
}


"""



c_event_projection_tmpl = r"""

// Event Coupling:
namespace NS_eventcoupling_${projection.name}
{

    typedef std::vector<IntType> TargetList;
    TargetList projections[${projection.src_population.get_size()}];


    void setup_connections()
    {

        ${projection.connector.build_c( src_pop_size_expr=projection.src_population.get_size(),
                                        dst_pop_size_expr=projection.dst_population.get_size(),
                                        add_connection_functor=lambda i,j: "projections[get_value32(%s)].push_back(%s)" % (i,j),
                                        add_connection_set_functor=None
                                        ) }

        size_t n_connections = 0;
        for(size_t i=0;i<${projection.src_population.get_size()};i++) n_connections+= projections[i].size();
        cout << "\n Projection: ${projection.name} contains: " << n_connections << std::flush;
    }


    // This is the neuron index inside the whole population, so lets check its for us and dispatch if so:
    void dispatch_event(IntType src_neuron)
    {
        //cout << "\nDispatch_event: " << src_neuron;
        //cout << "\nDelivering to:";
        if( src_neuron < ${projection.src_population.start_index} || src_neuron >= ${projection.src_population.end_index} )
            return;
        


        TargetList& targets = projections[get_value32(src_neuron - ${projection.src_population.start_index} )];
        for( TargetList::iterator it = targets.begin(); it!=targets.end();it++)
        {
            //IntType target_index = (*it);
            //cout << " " << target_index;

            NS_${projection.dst_population.population.name}::input_event_types::Event_${projection.dst_port.symbol} evt(IntType(0));

            
            int tgt_nrn_index = get_value32(*it) + ${projection.dst_population.start_index};

            data_${projection.dst_population.population.name}.incoming_events_${projection.dst_port.symbol}[tgt_nrn_index].push_back( evt ) ;
            //cout << "\nDelivered event to: " << (tgt_nrn_index);
        }


    }


}


"""


popl_obj_tmpl = r"""

// Setup the global variables:
%for pop in network.populations:
NS_${pop.name}::NrnPopData data_${pop.name};
%endfor




struct RecordingMgr
{
    // Old storage:
    %for pop in network.populations:
    NS_${pop.name}::NrnPopData* ${pop.name}_recorded_output_data_OLD;
    %endfor

    RecordingMgr()
    {
    %for pop in network.populations:
        ${pop.name}_recorded_output_data_OLD = new NS_${pop.name}::NrnPopData[n_results_total];
    %endfor
    }

    ~RecordingMgr()
    {
        %for pop in network.populations:
        delete[] ${pop.name}_recorded_output_data_OLD;
        %endfor
    }
};




























struct RecordMgrNew
{
    static const int buffer_size = n_results_total;

    // What are we recording:
    %for poprec in network.all_trace_recordings:
    // Record: ${poprec}
    %endfor
    static const int n_rec_buffers = ${network.n_trace_recording_buffers};

    // Allocate the storage for the traces:
    IntType time_buffer[buffer_size];
    IntType data_buffers[buffer_size][n_rec_buffers];


    // Allocate space for the spikes:
    typedef  list<SpikeEmission> SpikeList;
    SpikeList emitted_spikes[ ${network.n_output_event_recording_buffers} ];



    void write_all_output_events_to_hdf()
    {

        %if network.all_output_event_recordings:
        cout << "\n\nWriting spikes to HDF5";
        HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
        //const T_hdf5_type_float dt_float = FixedFloatConversion::to_float(dt_int, dt_upscale);
        const T_hdf5_type_float dt_float = FixedFloatConversion::to_float(1, time_upscale);
        %endif


        %for i,poprec in enumerate(network.all_output_event_recordings):


        for(int i=0; i< ${poprec.size};i++)
        {
            const int buffer_offset = ${poprec.global_offset}+i;
            int nrn_offset = i + ${poprec.src_pop_start_index};
            const int nspikes = emitted_spikes[buffer_offset].size();
            //cout << "\nSpikes:"  << nspikes;
            int buffer_int[nspikes];
            double buffer_float[nspikes];
            int s=0;
            for(SpikeList::iterator it=emitted_spikes[buffer_offset].begin(); it!=emitted_spikes[buffer_offset].end(); it++,s++) 
            {
                buffer_int[s] = it->time;
                buffer_float[s] = buffer_int[s] * dt_float;
            } 


            
            string tag_string = "EVENT:${poprec.node.symbol},SRCPOP:${poprec.src_population.name},${','.join(poprec.tags)}";
            string tag_string_index = (boost::format("POPINDEX:%04d")%nrn_offset).str();
            

            #if SAVE_HDF5_INT
            string location_int =  (boost::format("simulation_fixed/int/${poprec.src_population.name}/%04d/output_events/")%nrn_offset).str();
            HDF5GroupPtr pGroup_int = file->get_group(location_int + "${poprec.node.symbol}");
            HDF5DataSet2DStdPtr event_output_int  = pGroup_int->create_dataset("${poprec.node.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
            if(nspikes>0) event_output_int->set_data(nspikes, 1, buffer_int);
            
            pGroup_int->add_attribute("hdf-jive","events");
            pGroup_int->add_attribute("hdf-jive:tags",string("fixed-int,") + tag_string + "," + tag_string_index);
            
            #endif

            #if SAVE_HDF5_FLOAT
            string location_float =  (boost::format("simulation_fixed/double/${poprec.src_population.name}/%04d/output_events/")%nrn_offset).str();
            HDF5GroupPtr pGroup_float = file->get_group(location_float + "${poprec.node.symbol}");
            HDF5DataSet2DStdPtr event_output_float = pGroup_float->create_dataset("${poprec.node.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
            if(nspikes>0) event_output_float->set_data(nspikes, 1, buffer_float);
            pGroup_float->add_attribute("hdf-jive","events");
            pGroup_float->add_attribute("hdf-jive:tags",string("fixed-int,") + tag_string + "," + tag_string_index);
            #endif

        }





        %endfor






    }


    void write_all_traces_to_hdf()
    {

        cout << "\n\nWriting traces to HDF5";

        // Working buffers:
        T_hdf5_type_int data_int[n_results_written];
        T_hdf5_type_float data_float[n_results_written];


        HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);

        HDF5DataSet2DStdPtr time_dataset_int = file->get_group("simulation_fixed/int")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
        HDF5DataSet2DStdPtr time_dataset_float = file->get_group("simulation_fixed/double")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
        ##T_hdf5_type_float dt_float = FixedFloatConversion::to_float(dt_int, dt_upscale);
        
        T_hdf5_type_float dt_float = FixedFloatConversion::to_float(1, time_upscale);
        for(int t=0;t<n_results_written;t++)
        {
            data_int[t] = time_buffer[t];
            data_float[t]  = data_int[t] * dt_float;
        }
        time_dataset_int->set_data(n_results_written,1, data_int);
        time_dataset_float->set_data(n_results_written,1, data_float);



        %for i,poprec in enumerate(network.all_trace_recordings):
        {
            // Save: ${poprec}
            const T_hdf5_type_float node_sf = pow(2.0, ${poprec.node.annotations['fixed-point-format'].upscale} - (VAR_NBITS-1));

            for(int i=0;i<${poprec.size};i++)
            {
                int buffer_offset = ${poprec.global_offset}+i;

                for(int t=0;t<n_results_written;t++)
                {
                    data_int[t] = data_buffers[t][buffer_offset];
                    data_float[t] = data_int[t] * node_sf;
                }

                int nrn_offset = i + ${poprec.src_pop_start_index};
                string tag_string = "${poprec.node.symbol},POP:${poprec.src_population.name},${','.join(poprec.tags)}";
                string tag_string_index = (boost::format("POPINDEX:%04d")%nrn_offset).str();


                #if SAVE_HDF5_INT
                pVecInt[${poprec.src_pop_start_index}+i]->set_data(n_results_written,1, data_int);
                HDF5GroupPtr pGroup_int = file->get_group((boost::format("simulation_fixed/int/${poprec.src_population.name}/%04d/variables/${poprec.node.symbol}")%nrn_offset).str());
                pGroup_int->add_attribute("hdf-jive","trace");

                pGroup_int->add_attribute("hdf-jive:tags",string("fixed-int,") + tag_string + "," + tag_string_index);
                pGroup_int->get_subgroup("raw")->create_softlink(time_dataset_int, "time");
                pHDF5DataSet2DStdPtr pDataset_int = pGroup_int->get_subgroup("raw")->create_dataset("data", HDF5DataSet2DStdSettings(1, hdf5_type_int));
                pDataset_int->set_data(n_results_written,1, data_int);
                #endif


                #if SAVE_HDF5_FLOAT
                HDF5GroupPtr pGroup_float = file->get_group((boost::format("simulation_fixed/double/${poprec.src_population.name}/%04d/variables/${poprec.node.symbol}")%nrn_offset).str());
                pGroup_float->add_attribute("hdf-jive","trace");
                pGroup_float->add_attribute("hdf-jive:tags",string("fixed-float,") + tag_string + "," + tag_string_index);
                pGroup_float->get_subgroup("raw")->create_softlink(time_dataset_float, "time");
                HDF5DataSet2DStdPtr pDataset_float = pGroup_float->get_subgroup("raw")->create_dataset("data", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
                pDataset_float->set_data(n_results_written,1, data_float);
                #endif

            }
        }
        %endfor

        cout << "\n\nFisnihed Writing to HDF5";
    } // void write_all_to_hdf5()






};




struct GlobalData {

    // New version:
    RecordMgrNew recordings_new;

};


GlobalData global_data;




void record_event( IntType global_buffer, const SpikeEmission& evt )
{
    global_data.recordings_new.emitted_spikes[global_buffer].push_back(evt);
}





"""



from fixed_point_common import Eqn, IntermediateNodeFinder, CBasedFixedWriter




class CBasedEqnWriterFixedNetwork(object):
    def __init__(self, network, output_filename, output_c_filename=None, run=True, compile=True, CPPFLAGS=None): #, record_symbols=None):

        self.dt_float = 0.02e-3
        self.dt_upscale = int(np.ceil(np.log2(self.dt_float)))


        # Check all the components use the same floating point formats:
        # NBITS:
        nbits = set([ pop.component.annotation_mgr._annotators['fixed-point-format-ann'].nbits for pop in network.populations])
        assert len(nbits) == 1
        self.nbits = list(nbits)[0]

        #ENCODING OF TIME:
        time_upscale = set([pop.component.get_terminal_obj('t').annotations['fixed-point-format'].upscale for pop in network.populations])
        assert len(time_upscale) == 1
        self.time_upscale = list(time_upscale)[0]


        self.dt_int = NodeFixedPointFormatAnnotator.encore_value_cls(self.dt_float, self.dt_upscale, self.nbits )



        # Make sure the events can be connected:
        evt_src_to_evtportconns = {}
        for evt_conn in network.event_port_connectors:
            key = (evt_conn.src_population, evt_conn.src_port)
            if not key in evt_src_to_evtportconns:
                evt_src_to_evtportconns[key] = []
            evt_src_to_evtportconns[key].append(evt_conn)


        std_variables = {
            'nsim_steps' : 50000,
            'nbits':self.nbits,
            'dt_float' : self.dt_float,
            'dt_int' : self.dt_int,
            'dt_upscale' : self.dt_upscale,
            'time_upscale' : self.time_upscale,
            'output_filename' : output_filename,
            'network':network,
            'evt_src_to_evtportconns': evt_src_to_evtportconns,
                         }



        code_per_electrical_projection = []

        for proj in network.electrical_synapse_projections:
            c = Template(c_electrical_projection_tmpl).render(
                                        projection=proj,
                                        **std_variables
                                            )
            code_per_electrical_projection.append(c)



        code_per_eventport_projection = []
        for proj in network.event_port_connectors:
            c = Template(c_event_projection_tmpl).render(
                                        projection=proj,
                                        **std_variables
                                            )
            code_per_eventport_projection.append(c)






        code_per_pop = []

        for population in network.populations:

            intermediate_nodes = IntermediateNodeFinder(population.component).valid_nodes
            self.intermediate_store_locs = [("op%d" % o.annotations['node-id'], o_number) for (o, o_number) in intermediate_nodes.items()]

            component = population.component


            self.writer = CBasedFixedWriter(component=population.component, population_access_index='i')




            ordered_assignments = component.ordered_assignments_by_dependancies
            self.ass_eqns =[ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in ordered_assignments]
            self.td_eqns = [ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in component.timederivatives]
            self.td_eqns = sorted(self.td_eqns, key=lambda o: o.node.lhs.symbol.lower())


            rv_per_neuron = []
            rv_per_population = []

            for rv in component.random_variable_nodes:

                assert rv.functionname == 'uniform'
                params = [ rv.parameters.get_single_obj_by(name='min'), rv.parameters.get_single_obj_by(name='max'), ]
                param_string = ','.join( "%s, IntType(%d)" % (self.writer.visit( p.rhs_ast), p.rhs_ast.annotations['fixed-point-format'].upscale ) for p in params )

                if rv.modes['share']=='PER_NEURON':
                    rv_per_neuron.append( (rv,param_string) )
                elif rv.modes['share']=='PER_POPULATION':
                    rv_per_population.append( (rv,param_string) )

            try:
                cfile = Template(c_population_details_tmpl).render(
                            population=population,

                            writer = self.writer,

                            eqns_timederivatives = self.td_eqns,
                            eqns_assignments = self.ass_eqns,

                            intermediate_store_locs=self.intermediate_store_locs,

                            rv_per_neuron = rv_per_neuron,
                            rv_per_population = rv_per_population,
                            #record_symbols = record_symbols if record_symbols else [o.symbol for o in  component.assignedvalues + component.state_variables ],

                            **std_variables
                            )
            except:
                print exceptions.html_error_template().render()
                raise

            code_per_pop.append(cfile)



        try:
            c_prog_header = Template(c_prog_header_tmpl).render(
                          ** std_variables
                        )
        except:
            print exceptions.html_error_template().render()
            raise

        try:
            c_main_loop = Template(c_main_loop_tmpl).render(
                        ** std_variables
                        )
        except:
            print exceptions.html_error_template().render()
            raise


        try:
            popl_objs = Template(popl_obj_tmpl).render(
                        ** std_variables
                        )
        except:
            print exceptions.html_error_template().render()
            raise




        cfile = '\n'.join([c_prog_header] +  code_per_pop + [popl_objs] + code_per_electrical_projection +  code_per_eventport_projection + [c_main_loop])

        for f in ['sim1.cpp','a.out',output_filename, 'debug.log',]:
            if os.path.exists(f):
                os.unlink(f)


        if not compile and output_c_filename:
            with open(output_c_filename,'w') as f:
                f.write(cfile)




        # Print out the Node-expressions:
        print '\n\n\n'
        for node in population.component.all_ast_nodes():
            print repr(node), node.annotations['node-id']
            try:
                print ' -> ', self.writer.visit(node)
                print ' -> ', node.annotations['node-value-range']
            except:
                print 'Skipped'
            print
        print '\n\n\n'
        import sys
        sys.stdout.flush()
        sys.stderr.flush()



        if compile:
            self.compile_and_run(cfile, output_c_filename=output_c_filename, run=run, CPPFLAGS=CPPFLAGS)




    def compile_and_run(self, cfile, output_c_filename, run,CPPFLAGS):

        from neurounits.codegen.utils.c_compilation import CCompiler, CCompilationSettings


        ## The preprocessed C++ output:

        # The executable:
        CCompiler.build_executable(src_text=cfile,
                                   compilation_settings = CCompilationSettings(
                                                additional_include_paths=[os.path.expanduser("~/hw/hdf-jive/include"), os.path.abspath('../../cpp/include/') ],
                                                additional_library_paths=[os.path.expanduser("~/hw/hdf-jive/lib/")],
                                                libraries = ['gmpxx', 'gmp','hdfjive','hdf5','hdf5_hl'],
                                                #compile_flags=['-Wall -Werror  -Wfatal-errors -std=gnu++0x  -O3  -g -fopenmp ' + (CPPFLAGS if CPPFLAGS else '') ]),
                                                compile_flags=['-Wall -Werror  -Wfatal-errors -std=gnu++0x  -O2  -g  ' + (CPPFLAGS if CPPFLAGS else '') ]),
                                                #compile_flags=['-Wall -Werror  -Wfatal-errors -std=gnu++0x -O3  -g -march=native ' + (CPPFLAGS if CPPFLAGS else '') ]),
                                                #compile_flags=['-Wall -Wfatal-errors -std=gnu++0x -O2  -g  ' + (CPPFLAGS if CPPFLAGS else '') ]),
#-Wno-used-variable
                                                #
                                   run=True)
        self.results = None #CBasedEqnWriterFixedResultsProxy(self)
        return










#import pylab
##import pylab as plt
#
#
#class CBasedEqnWriterFixedResultsProxy(object):
#    def __init__(self, eqnwriter):
#        self.eqnwriter = eqnwriter
#
#
#    def plot_ranges(self):
#        import tables
#        import sys
#
#
#        h5file = tables.openFile("output.hd5")
#
#        float_group = h5file.root._f_getChild('/simulation_fixed/double/variables/')
#        time_array = h5file.root._f_getChild('/simulation_fixed/double/time').read()
#
#
#        downscale = 10
#        # Plot the variable values:
#        for ast_node in self.eqnwriter.component.assignedvalues+self.eqnwriter.component.state_variables:
#            print 'Plotting:', ast_node
#            data_float = h5file.root._f_getChild('/simulation_fixed/double/variables/%s' % ast_node.symbol).read()
#            data_int   = h5file.root._f_getChild('/simulation_fixed/int/variables/%s' % ast_node.symbol).read()
#
#            f = pylab.figure()
#            ax1 = f.add_subplot(311)
#            ax2 = f.add_subplot(312)
#            ax3 = f.add_subplot(313)
#            ax1.set_ymargin(0.1)
#            ax2.set_ymargin(0.1)
#            ax3.set_ymargin(0.1)
#
#            # Plot the floating-point values:
#            f.suptitle("Values of variable: %s" % ast_node.symbol)
#            ax1.plot(time_array[::downscale], data_float[::downscale], color='blue')
#            node_min = ast_node.annotations['node-value-range'].min.float_in_si()
#            node_max = ast_node.annotations['node-value-range'].max.float_in_si()
#            node_upscale = ast_node.annotations['fixed-point-format'].upscale
#            ax1.axhspan(node_min, node_max, color='green', alpha=0.2  )
#            ax1.axhspan( pow(2,node_upscale), -pow(2,node_upscale), color='lightgreen', alpha=0.4  )
#
#
#            # Plot the integer values:
#            nbits = self.eqnwriter.nbits
#            _min = -pow(2.0, nbits-1)
#            _max =  pow(2.0, nbits-1)
#            ax2.plot( time_array, data_int[:,-1], color='blue')
#            ax2.axhspan( _min, _max, color='lightgreen', alpha=0.4  )
#
#            ax3.hist(data_int[:,-1], range = (_min * 1.1 , _max * 1.1), bins=1024)
#            ax3.axvline( _min, color='black', ls='--')
#            ax3.axvline( _max, color='black', ls='--')
#
#
#
#
#        # Plot the intermediate nodes values:
#        for ast_node in self.eqnwriter.component.all_ast_nodes():
#
#            try:
#
#                data_float = h5file.root._f_getChild('/simulation_fixed/double/operations/' + "op%d" % ast_node.annotations['node-id']).read()
#                data_int = h5file.root._f_getChild('/simulation_fixed/int/operations/' + "op%d" % ast_node.annotations['node-id']).read()
#
#                f = pylab.figure()
#                ax1 = f.add_subplot(311)
#                ax2 = f.add_subplot(312)
#                ax3 = f.add_subplot(313)
#                ax1.set_ymargin(0.1)
#                ax2.set_ymargin(0.1)
#                ax3.set_ymargin(0.1)
#
#                f.suptitle("Values of ast_node: %s" % str(ast_node))
#                ax1.plot(time_array[::downscale], data_float[::downscale,-1], color='blue')
#                node_min = ast_node.annotations['node-value-range'].min.float_in_si()
#                node_max = ast_node.annotations['node-value-range'].max.float_in_si()
#                node_upscale = ast_node.annotations['fixed-point-format'].upscale
#                ax1.axhspan(node_min, node_max, color='green', alpha=0.2  )
#                ax1.axhspan(pow(2,node_upscale), -pow(2,node_upscale), color='lightgreen', alpha=0.4  )
#
#                            # Plot the integer values:
#                _min = -pow(2.0, nbits-1)
#                _max =  pow(2.0, nbits-1)
#                ax2.plot( time_array, data_int[:,-1], color='blue')
#                ax2.axhspan( _min, _max, color='lightgreen', alpha=0.4  )
#
#                ax3.hist(data_int[:,-1], range = (_min * 1.1 , _max * 1.1), bins=1024)
#                ax3.axvline( _min, color='black', ls='--')
#                ax3.axvline( _max, color='black', ls='--')
#
#
#
#                invalid_points_limits = np.logical_or( node_min > data_float[:,-1], data_float[:,-1]  > node_max).astype(int)
#                invalid_points_upscale = np.logical_or( -pow(2,node_upscale) > data_float[:,-1], data_float[:,-1]  > pow(2,node_upscale)).astype(int)
#
#
#
#                def get_invalid_ranges(data):
#                    """Turn an array of integers into a list of pairs, denoting when we turn on and off"""
#                    data_switch_to_valid = np.where( np.diff(data) > 0 )[0]
#                    data_switch_to_invalid = np.where( np.diff(data) < 0 )[0]
#                    print data_switch_to_valid
#                    print data_switch_to_invalid
#
#                    assert np.fabs( len(data_switch_to_valid) - len(data_switch_to_invalid) ) <= 1
#
#                    if len(data_switch_to_valid) == len(data_switch_to_invalid) == 0:
#                        return []
#
#                    valid_invalid =  np.sort( np.concatenate([data_switch_to_valid, data_switch_to_invalid] ) ).tolist()
#
#
#
#                    if len(data_switch_to_invalid)>0:
#                        if  len(data_switch_to_valid)>0:
#                            offset = 1 if data_switch_to_invalid[0] > data_switch_to_valid[0] else 0
#                        else:
#                            offset = 1
#                    else:
#                        offset = 0
#
#                    valid_invalid = [0] + valid_invalid + [len(data)-1]
#                    pairs = zip(valid_invalid[offset::2], valid_invalid[offset+1::2])
#                    print pairs
#
#                    #if pairs:
#                    #    print 'ERRORS!'
#
#                    return pairs
#
#
#
#
#                print 'Plotting Node:', ast_node
#                print '  -', node_min, 'to', node_max
#                print data_float.shape
#
#                print 'Invalid regions:'
#                invalid_ranges_limits = get_invalid_ranges(invalid_points_limits)
#                invalid_ranges_upscale = get_invalid_ranges(invalid_points_upscale)
#
#
#                for (x1,x2) in invalid_ranges_upscale:
#                    ax1.axvspan(time_array[x1],time_array[x2], color='red',alpha=0.6)
#
#
#                if invalid_ranges_upscale:
#                    print 'ERROR: Value falls out of upscale range!'
#
#                #f.close()
#
#
#
#
#                print 'Recorded'
#
#
#                #pylab.show()
#                #pylab.close(f)
#
#
#            except tables.exceptions.NoSuchNodeError:
#                print 'Not recorded'
#
#
#
#
#
#
#        pylab.show()
#        sys.exit(0)
#
#        assert False
