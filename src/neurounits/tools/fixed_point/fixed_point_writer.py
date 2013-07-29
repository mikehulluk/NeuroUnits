


import mako
from mako.template import Template

import subprocess
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np


c_prog = r"""

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <gmpxx.h>
#include <iomanip>
#include <sstream>
#include <assert.h>
#include <cinttypes>
#include <fenv.h>
#include <boost/format.hpp>




#include "hdfjive.h"
const string output_filename = "${output_filename}";

// Data types used for storing in HDF5: 
const hid_t hdf5_type_int = H5T_NATIVE_INT;
const hid_t hdf5_type_float = H5T_NATIVE_FLOAT;

typedef int T_hdf5_type_int;
typedef float T_hdf5_type_float;    




typedef std::int64_t int64;


const int VAR_NBITS = ${nbits};



#define CALCULATE_FLOAT true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT true

#define CHECK_INT_FLOAT_COMPARISON true



#include "float_utils.h"


// Save-data function
typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;

double to_float(int val, int upscale)
{
    return FixedFloatConversion::to_float(val, upscale);
}

int from_float(double val, int upscale)
{
    return FixedFloatConversion::from_float(val, upscale);
}

using mh::auto_shift;
using mh::auto_shift64;




#include "float_utils.h"
#include "lut.h"


//#include "c_deps/lut.h"

struct LookUpTables
{

    LookUpTables() 
        //: exponential(8, 3)    // (nbits, upscale)
        : exponential(5, 3)    // (nbits, upscale)
    { }
    
    LookUpTableExpPower2<VAR_NBITS> exponential;


};
LookUpTables lookuptables;




int do_add_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
            
    int res_int = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local); 

    if( SAVE_HDF5_INT )
    {
        HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) v1 | (T_hdf5_type_int) v2 | (T_hdf5_type_int) (res_int) ) ;
    }
    

    
    if(CALCULATE_FLOAT)
    {
        int res_fp = from_float(to_float(v1,up1) + to_float(v2,up2), up_local);
        
        if( CHECK_INT_FLOAT_COMPARISON )
        {
            int diff = res_int - res_fp;
            if(diff <0) diff = -diff;
            assert( (diff==0)  || (diff==1));
        }
        
        if( SAVE_HDF5_FLOAT )
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% expr_id ).str())->append_buffer( 
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp) ) ;
        }    
    }
   
    return res_int;    
} 


int do_sub_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    
    
    
    
    
    int res_int = auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local); 
    
    
    //std::cout << "\nSub OP:" << res_fp << " and " << res_int  << "\n";
    
    // Check the results:
    // //////////////////
    int res_fp = from_float(to_float(v1,up1) - to_float(v2,up2), up_local);
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    assert( (diff==0)  || (diff==1));



    // Write to HDF5:
    //////////////////
    // -- Floating point version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp) ) ;
    
    // -- Integer version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) v1 | (T_hdf5_type_int) v2 | (T_hdf5_type_int) (res_int) ) ;


    return res_int;    
} 

int do_mul_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) * to_float(v2,up2), up_local);
    
    
    // Convert into integer operations:
   
    // Need to promote to 64 bit:
    int64 v12 = (int64)v1* (int64)v2;
    int res_int = auto_shift64(v12, (up1+up2-up_local-(VAR_NBITS-1)) );
    
    //std::cout << "\nMul OP:" << res_fp << " and " << res_int  << "\n";
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    assert( (diff==0)  || (diff==1));
    
    
    
    // Write to HDF5:
    //////////////////
    // -- Floating point version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp) ) ;
    
    // -- Integer version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) v1 | (T_hdf5_type_int) v2 | (T_hdf5_type_int) (res_int) ) ;
    
    return res_int;    
} 



int do_div_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) / to_float(v2,up2), up_local);
    
    int64 v1_L = (int64) v1;
    int64 v2_L = (int64) v2;
    
    v1_L = auto_shift64(v1_L, (VAR_NBITS-1) );
    
    
    int64 v = v1_L/v2_L;
    v = auto_shift64(v, up1-up2 - up_local);
    
    assert( v < (1<<(VAR_NBITS) ) );
    
    
    int res_int = v; 
    
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    //assert( (diff==0)  || (diff==1));
    
    
    // Write to HDF5:
    //////////////////
    // -- Floating point version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp) ) ;
    
    // -- Integer version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) v1 | (T_hdf5_type_int) v2 | (T_hdf5_type_int) (res_int) ) ;
    
    return res_int;    
} 

int int_exp(int v1, int up1, int up_local, int expr_id)
{

    int res_fp = from_float( exp( to_float(v1,up1) ), up_local );    
    int res_int = lookuptables.exponential.get( v1, up1, up_local ); 
    
    
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    //cout << "Diff: " << diff;
    //assert( (diff==0)  || (diff==1) || (diff==2) );
    

    
    // Write to HDF5:
    //////////////////
    // -- Floating point version: 
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% expr_id ).str())->append_buffer( 
            DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) |  (T_hdf5_type_float) (res_fp) ) ;
    
    ## // -- Integer version: 
    ## HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% expr_id ).str())->append_buffer( 
    ##        DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) v1 | (T_hdf5_type_int) (res_int) ) ;
    
    
    return res_int;

}




// Define the data-structures:
struct NrnData
{

    // Parameters:
% for p in parameter_defs_new:
    ${p.annotations['fixed-point-format'].datatype} ${p.symbol};      // Upscale: ${p.annotations['fixed-point-format'].upscale}
% endfor

    // Assignments:
% for ass in assignment_defs_new:
    ${ass.annotations['fixed-point-format'].datatype} ${ass.symbol};      // Upscale: ${ass.annotations['fixed-point-format'].upscale}
% endfor

    // States:
% for sv_def in state_var_defs_new:
    ${sv_def.annotations['fixed-point-format'].datatype} ${sv_def.symbol};    // Upscale: ${sv_def.annotations['fixed-point-format'].upscale} 
    ${sv_def.annotations['fixed-point-format'].datatype} d_${sv_def.symbol};
% endfor


};





// Update-function
void sim_step(NrnData& d, int time_step)
{
    const double dt = 0.1e-3;
    const double t_float = time_step * dt;
    const int t = from_float(t_float, 1);

    if(time_step%100 == 0)
    {
        std::cout << "Loop: " << time_step << "\n";
        std::cout << "t: " << t << "\n";
    }

    // Calculate assignments:
% for eqn in eqns_assignments:
    d.${eqn.node.lhs.symbol} = from_float( to_float( ${eqn.rhs_cstr},  ${eqn.node.rhs_map.annotations['fixed-point-format'].upscale}), ${eqn.node.lhs.annotations['fixed-point-format'].upscale}) ;
% endfor

    // Calculate delta's for all state-variables:
% for eqn in eqns_timederivatives:
    float d_${eqn.node.lhs.symbol} = to_float( ${eqn.rhs_cstr} , ${eqn.node.rhs_map.annotations['fixed-point-format'].upscale} ) * dt;
    d.${eqn.node.lhs.symbol} += from_float( ( d_${eqn.node.lhs.symbol} ),  ${eqn.node.lhs.annotations['fixed-point-format'].upscale} );
% endfor    


    
    
    
    
    
    // Write to HDF5
    /* -------------------------------------------------------------------------------------------- */
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
    
    // Time
    file->get_dataset("simulation_fixed/int/time")->append<T_hdf5_type_int>(t);
    file->get_dataset("simulation_fixed/float/time")->append<T_hdf5_type_float>(t_float);
    
    // Storage for state-variables and assignments:
    % for eqn in eqns_assignments:
    file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>( d.${eqn.node.lhs.symbol} );
    file->get_dataset("simulation_fixed/float/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( to_float(  d.${eqn.node.lhs.symbol},  ${eqn.node.lhs.annotations['fixed-point-format'].upscale} ) );
    % endfor   
    
    % for eqn in eqns_timederivatives:
    file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>( d.${eqn.node.lhs.symbol} );
    file->get_dataset("simulation_fixed/float/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( to_float(  d.${eqn.node.lhs.symbol},  ${eqn.node.lhs.annotations['fixed-point-format'].upscale} ) );
    % endfor   
    /* -------------------------------------------------------------------------------------------- */


}






void initialise_statevars(NrnData& d)
{          
    % for sv_def in state_var_defs_new:
    d.${sv_def.symbol} = auto_shift( ${sv_def.initial_value.annotations['fixed-point-format'].const_value_as_int},  ${sv_def.initial_value.annotations['fixed-point-format'].upscale} - ${sv_def.annotations['fixed-point-format'].upscale} );
    % endfor   
   
}




void setup_hdf5()
{
    
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
    

    
    // Time
    file->get_group("simulation_fixed/float")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
    file->get_group("simulation_fixed/int")->create_dataset("time", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
    
    // Storage for state-variables and assignments:
    % for sv_def in state_var_defs_new:
    file->get_group("simulation_fixed/float/variables/")->create_dataset("${sv_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
    file->get_group("simulation_fixed/int/variables/")->create_dataset("${sv_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
    % endfor   
    
    % for ass_def in assignment_defs_new:
    file->get_group("simulation_fixed/float/variables/")->create_dataset("${ass_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_float) );
    file->get_group("simulation_fixed/int/variables/")->create_dataset("${ass_def.symbol}", HDF5DataSet2DStdSettings(1, hdf5_type_int) );
    % endfor   


    // Storage for the intermediate values in calculations:

    %for intermediate_store_loc, size in intermediate_store_locs:
    file->get_group("simulation_fixed/float/operations/")->create_dataset("${intermediate_store_loc}", HDF5DataSet2DStdSettings(${size}, hdf5_type_float) );
    file->get_group("simulation_fixed/int/operations/")->create_dataset("${intermediate_store_loc}", HDF5DataSet2DStdSettings(${size},  hdf5_type_int) );
    %endfor
    
}




int main()
{

    
    // Enable floating point exception trapping:
    //feenableexcept(-1);
    feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    
    
    
    
    setup_hdf5();
    
    NrnData data;
    initialise_statevars(data);



    for(int i=0;i<3000;i++)
    {
    
        
        sim_step(data, i);
                
    }


    

    printf("Simulation Complete\n");
}




"""








