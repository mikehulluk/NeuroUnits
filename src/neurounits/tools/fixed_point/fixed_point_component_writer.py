


import mako
from mako.template import Template

#import subprocess
#from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np

import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase

import pylab
import pylab as plt




c_prog = r"""





/* Set or unset this variable: */

#ifndef ON_NIOS
#define ON_NIOS false
#endif
#define DISPLAY_LOOP_INFO true



#include "basic_types.h"






#if ON_NIOS
#define CALCULATE_FLOAT false
#define USE_HDF false
#define SAVE_HDF5_FLOAT false
#define SAVE_HDF5_INT false
#define SAFEINT false 

#else
#define CALCULATE_FLOAT true
#define USE_HDF true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT true
#define SAFEINT true
#endif




//#define NSIM_REPS 200




/* ------- General  ----------- */ 
#define CHECK_INT_FLOAT_COMPARISON true
#define CHECK_INT_FLOAT_COMPARISON_FOR_EXP false

const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT = 100;
const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT_FOR_EXP = 300;

const int nsim_steps = ${nsim_steps};


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
// For Saving the data to HDF5:
#include "hdfjive.h"
const string output_filename = "${output_filename}";

// Data types used for storing in HDF5:
const hid_t hdf5_type_int = H5T_NATIVE_INT;
const hid_t hdf5_type_float = H5T_NATIVE_FLOAT;

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
        //: exponential(8, 3)    // (nbits, upscale)
        : exponential(5, 3)    // (nbits, upscale)
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




// Define the data-structures:
struct NrnData
{
    // Parameters:
% for p in parameter_defs:
    IntType ${p.symbol};      // Upscale: ${p.annotations['fixed-point-format'].upscale}
% endfor

    // Assignments:
% for ass in assignment_defs:
    IntType ${ass.symbol};      // Upscale: ${ass.annotations['fixed-point-format'].upscale}
% endfor

    // States:
% for sv_def in state_var_defs:
    IntType ${sv_def.symbol};    // Upscale: ${sv_def.annotations['fixed-point-format'].upscale}
    IntType d_${sv_def.symbol};
% endfor

<%
    cons = ',\n      '.join( 
                    ['%s(0)' % o.symbol for o in parameter_defs + assignment_defs ] +
                    ['%s(0),\n      d_%s(0)' % (o.symbol, o.symbol) for o in state_var_defs ] 
                    )
%>
    NrnData()
    : ${cons} 
    {}
};




NrnData output_data[nsim_steps];




void initialise_statevars(NrnData& d)
{
    % for sv_def in state_var_defs:
    d.${sv_def.symbol} = auto_shift( IntType(${sv_def.initial_value.annotations['fixed-point-format'].const_value_as_int}),  IntType(${sv_def.initial_value.annotations['fixed-point-format'].upscale} - ${sv_def.annotations['fixed-point-format'].upscale} ) );
    % endfor
}





// Update-function
void sim_step(NrnData& d, IntType time_step)
{
    const IntType dt_int = IntType(${dt_int});
    const IntType dt_upscale = IntType(${dt_upscale});
    const IntType time_upscale = IntType(${time_upscale});
    const IntType t = inttype32_from_inttype64<IntType>( auto_shift64( get_value64(dt_int) * get_value64(time_step), get_value64(dt_upscale- time_upscale ) ));


    #if DISPLAY_LOOP_INFO
    if(get_value32(time_step)%100 == 0)
    {
        std::cout << "Loop: " << time_step << "\n";
        std::cout << "t: " << t << "\n";
    }
    #endif

    // Calculate assignments:
    % for eqn in eqns_assignments:
    d.${eqn.node.lhs.symbol} = ${eqn.rhs_cstr} ;
    % endfor

    // Calculate delta's for all state-variables:
    % for eqn in eqns_timederivatives:
    IntType d_${eqn.node.lhs.symbol} = ${eqn.rhs_cstr[0]} ;
    d.${eqn.node.lhs.symbol} += ${eqn.rhs_cstr[1]} ;
    % endfor


    #if USE_HDF && SAVE_HDF5_INT
    {
        HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
        file->get_dataset("simulation_fixed/int/time")->append<T_hdf5_type_int>(get_value32(t));
    
        % for eqn in eqns_assignments:
        file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>(get_value32( d.${eqn.node.lhs.symbol}));
        % endfor

        % for eqn in eqns_timederivatives:
        file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>(get_value32( d.${eqn.node.lhs.symbol}));
        % endfor
    }
    #endif

    
    #if USE_HDF && SAVE_HDF5_FLOAT
    { 
        const double dt_float = FixedFloatConversion::to_float(IntType(dt_int), IntType(${dt_upscale}));  
        const double t_float = get_value32(time_step) * dt_float;
    
        HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
        file->get_dataset("simulation_fixed/double/time")->append<T_hdf5_type_float>(t_float);
        % for eqn in eqns_timederivatives:
        file->get_dataset("simulation_fixed/double/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( FixedFloatConversion::to_float(  d.${eqn.node.lhs.symbol},  IntType(${eqn.node.lhs.annotations['fixed-point-format'].upscale}) ) );
        % endfor
        % for eqn in eqns_assignments:
        file->get_dataset("simulation_fixed/double/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( FixedFloatConversion::to_float(  d.${eqn.node.lhs.symbol},  IntType(${eqn.node.lhs.annotations['fixed-point-format'].upscale}) ) );
        % endfor
    }
    #endif

}








#if USE_HDF
void setup_hdf5()
{
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);

    // Time
    file->get_group("simulation_fixed/double")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
    file->get_group("simulation_fixed/int")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_int) );

    // Storage for state-variables and assignments:
    % for sv_def in state_var_defs + assignment_defs:
    file->get_group("simulation_fixed/double/variables/")->create_dataset("${sv_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
    file->get_group("simulation_fixed/int/variables/")->create_dataset("${sv_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
    % endfor

    // Storage for the intermediate values in calculations:
    %for intermediate_store_loc, size in intermediate_store_locs:
    file->get_group("simulation_fixed/double/operations/")->create_dataset("${intermediate_store_loc}", HDF5DataSet2DStdSettings(${size}, hdf5_type_float) );
    file->get_group("simulation_fixed/int/operations/")->create_dataset("${intermediate_store_loc}", HDF5DataSet2DStdSettings(${size},  hdf5_type_int) );
    %endfor
}
#endif


void print_results_from_NIOS()
{
    // Assignments + states:
    % for ass in assignment_defs + state_var_defs:
    cout << "\n#!DATA{ 'name':'${ass.symbol}' } {'size': ${nsim_steps},  'fixed_point': {'upscale':${ass.annotations['fixed-point-format'].upscale}, 'nbits':${nbits}} } [";
    for(IntType i=IntType(0);i<nsim_steps;i++) cout << output_data[ get_value32(i)].${ass.symbol} << " ";
    cout << "]\n"; 
    % endfor

    cout << "\n#! FINISHED\n";  
}


 






int main()
{

    // Enable floating point exception trapping:
    //feenableexcept(-1);
    #if !ON_NIOS
    feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    #endif //!ON_NIOS


    #if USE_HDF
    setup_hdf5();
    #endif

    NrnData data;
    initialise_statevars(data);



    #if NSIM_REPS
    for(int k=0;k<NSIM_REPS;k++)
    {
        if(k%100==0) cout << "Loop: " << k << "\n" << flush;
    #endif
        
        for(IntType i=IntType(0);i<nsim_steps;i++)
        {
            sim_step(data, IntType(i));
            output_data[get_value32(i)] = data;    
        }
    
    #if NSIM_REPS
    }
    #endif
    
    
    
    #if ON_NIOS
    print_results_from_NIOS();
    #endif


    printf("Simulation Complete\n");
}




"""








