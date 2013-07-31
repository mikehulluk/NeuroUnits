


import mako
from mako.template import Template

import subprocess
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np

import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase





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


#include "safe_int.h"
#include "safe_int_utils.h"


#include "hdfjive.h"
const string output_filename = "${output_filename}";

// Data types used for storing in HDF5:
const hid_t hdf5_type_int = H5T_NATIVE_INT;
const hid_t hdf5_type_float = H5T_NATIVE_FLOAT;

typedef int T_hdf5_type_int;
typedef float T_hdf5_type_float;





//typedef int IntType;
typedef SafeInt32 IntType;



template<typename T> 
T inttype_from_long(long value)
{
    assert(0);
}

template<> 
int inttype_from_long(long value)
{
   return value;
}

template<> 
SafeInt32 inttype_from_long(long value)
{
   return SafeInt32::from_long(value);
}










typedef std::int64_t int64;
const int VAR_NBITS = ${nbits};



#define CALCULATE_FLOAT true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT true

#define CHECK_INT_FLOAT_COMPARISON true
const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT = 100;






#include "float_utils.h"


// Save-data function
typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;

double to_float(IntType val, IntType upscale)
{
    return FixedFloatConversion::to_float(val, upscale);
}

IntType from_float(double val, IntType upscale)
{
    return IntType(FixedFloatConversion::from_float(val, upscale));
}

using mh::auto_shift;
using mh::auto_shift64;




#include "float_utils.h"
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









IntType do_add_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

    IntType res_int = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local);


    if( SAVE_HDF5_INT )
    {
        HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value(v1) | (T_hdf5_type_int) get_value(v2) | (T_hdf5_type_int) get_value(res_int) ) ;
    }

    if(CALCULATE_FLOAT)
    {
        float res_fp_fl = to_float(v1,up1) + to_float(v2,up2);
        IntType res_fp = from_float(res_fp_fl, up_local);

        if( CHECK_INT_FLOAT_COMPARISON )
        {
            IntType diff = res_int - res_fp;
            //cout << "diff" << diff << "\n" << flush; 
            if(diff <0) diff = -diff;
            assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
        }

        if( SAVE_HDF5_FLOAT )
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
    }


    return res_int;
}


IntType do_sub_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

    IntType res_int = auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local);


    if( SAVE_HDF5_INT )
    {
        HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value(v1) | (T_hdf5_type_int) get_value(v2) | (T_hdf5_type_int) get_value(res_int) ) ;
    }

    if(CALCULATE_FLOAT)
    {
        float res_fp_fl = to_float(v1,up1) - to_float(v2,up2);
        IntType res_fp = from_float(res_fp_fl, up_local);

        if( CHECK_INT_FLOAT_COMPARISON )
        {
            IntType diff = res_int - res_fp;
            //cout << "diff" << diff << "\n" << flush; 
            if(diff <0) diff = -diff;
            assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
        }

        if( SAVE_HDF5_FLOAT )
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
    }

    return res_int;
}

IntType do_mul_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{
    // Need to promote to 64 bit:
    int64 v12 = (int64) get_value(v1) * (int64) get_value(v2);
    IntType res_int = inttype_from_long<IntType>( auto_shift64(v12, get_value(up1+up2-up_local-(VAR_NBITS-1)) ) ) ;



    if( SAVE_HDF5_INT )
    {
        HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value(v1) | (T_hdf5_type_int) get_value(v2) | (T_hdf5_type_int) get_value(res_int) ) ;
    }

    if(CALCULATE_FLOAT)
    {
        float res_fp_fl = to_float(v1,up1) * to_float(v2,up2);
        IntType res_fp = from_float(res_fp_fl, up_local);

        if( CHECK_INT_FLOAT_COMPARISON )
        {
            IntType diff = res_int - res_fp;
            //cout << "diff" << diff << "\n" << flush; 
            if(diff <0) diff = -diff;
            assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
        }

        if( SAVE_HDF5_FLOAT )
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
    }

    

    return res_int;

}