import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase 



        
        
class Eqn(object):
    def __init__(self, node, rhs_cstr):
        self.node = node
        self.rhs_cstr = rhs_cstr




class IntermediateNodeFinder(ASTActionerDefaultIgnoreMissing):
    
    def __init__(self, component):
        self.valid_nodes = {}
        super(IntermediateNodeFinder,self).__init__(component=component)
        
    # How many values do we store per operation:
    def ActionAddOp(self, o, **kwargs):
        self.valid_nodes[o] = 3 

    def ActionSubOp(self, o, **kwargs):
        self.valid_nodes[o] = 3
        
    def ActionMulOp(self, o, **kwargs):
        self.valid_nodes[o] = 3
        
    def ActionDivOp(self, o, **kwargs):
        self.valid_nodes[o] = 3
        
    def ActionExpOp(self, o, **kwargs):
        assert False
        self.valid_nodes[o] = 3

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        assert o.function_def.funcname == '__exp__'
        self.valid_nodes[o] = 2      

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        assert False





class CBasedFixedWriter(ASTVisitorBase):
    
    def __init__(self, component, node_int_labels):
       
        self.intlabels = node_int_labels 
        
        
        super(CBasedFixedWriter, self).__init__()
        
    def to_c(self, obj):
        return self.visit(obj)

    def VisitRegimeDispatchMap(self, o):
        assert len (o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0])

    def get_var_str(self, name):
        return "d.%s" % name

    def DoOpOpComplex(self, o, op): 

        expr_lhs = self.visit(o.lhs)
        expr_rhs = self.visit(o.rhs)
        expr_num = self.intlabels[o]
        res = "do_%s_op( %s, %d, %s, %d, %d, %d)" % (
                                            op,
                                            expr_lhs, o.lhs.annotations['fixed-point-format'].upscale,
                                            expr_rhs, o.rhs.annotations['fixed-point-format'].upscale,
                                            o.annotations['fixed-point-format'].upscale, 
                                            expr_num,
                                                     )
        return res

    
    def VisitAddOp(self, o):
        return self.DoOpOpComplex(o, 'add')

    def VisitSubOp(self, o):
        return self.DoOpOpComplex(o, 'sub')

    def VisitMulOp(self, o):
        return self.DoOpOpComplex(o, 'mul')

    def VisitDivOp(self, o):
        return self.DoOpOpComplex(o, 'div')




    def VisitIfThenElse(self, o):

        return "from_float( (%s) ? to_float(%s, %d) : to_float(%s, %d), %d )" % (
                    self.visit(o.predicate),
                    self.visit(o.if_true_ast),
                    o.if_true_ast.annotations['fixed-point-format'].upscale, 
                    self.visit(o.if_false_ast),
                    o.if_false_ast.annotations['fixed-point-format'].upscale, 
                    o.annotations['fixed-point-format'].upscale, 
                ) 
        
        
        
        

    def VisitInEquality(self, o):
        ann_lt_upscale = o.less_than.annotations['fixed-point-format'].upscale 
        ann_gt_upscale = o.greater_than.annotations['fixed-point-format'].upscale    
        return "(to_float(%s, %d) < to_float(%s, %d) )" % ( self.visit(o.less_than), ann_lt_upscale,  self.visit(o.greater_than), ann_gt_upscale )


    def VisitFunctionDefUserInstantiation(self,o):        
        assert False

    def VisitFunctionDefBuiltInInstantiation(self,o):        
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'
        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast)
        ann_func_upscale = o.annotations['fixed-point-format'].upscale 
        ann_param_upscale = param.rhs_ast.annotations['fixed-point-format'].upscale 
        expr_num = self.intlabels[o]
        
        return """ int_exp( %s, %d, %d, %d )""" %(param_term, ann_param_upscale, ann_func_upscale, expr_num ) 

    def VisitFunctionDefInstantiationParater(self, o):
        assert False
        return o.symbol

    def VisitFunctionDefParameter(self, o):
        assert False
        return o.symbol

    def VisitStateVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitParameter(self, o):
        return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        return "%d" % o.annotations['fixed-point-format'].const_value_as_int
        
    def VisitAssignedVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        return "%d" % o.annotations['fixed-point-format'].const_value_as_int

    def VisitSuppliedValue(self, o):
        return o.symbol




    
    
    