from fixed_point_common import Eqn, IntermediateNodeFinder, CBasedFixedWriter



class CBasedEqnWriterFixedComponent(object):
    def __init__(self, component, output_filename, output_c_filename=None, run=True, compile=True, CPPFLAGS=None):

        self.dt_float = 0.1e-3
        self.dt_upscale = int(np.ceil(np.log2(self.dt_float)))
        self.dt_int = component.annotation_mgr._annotators['fixed-point-format-ann'].encode_value(self.dt_float, self.dt_upscale)

        

        self.node_labeller = component.annotation_mgr._annotators['node-ids']
        intermediate_nodes = IntermediateNodeFinder(component).valid_nodes
        self.intermediate_store_locs = [("op%d" % o.annotations['node-id'], o_number) for (o, o_number) in intermediate_nodes.items()]

        self.component = component
        

        self.writer = CBasedFixedWriter(component=component) 
        self.nbits = component.annotation_mgr._annotators['fixed-point-format-ann'].nbits



        ordered_assignments = self.component.ordered_assignments_by_dependancies
        self.ass_eqns =[ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in ordered_assignments]
        self.td_eqns = [ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in self.component.timederivatives]        
        self.td_eqns = sorted(self.td_eqns, key=lambda o: o.node.lhs.symbol.lower())

        

        cfile = Template(c_prog).render(
                    output_filename = output_filename,

                    parameter_defs = list(self.component.parameters),
                    state_var_defs = list(self.component.state_variables),
                    assignment_defs = list(self.component.assignedvalues),

                    dt_float = self.dt_float,
                    dt_int = self.dt_int,
                    dt_upscale = self.dt_upscale,
                    
                    time_upscale = self.component.get_terminal_obj('t').annotations['fixed-point-format'].upscale,
                    
                    eqns_timederivatives = self.td_eqns,
                    eqns_assignments = self.ass_eqns,
                    
                    nbits=self.nbits,
                    intermediate_store_locs=self.intermediate_store_locs,
                    
                    nsim_steps = 3000,
                    )



        for f in ['sim1.cpp','a.out',output_filename, 'debug.log',]:
            if os.path.exists(f):
                os.unlink(f)


        if not compile and output_c_filename:
            with open(output_c_filename,'w') as f:
                f.write(cfile)


        if compile:
            self.compile_and_run(cfile, output_c_filename=output_c_filename, run=run, CPPFLAGS=CPPFLAGS)




    def compile_and_run(self, cfile, output_c_filename, run,CPPFLAGS):

        from neurounits.tools.c_compilation import CCompiler, CCompilationSettings
        
        
        CCompiler.build_executable(src_text=cfile, 
                                   compilation_settings = CCompilationSettings(
                                                additional_include_paths=[os.path.expanduser("~/hw/hdf-jive/include"), os.path.abspath('../../cpp/include/') ], 
                                                additional_library_paths=[os.path.expanduser("~/hw/hdf-jive/lib/")], 
                                                libraries = ['gmpxx', 'gmp','hdfjive','hdf5','hdf5_hl'],
                                                compile_flags=['-Wall -Werror -Wfatal-errors -std=gnu++0x -g -p ' + (CPPFLAGS if CPPFLAGS else '') ]),
                                   run=True)

        self.results = CBasedEqnWriterFixedResultsProxy(self)
        return