IntType do_div_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

    int64 v1_L = (int64) get_value(v1);
    int64 v2_L = (int64) get_value(v2);

    v1_L = auto_shift64(v1_L, (VAR_NBITS-1) );
    int64 v = v1_L/v2_L;
    v = auto_shift64(v, get_value( up1-up2 - up_local) );
    assert( v < (1<<(VAR_NBITS) ) );
    IntType res_int = inttype_from_long<IntType>(v);
    


    if( SAVE_HDF5_INT )
    {
        HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
            DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value(v1) | (T_hdf5_type_int) get_value(v2) | (T_hdf5_type_int) get_value(res_int) ) ;
    }

    if(CALCULATE_FLOAT)
    {
        float res_fp_fl = to_float(v1,up1) / to_float(v2,up2);
        IntType res_fp = from_float(res_fp_fl, up_local);

        if( CHECK_INT_FLOAT_COMPARISON )
        {
            IntType diff = res_int - res_fp;
            //cout << "diff" << "\n" << diff << flush; 
            if(diff <0) diff = -diff;
            assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
        }

        if( SAVE_HDF5_FLOAT )
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) | (T_hdf5_type_float) (to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
    }


    return res_int;

}

IntType int_exp(IntType v1, IntType up1, IntType up_local, IntType expr_id)
{

    float res_fp_fl = exp( to_float(v1,up1) );
    IntType res_fp = from_float( res_fp_fl, up_local);

    IntType res_int = lookuptables.exponential.get( v1, up1, up_local );


    IntType diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    //cout << "Diff: " << diff;
    //assert( (diff==0)  || (diff==1) || (diff==2) );



    // Write to HDF5:
    //////////////////
    // -- Floating point version:
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
            DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (to_float(v1,up1)) |  (T_hdf5_type_float) (res_fp_fl) ) ;

    if( SAVE_HDF5_INT )
    {
    // -- Integer version:
    HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value(expr_id) ).str())->append_buffer(
           DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value(v1) | (T_hdf5_type_int) get_value(res_int) ) ;
    }

    return res_int;

}




// Define the data-structures:
struct NrnData
{






    // Parameters:
% for p in parameter_defs_new:
    IntType ${p.symbol};      // Upscale: ${p.annotations['fixed-point-format'].upscale}
% endfor

    // Assignments:
% for ass in assignment_defs_new:
    IntType ${ass.symbol};      // Upscale: ${ass.annotations['fixed-point-format'].upscale}
% endfor

    // States:
% for sv_def in state_var_defs_new:
    IntType ${sv_def.symbol};    // Upscale: ${sv_def.annotations['fixed-point-format'].upscale}
    IntType d_${sv_def.symbol};
% endfor


<%
    cons = ',\n      '.join( 
                    ['%s(0)' % o.symbol for o in parameter_defs_new + assignment_defs_new ] +
                    ['%s(0),\n      d_%s(0)' % (o.symbol, o.symbol) for o in state_var_defs_new ] 
                    )
%>
    NrnData()
    : ${cons} 
    {}
};