class CBasedEqnWriterFixed(object):
    def __init__(self, component, output_filename, nbits):
        
        
        
        #from neurounits.visitors.common.node_label_with_integers import NodeToIntLabeller
        
        
        self.node_labeller = component.annotation_mgr._annotators['node-ids']
        self.node_labels = self.node_labeller.node_to_int
        intermediate_nodes = IntermediateNodeFinder(component).valid_nodes
        self.intermediate_store_locs = [("op%d" % self.node_labeller.node_to_int[o], o_number ) for (o, o_number) in intermediate_nodes.items()]
        
        
        
        self.component = component
        self.float_type = 'int'

        self.writer = CBasedFixedWriter(component=component, node_int_labels=self.node_labeller.node_to_int)




        ordered_assignments = self.component.ordered_assignments_by_dependancies
        self.ass_eqns =[ Eqn(node=td, rhs_cstr=self.writer.to_c(td.rhs_map) ) for td in ordered_assignments]
        self.td_eqns = [ Eqn(node=td, rhs_cstr=self.writer.to_c(td.rhs_map) ) for td in self.component.timederivatives]
        self.td_eqns = sorted(self.td_eqns, key=lambda o: o.node.lhs.symbol.lower())
                
      
        cfile = Template(c_prog).render(
                    output_filename = output_filename,
                    
                    parameter_defs_new = list(self.component.parameters),
                    state_var_defs_new = list(self.component.state_variables),
                    assignment_defs_new = list(self.component.assignedvalues),
                    
                    eqns_timederivatives = self.td_eqns,
                    eqns_assignments = self.ass_eqns,
                    
                    floattype = self.float_type,
                    nbits=nbits,
                    intermediate_store_locs=self.intermediate_store_locs
                    )



        for f in ['sim1.cpp','a.out',output_filename, 'debug.log',]:
            if os.path.exists(f):
                os.unlink(f)

        self.compile_and_run(cfile)




    def compile_and_run(self, cfile):
         
        # Compile and run:


        with open( 'sim1.cpp','w') as f:
            f.write(cfile)
        print 
        print 'Compiling & Running:'
        
        
        
        hdfjive_path_incl = os.path.expanduser("~/hw/hdf-jive/include")
        hdfjive_path_lib = os.path.expanduser("~/hw/hdf-jive/lib/")
        
        
        c1 = "g++ -g sim1.cpp -lgmpxx -lgmp -Wall -Werror -std=gnu++0x -I%s -L%s -lhdfjive -lhdf5 -lhdf5_hl -I../../cpp/include/ " % (hdfjive_path_incl, hdfjive_path_lib)
        c2 = 'export LD_LIBRARY_PATH="%s:$LD_LIBRARY_PATH"; ./a.out' % hdfjive_path_lib
        
        #os.system("g++ -g sim1.cpp -lgmpxx -lgmp -Wall -Werror && ./a.out > /dev/null")
        subprocess.check_call(c1, shell=True)
        subprocess.check_call(c2, shell=True)


        self.results = CBasedEqnWriterFixedResultsProxy(self)

        return 
    
    
    
    
    
    
    
    
    
    