class CBasedEqnWriterFixedResultsProxy(object):
    def __init__(self, eqnwriter):
        self.eqnwriter = eqnwriter


    def plot_ranges(self):
        import tables
        import sys


        h5file = tables.openFile("output.hd5")

        float_group = h5file.root._f_getChild('/simulation_fixed/double/variables/')
        time_array = h5file.root._f_getChild('/simulation_fixed/double/time').read()


        downscale = 10
        # Plot the variable values:
        for ast_node in self.eqnwriter.component.assignedvalues+self.eqnwriter.component.state_variables:
            print 'Plotting:', ast_node
            data_float = h5file.root._f_getChild('/simulation_fixed/double/variables/%s' % ast_node.symbol).read()
            data_int   = h5file.root._f_getChild('/simulation_fixed/int/variables/%s' % ast_node.symbol).read()

            f = pylab.figure()
            ax1 = f.add_subplot(311)
            ax2 = f.add_subplot(312)
            ax3 = f.add_subplot(313)
            ax1.set_ymargin(0.1)
            ax2.set_ymargin(0.1)
            ax3.set_ymargin(0.1)

            # Plot the floating-point values: 
            f.suptitle("Values of variable: %s" % ast_node.symbol)
            ax1.plot(time_array[::downscale], data_float[::downscale], color='blue')
            node_min = ast_node.annotations['node-value-range'].min.float_in_si()
            node_max = ast_node.annotations['node-value-range'].max.float_in_si()
            node_upscale = ast_node.annotations['fixed-point-format'].upscale
            ax1.axhspan(node_min, node_max, color='green', alpha=0.2  )
            ax1.axhspan( pow(2,node_upscale), -pow(2,node_upscale), color='lightgreen', alpha=0.4  )


            # Plot the integer values:
            nbits = self.eqnwriter.nbits
            _min = -pow(2.0, nbits-1)
            _max =  pow(2.0, nbits-1)
            ax2.plot( time_array, data_int[:,-1], color='blue')
            ax2.axhspan( _min, _max, color='lightgreen', alpha=0.4  )
            
            ax3.hist(data_int[:,-1], range = (_min * 1.1 , _max * 1.1), bins=1024)
            ax3.axvline( _min, color='black', ls='--')
            ax3.axvline( _max, color='black', ls='--')




        # Plot the intermediate nodes values:
        for ast_node in self.eqnwriter.component.all_ast_nodes():

            try:
                
                data_float = h5file.root._f_getChild('/simulation_fixed/double/operations/' + "op%d" % ast_node.annotations['node-id']).read()
                data_int = h5file.root._f_getChild('/simulation_fixed/int/operations/' + "op%d" % ast_node.annotations['node-id']).read()

                f = pylab.figure()
                ax1 = f.add_subplot(311)
                ax2 = f.add_subplot(312)
                ax3 = f.add_subplot(313)
                ax1.set_ymargin(0.1)
                ax2.set_ymargin(0.1)
                ax3.set_ymargin(0.1)

                f.suptitle("Values of ast_node: %s" % str(ast_node))
                ax1.plot(time_array[::downscale], data_float[::downscale,-1], color='blue')
                node_min = ast_node.annotations['node-value-range'].min.float_in_si()
                node_max = ast_node.annotations['node-value-range'].max.float_in_si()
                node_upscale = ast_node.annotations['fixed-point-format'].upscale
                ax1.axhspan(node_min, node_max, color='green', alpha=0.2  )
                ax1.axhspan(pow(2,node_upscale), -pow(2,node_upscale), color='lightgreen', alpha=0.4  )

                            # Plot the integer values:
                _min = -pow(2.0, nbits-1)
                _max =  pow(2.0, nbits-1)
                ax2.plot( time_array, data_int[:,-1], color='blue')
                ax2.axhspan( _min, _max, color='lightgreen', alpha=0.4  )
                
                ax3.hist(data_int[:,-1], range = (_min * 1.1 , _max * 1.1), bins=1024)
                ax3.axvline( _min, color='black', ls='--')
                ax3.axvline( _max, color='black', ls='--')

                

                invalid_points_limits = np.logical_or( node_min > data_float[:,-1], data_float[:,-1]  > node_max).astype(int)
                invalid_points_upscale = np.logical_or( -pow(2,node_upscale) > data_float[:,-1], data_float[:,-1]  > pow(2,node_upscale)).astype(int)



                def get_invalid_ranges(data):
                    """Turn an array of integers into a list of pairs, denoting when we turn on and off"""
                    data_switch_to_valid = np.where( np.diff(data) > 0 )[0]
                    data_switch_to_invalid = np.where( np.diff(data) < 0 )[0]
                    print data_switch_to_valid
                    print data_switch_to_invalid

                    assert np.fabs( len(data_switch_to_valid) - len(data_switch_to_invalid) ) <= 1

                    if len(data_switch_to_valid) == len(data_switch_to_invalid) == 0:
                        return []

                    valid_invalid =  np.sort( np.concatenate([data_switch_to_valid, data_switch_to_invalid] ) ).tolist()



                    if len(data_switch_to_invalid)>0:
                        if  len(data_switch_to_valid)>0:
                            offset = 1 if data_switch_to_invalid[0] > data_switch_to_valid[0] else 0
                        else:
                            offset = 1
                    else:
                        offset = 0

                    valid_invalid = [0] + valid_invalid + [len(data)-1]
                    pairs = zip(valid_invalid[offset::2], valid_invalid[offset+1::2])
                    print pairs

                    #if pairs:
                    #    print 'ERRORS!'

                    return pairs




                print 'Plotting Node:', ast_node
                print '  -', node_min, 'to', node_max
                print data_float.shape

                print 'Invalid regions:'
                invalid_ranges_limits = get_invalid_ranges(invalid_points_limits)
                invalid_ranges_upscale = get_invalid_ranges(invalid_points_upscale)


                for (x1,x2) in invalid_ranges_upscale:
                    ax1.axvspan(time_array[x1],time_array[x2], color='red',alpha=0.6)


                if invalid_ranges_upscale:
                    print 'ERROR: Value falls out of upscale range!'
                
                #f.close()




                print 'Recorded'


                #pylab.show()
                #pylab.close(f)


            except tables.exceptions.NoSuchNodeError:
                print 'Not recorded'






        pylab.show()
        sys.exit(0)

        assert False