// Update-function
void sim_step(NrnData& d, IntType time_step)
{
    const double dt = 0.1e-3;
    const double t_float = get_value(time_step) * dt;
    const IntType t = from_float(t_float, IntType(1));

    if(get_value(time_step)%100 == 0)
    {
        std::cout << "Loop: " << time_step << "\n";
        std::cout << "t: " << t << "\n";
    }

    // Calculate assignments:
% for eqn in eqns_assignments:
    d.${eqn.node.lhs.symbol} = ${eqn.rhs_cstr} ;
% endfor

    // Calculate delta's for all state-variables:
% for eqn in eqns_timederivatives:
    IntType d_${eqn.node.lhs.symbol} = ${eqn.rhs_cstr[0]} ;
    d.${eqn.node.lhs.symbol} += ${eqn.rhs_cstr[1]} ;
% endfor







    // Write to HDF5
    /* -------------------------------------------------------------------------------------------- */
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);

    // Time
    file->get_dataset("simulation_fixed/int/time")->append<T_hdf5_type_int>( get_value(t));
    file->get_dataset("simulation_fixed/float/time")->append<T_hdf5_type_float>(t_float);

    // Storage for state-variables and assignments:
    % for eqn in eqns_assignments:
    file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>( get_value( d.${eqn.node.lhs.symbol} ) );
    file->get_dataset("simulation_fixed/float/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( to_float(  d.${eqn.node.lhs.symbol},  IntType(${eqn.node.lhs.annotations['fixed-point-format'].upscale}) ) );
    % endfor

    % for eqn in eqns_timederivatives:
    file->get_dataset("simulation_fixed/int/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_int>( get_value( d.${eqn.node.lhs.symbol} ) );
    file->get_dataset("simulation_fixed/float/variables/${eqn.node.lhs.symbol}")->append<T_hdf5_type_float>( to_float(  d.${eqn.node.lhs.symbol},  IntType(${eqn.node.lhs.annotations['fixed-point-format'].upscale}) ) );
    % endfor
    /* -------------------------------------------------------------------------------------------- */


}






void initialise_statevars(NrnData& d)
{
    % for sv_def in state_var_defs_new:
    d.${sv_def.symbol} = auto_shift( IntType(${sv_def.initial_value.annotations['fixed-point-format'].const_value_as_int}),  IntType(${sv_def.initial_value.annotations['fixed-point-format'].upscale} - ${sv_def.annotations['fixed-point-format'].upscale} ) );
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


        sim_step(data, IntType(i));

    }




    printf("Simulation Complete\n");
    //assert(0);
    
}