import pylab
import pylab as plt


class CBasedEqnWriterFixedResultsProxy(object):
    def __init__(self, eqnwriter):
        self.eqnwriter = eqnwriter


    def plot_func_exp(self):
        import tables
        h5file = tables.openFile("output.hd5")
        
        float_group = h5file.root._f_getChild('/simulation_fixed/float/variables/')
        time_array = h5file.root._f_getChild('/simulation_fixed/float/time').read()

        from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector

        from neurounits import ast
        func_call_nodes = EqnsetVisitorNodeCollector(self.eqnwriter.component).nodes[ ast.FunctionDefBuiltInInstantiation ]
        print func_call_nodes
        
        
        
        nbits = 10
        LUT_size = 2**nbits
        
        in_min_max = None
        
        for func_call_node in func_call_nodes:
            
            try:
                node_loc = self.eqnwriter.node_labels[ func_call_node ]
                 
                data = h5file.root._f_getChild('/simulation_fixed/float/operations/' + "op%d" % node_loc).read()
                
                print data.shape
                print time_array.shape
                
                
                in_data = data[:,0]
                out_data = data[:,1]
                
                in_min = np.min(in_data)
                in_max = np.max(in_data)
                out_min = np.min(out_data)
                out_max = np.max(out_data)
            
            
                if in_min_max == None:
                    in_min_max = (in_min, in_max)
                else:
                    in_min_max = (np.min([in_min,in_min_max[0]]), np.max([in_max, in_min_max[1]]) )
                    
                    
                
                f = pylab.figure()
                ax1 = f.add_subplot(3,1,1)
                ax2 = f.add_subplot(3,1,2)
                ax3 = f.add_subplot(3,1,3)
                
                
                
                x_space = np.linspace( in_min, in_max, num=2**(nbits+8))
                x_space_binned = np.linspace( in_min, in_max, num=LUT_size)
                 
                
                
                
                ax1.plot(time_array, in_data, label='in_data (in: %f to %f)' % (in_min, in_max) )
                ax2.plot(time_array, out_data, label='out_data (in: %f to %f)' % (out_min, out_max) )
                ax1.legend()
                ax2.legend()
                
                ax3.plot( x_space, np.exp(x_space) )
                #fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey=True)
                
                
                
                
                pylab.legend()
        
            except tables.exceptions.NoSuchNodeError, e :
                print 'Not such group!: ', e
        
        
        print 'In_min_max = ', in_min_max
        
        pylab.show()
    
     
     
     
     
     
     
    def plot_ranges(self):
        
        
        
        # Plot the variable values:
        for ast_node in self.eqnwriter.component.assignedvalues:
            print 'Plotting:', ast_node
        
     
        assert False
 