"""












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

    def __init__(self, component, node_int_labels, dt, dt_upscale):


        self.intlabels = node_int_labels
        
        
        self.dt = dt
        self.dt_upscale = dt_upscale
        
        
        
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
        res = "do_%s_op( %s, IntType(%d), %s, IntType(%d), IntType(%d), IntType(%d))" % (
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
        return "( (%s) ? auto_shift(%s, IntType(%d)) : auto_shift(%s, IntType(%d)) )" % (
                    self.visit(o.predicate),
                    self.visit(o.if_true_ast),
                    o.annotations['fixed-point-format'].upscale - o.if_true_ast.annotations['fixed-point-format'].upscale,
                    self.visit(o.if_false_ast),
                    o.annotations['fixed-point-format'].upscale - o.if_false_ast.annotations['fixed-point-format'].upscale,
                    
                )



    def VisitInEquality(self, o):
        ann_lt_upscale = o.lesser_than.annotations['fixed-point-format'].upscale
        ann_gt_upscale = o.greater_than.annotations['fixed-point-format'].upscale
        
        if ann_lt_upscale < ann_gt_upscale:
            return "( ((%s)>>IntType(%d)) < ( (%s)) )" %( self.visit(o.lesser_than), (ann_gt_upscale-ann_lt_upscale),  self.visit(o.greater_than) )
        elif ann_lt_upscale > ann_gt_upscale:
            return "( (%s) < ( (%s)>>IntType(%d)))" %( self.visit(o.lesser_than), self.visit(o.greater_than), (ann_lt_upscale-ann_gt_upscale) )
        else:
            return "( (%s) < (%s) )" %( self.visit(o.lesser_than), self.visit(o.greater_than), (ann_gt_upscale-ann_lt_upscale) )


    def VisitFunctionDefUserInstantiation(self,o):
        assert False

    def VisitFunctionDefBuiltInInstantiation(self,o):
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'
        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast)
        ann_func_upscale = o.annotations['fixed-point-format'].upscale
        ann_param_upscale = param.rhs_ast.annotations['fixed-point-format'].upscale
        expr_num = self.intlabels[o]

        return """ int_exp( %s, IntType(%d), IntType(%d), IntType(%d) )""" %(param_term, ann_param_upscale, ann_func_upscale, expr_num )

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
        return "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int

    def VisitAssignedVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        return "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int

    def VisitSuppliedValue(self, o):
        return o.symbol


    def VisitEqnAssignmentByRegime(self, o):
        rhs_c = self.visit(o.rhs_map)
        return " auto_shift( %s, IntType(%d) )" % (rhs_c, o.rhs_map.annotations['fixed-point-format'].upscale - o.lhs.annotations['fixed-point-format'].upscale )


    def VisitTimeDerivativeByRegime(self, o):
        
        # Assume the delta_StateVariable format is the same as the state vairable:
        delta_upscale = o.lhs.annotations['fixed-point-format'].delta_upscale
    
        c1 = "from_float(  to_float( %s , IntType( %d )) * dt, IntType(%d)) " % ( self.visit(o.rhs_map), o.rhs_map.annotations['fixed-point-format'].upscale, delta_upscale  )
        c2 = "from_float( to_float( ( d_%s ), IntType(%d) ),  IntType(%d) )" % ( o.lhs.symbol, delta_upscale, o.lhs.annotations['fixed-point-format'].upscale)
        
        return c1, c2
        #float d_${eqn.node.lhs.symbol} = to_float( ${eqn.rhs_cstr} , IntType(${eqn.node.rhs_map.annotations['fixed-point-format'].upscale} )) * dt;
        #d.${eqn.node.lhs.symbol} = d.${eqn.node.lhs.symbol}  + from_float( ( d_${eqn.node.lhs.symbol} ),  IntType(${eqn.node.lhs.annotations['fixed-point-format'].upscale}) );







class CBasedEqnWriterFixed(object):
    def __init__(self, component, output_filename, nbits,):


        self.dt = 0.1e-3
        self.dt_upscale = int( np.ceil( np.log2 (self.dt)) )


        self.node_labeller = component.annotation_mgr._annotators['node-ids']
        self.node_labels = self.node_labeller.node_to_int
        intermediate_nodes = IntermediateNodeFinder(component).valid_nodes
        self.intermediate_store_locs = [("op%d" % self.node_labeller.node_to_int[o], o_number ) for (o, o_number) in intermediate_nodes.items()]



        self.component = component
        self.float_type = 'int'

        self.writer = CBasedFixedWriter(component=component, node_int_labels=self.node_labeller.node_to_int, dt=self.dt, dt_upscale=self.dt_upscale)
        self.nbits = nbits



        ordered_assignments = self.component.ordered_assignments_by_dependancies
        self.ass_eqns =[ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in ordered_assignments]
        self.td_eqns = [ Eqn(node=td, rhs_cstr=self.writer.to_c(td) ) for td in self.component.timederivatives]        
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

        from neurounits.tools.c_compilation import CCompiler, CCompilationSettings
        
        CCompiler.build_executable(src_text=cfile, 
                                   compilation_settings = CCompilationSettings(
                                                additional_include_paths=[os.path.expanduser("~/hw/hdf-jive/include"), os.path.abspath('../../cpp/include/') ], 
                                                additional_library_paths=[os.path.expanduser("~/hw/hdf-jive/lib/")], 
                                                libraries = ['gmpxx', 'gmp','hdfjive','hdf5','hdf5_hl'],
                                                compile_flags=['-Wall -Werror -Wfatal-errors -std=gnu++0x -g']),
                                   run=True)

        self.results = CBasedEqnWriterFixedResultsProxy(self)
        return










import pylab
import pylab as plt


class CBasedEqnWriterFixedResultsProxy(object):
    def __init__(self, eqnwriter):
        self.eqnwriter = eqnwriter











    def plot_ranges(self):
        import tables
        import sys


        h5file = tables.openFile("output.hd5")

        float_group = h5file.root._f_getChild('/simulation_fixed/float/variables/')
        time_array = h5file.root._f_getChild('/simulation_fixed/float/time').read()


        downscale = 10
        # Plot the variable values:
        for ast_node in self.eqnwriter.component.assignedvalues+self.eqnwriter.component.state_variables:
            print 'Plotting:', ast_node
            data_float = h5file.root._f_getChild('/simulation_fixed/float/variables/%s' % ast_node.symbol).read()
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
                
                data_float = h5file.root._f_getChild('/simulation_fixed/float/operations/' + "op%d" % ast_node.annotations['node-id']).read()
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