#  
#         import pylab
#         import numpy as np
#         from collections import defaultdict
#         import shutil
#  
#         if os.path.exists('output/'):
#             shutil.rmtree("output/")
#         if not os.path.exists('output/'):
#             os.makedirs('output/')
#          
#  
#  
#  
#         import numpy as np
#         data_int = np.genfromtxt('res_int.txt_int', names=True, delimiter=',', dtype=int)
#          
#          
#          
#         #pylab.show()
#         #pylab.plot(data_int['i'], data_int['tau_kf_n'] )
#         #pylab.show()
#          
#          
#         for index,name in enumerate(data_int.dtype.names):
#             if name in ['i', 'f0']:
#                 continue
#              
#             print 'Plotting:', name
#             res = data_int[name]
#              
#             f = pylab.figure()
#             ax = f.add_subplot(211)
#              
#             pc_of_dyn_range_used = ( float(np.ptp(res)) / 2**nbits ) * 100.0
#              
#             node = component.get_terminal_obj(name)
#             ann = self.annotations[node]
#             t1 = 'Distribution of values of: %s. (Using %.2f%% of possible range)' % (name,pc_of_dyn_range_used)
#             t2 = "Infered range: %s to %s" % (ann.val_min,  ann.val_max) 
#             f.suptitle(t1 + "\n" + t2)
#             ext = 2**(nbits-1)-1
#             ax.hist(res, range=(-ext,ext), bins=50 )
#             ax.axvspan( np.min(res), np.max(res), alpha=0.3, color='green')
#             #ax.set_xlim(-ext,ext)
#             ax.set_xlim(-ext*1.1,ext*1.1)
#             ax.axvline(-ext)
#             ax.axvline(ext)
#              
#             ax = f.add_subplot(212)
#             ax.plot(data_int['i'], res )
#              
#             pylab.savefig('output/variables_dynamicranges_%03d.png' % index)
#             pylab.close()
#              
#         print data_int
#          
#         #res_int.txt_int
#          
#  
#  
#  
#  
#  
#  
#  
#  
#  
#  
#         import re
#         r = re.compile(r"""OP\{(\d+)\}: (.*) => (.*) """, re.VERBOSE)
#         # Lets plot the graphs of ranges of each operation:
#         op_data = defaultdict(list)
#         with open('debug.log') as f:
#             for l in f.readlines():
#                 m = r.match(l)
#                 #print 
#                 op, operands, res = int(m.group(1)), m.group(2), int(m.group(3))
#                   
#                 op_data[ op ].append( (operands, res) )
#                 #assert m
#         op_data = [ (op, zip(*t)) for (op,t) in sorted(op_data.items()) ]
#          
#          
#          
#  
#          
#              
#              
#         for index, (op, (operands,res) ) in enumerate(op_data):    
#             print 'Operator: ', op, 'Results found:', len(res)
#             node = node_labeller.int_to_node[op]
#             ann = self.annotations[node] 
#             print node
#              
#             res = np.array( [int(r) for r in res] )
#              
#              
#             pc_of_dyn_range_used = ( float(np.ptp(res)) / 2**nbits ) * 100.0
#             f = pylab.figure()
#             ax = f.add_subplot(111)
#              
#             t1 = 'Distribution of values from operator: %s -- %.2f%% of range used -- [%d]' % ( repr(node), pc_of_dyn_range_used, op) 
#             t2 = "Infered range: %s to %s" % (ann.val_min,  ann.val_max)
#             f.suptitle(t1 + '\n' + t2)
#               
#              
#             #res_index = np.linspace( 0, 1.0, num=len(res)  )
#             print res
#              
#              
#              
#             ext = 2**(nbits-1)-1
#             ax.hist(res, range=(-ext,ext), bins=50 )
#             ax.axvspan( np.min(res), np.max(res), alpha=0.3, color='green')
#             ax.set_xlim(-ext*1.1,ext*1.1)
#             ax.axvline(-ext)
#             ax.axvline(ext)
#              
#              
#             pylab.savefig('output/operators_dynamicrange_%03d.png' % index)
#              
#             pylab.close()
#             #ax.scatter(res_index, res)
#             #pylab.show()
#              
#           
#           
#           
#          
#        
#          
#          
#          
#          
#          
#         #assert False
#          
#          
#  
#  
#  
 
 

