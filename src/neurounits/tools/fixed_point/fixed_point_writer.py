


import mako
from mako.template import Template

import subprocess

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



#include "hdfjive.h"


const string output_filename = "output.hd5";



typedef std::int64_t int64;


const int nbits = ${nbits};
const int range_max = (1<<(nbits-1)) ;  


// Save-data function

double to_float(int val, int upscale)
{
    //double res =  ( double(val) * (1<<(upscale-bits+1) ) );
    double res =  ( double(val) * pow(2.0, upscale) / double(range_max) );
    //std::cout << "to_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res; 
}

int from_float(double val, int upscale, int whoami=0)
{
    int res =  int(val * (double(range_max) / pow(2.0, upscale) ) ) ;
    //std::cout << "from_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res;
}





FILE* fdebug;
void  dump_op_info(int op, int input1, int input2, int output)
{
    std::stringstream os;
    os << "OP{" << op <<"}: " << input1 << " " << input2 << " => " << output << "\n";
    fprintf(fdebug, "%s", os.str().c_str() );
    

} 



int auto_shift(int n, int m)
{
    //std::cout << "\n" << "n/m:" << n << "/" << m << "\n";
    if(m==0)
    {
        return n;
    }
    if( m>0)
    {
        return n << m;
    }
    else 
    {
       return n >> -m;
    }
}


long auto_shift64(long n, int m)
{
    //std::cout << "\n" << "n/m:" << n << "/" << m << "\n";
    if(m==0)
    {
        return n;
    }
    if( m>0)
    {
        return n << m;
    }
    else 
    {
       return n >> -m;
    }
}




int do_add_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) + to_float(v2,up2), up_local);        
    int res_int = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local); 
    
    
    //std::cout << "\nAdd OP:" << res_fp << " and " << res_int  << "\n";
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    assert( (diff==0)  || (diff==1));
    
    // Store info:   
    dump_op_info(expr_id, v1, v2, res_fp); 
    return res_int;    
} 



// Basic Functions:
 // Convert into integer operations:
    //double f1 = ( double(v1) * pow(2.0, up1) / double(range_max) ) + ( double(v2) * pow(2.0, up2) / double(range_max) );
    //int res_int = int(f1 * (double(range_max) / pow(2.0, up_local) ) ) ;



int do_sub_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) - to_float(v2,up2), up_local);
    
    
    // Convert into integer operations:
    //double f1 = ( double(v1) * pow(2.0, up1) / double(range_max) ) - ( double(v2) * pow(2.0, up2) / double(range_max) );
    //int res_int = int(f1 * (double(range_max) / pow(2.0, up_local) ) ) ;
    
    int res_int = auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local); 
    
    
    //std::cout << "\nSub OP:" << res_fp << " and " << res_int  << "\n";
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    assert( (diff==0)  || (diff==1));
    
    // Store info:  
    dump_op_info(expr_id, v1, v2, res_fp);   
    return res_int;    
} 

int do_mul_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) * to_float(v2,up2), up_local);
    
    
    // Convert into integer operations:
   
    // Need to promote to 64 bit:
    int64 v12 = (int64)v1* (int64)v2;
    int res_int = auto_shift64(v12, (up1+up2-up_local-(nbits-1)) );
    
    //std::cout << "\nMul OP:" << res_fp << " and " << res_int  << "\n";
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    assert( (diff==0)  || (diff==1));
    
    // Store info:  
    dump_op_info(expr_id, v1, v2, res_fp);   
    return res_int;    
} 



int do_div_op(int v1, int up1, int v2, int up2, int up_local, int expr_id)
{
    int res_fp = from_float(to_float(v1,up1) / to_float(v2,up2), up_local);
    
    int64 v1_L = (int64) v1;
    int64 v2_L = (int64) v2;
    
    v1_L = auto_shift64(v1_L, (nbits-1) );
    
    
    int64 v = v1_L/v2_L;
    v = auto_shift64(v, up1-up2 - up_local);
    
    assert( v < (1<<(nbits) ) );
    
    
    int res_int = v; 
    
    
    //std::cout << "\nDiv OP:" << res_fp << " and " << res_int  << "\n";
    int diff = res_int - res_fp;
    if(diff <0) diff = -diff;
    
    
    // Store info:  
    dump_op_info(expr_id, v1, v2, res_fp);   
    return res_int;    
} 

int int_exp(int v1, int up1, int up_local, int expr_id)
{
    int res_fp = from_float( exp( to_float(v1,up1) ), up_local );
    
    
    //dump_op_info(expr_id, v1, v2, res_fp); 
    
    return res_fp;

}




// Define the data-structures:
${DEF_DATASTRUCT}

// Update-function
${DEF_UPDATE_FUNC}





std::ostream& operator << (std::ostream& o, const NrnData& d)
{
   
    % for a_def in assignment_defs:
    o << to_float( d.${a_def.name}, ${a_def.annotation.fixed_scaling_power} )  << ","; 
    % endfor
        
    % for sv_def in state_var_defs:
    o << to_float( d.${sv_def.name}, ${sv_def.annotation.fixed_scaling_power} )  << ","; 
    % endfor
    
    return o;
}



void write_float(std::ostream& o, const NrnData& d)
{
   
    % for a_def in assignment_defs:
    o << to_float( d.${a_def.name}, ${a_def.annotation.fixed_scaling_power} )  << ","; 
    % endfor
        
    % for sv_def in state_var_defs:
    o << to_float( d.${sv_def.name}, ${sv_def.annotation.fixed_scaling_power} )  << ","; 
    % endfor
}


void write_int(std::ostream& o, const NrnData& d)
{
   
    % for a_def in assignment_defs:
    o << d.${a_def.name}  << ","; 
    % endfor
        
    % for sv_def in state_var_defs:
    o << d.${sv_def.name}  << ","; 
    % endfor
}







std::ostream& header(std::ostream& o)
{          
    o << "i,";
    % for a_def in assignment_defs:
    o << "${a_def.name}" << ","; 
    % endfor
        
    % for sv_def in state_var_defs:
    o << "${sv_def.name}" << ","; 
    % endfor
    
    o << "\n";
    
    return o;   
}



void initialise_statevars(NrnData& d)
{          
    % for sv_def in state_var_defs:
    d.${sv_def.name} =  ${sv_def.annotation.initial_value};
    % endfor   
}




void setup_hdf5()
{
    
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
    
    // Time
    file->get_group("simulation-fixed/float")->create_dataset("time", HDF5DataSet2DStdSettings(1) );
    file->get_group("simulation-fixed/int")->create_dataset("time", HDF5DataSet2DStdSettings(1) );
    
    // Storage for state-variables and assignments:
    % for sv_def in state_var_defs:
    file->get_group("simulation-fixed/float/variables/")->create_dataset("${sv_def.name}", HDF5DataSet2DStdSettings(1) );
    file->get_group("simulation-fixed/int/variables/")->create_dataset("${sv_def.name}", HDF5DataSet2DStdSettings(1) );
    % endfor   
    
    % for ass_def in assignment_defs:
    file->get_group("simulation-fixed/float/variables/")->create_dataset("${ass_def.name}", HDF5DataSet2DStdSettings(1) );
    file->get_group("simulation-fixed/int/variables/")->create_dataset("${ass_def.name}", HDF5DataSet2DStdSettings(1) );
    % endfor   


    // Storage for the intermediate values in calculations:

    
}




int main()
{

    //feenableexcept(-1);
    feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    
    
    
    
    setup_hdf5();
    

    fdebug = fopen("debug.log","w");
    
    std::ofstream results_file_float("${output_filename}");
    std::ofstream results_file_int("${output_filename}_int");
    header(results_file_float);
    header(results_file_int);

    NrnData data;
    initialise_statevars(data);



    for(int i=0;i<3000;i++)
    {
        std::cout << "Loop: " << i << "\n";
        sim_step(data, i);

        
        // Results:
        results_file_int << i << ",";
        write_int( results_file_int, data); 
        results_file_int << "\n";

        
        results_file_float << i << ",";
        write_float( results_file_float, data); 
        results_file_float << "\n";
        
    }

    results_file_float.close();
    results_file_int.close();
    fclose(fdebug);
    

    printf("Simulation Complete\n");
}




"""




nrn_data_blk = r"""
struct NrnData
{
    // Parameters:
% for p_def in parameter_defs:
    ${p_def.datatype} ${p_def.name};      // Upscale: ${p_def.annotation.fixed_scaling_power}
% endfor

    // Assignments:
% for a_def in assignment_defs:
    ${a_def.datatype} ${a_def.name};      // Upscale: ${a_def.annotation.fixed_scaling_power}
% endfor

    // States:
% for sv_def in state_var_defs:
    ${sv_def.datatype} ${sv_def.name};    // Upscale: ${sv_def.annotation.fixed_scaling_power}
    ${sv_def.datatype} d_${sv_def.name};
% endfor
};



"""









update_func = r"""
void sim_step(NrnData& d, int time_step)
{
    const double dt = 0.1e-3;
    const double t_float = time_step * dt;
    const int t = from_float(t_float, 1);

    std::cout << "t: " << t << "\n";

    // Calculate assignments:
% for eqn in eqns_assignments:
    d.${eqn.lhs} = from_float( to_float( ${eqn.rhs},  ${eqn.rhs_annotation.fixed_scaling_power}), ${eqn.lhs_annotation.fixed_scaling_power}) ;
% endfor

    // Calculate delta's for all state-variables:
% for eqn in eqns_timederivatives:
    float d_${eqn.lhs} = to_float( ${eqn.rhs} , ${eqn.rhs_annotation.fixed_scaling_power}) * dt;
    d.${eqn.lhs} += from_float( ( d_${eqn.lhs} ),  ${eqn.lhs_annotation.fixed_scaling_power} );
% endfor    
    
    
    
    
    
    // Write to HDF5
    /* -------------------------------------------------------------------------------------------- */
    HDF5FilePtr file = HDFManager::getInstance().get_file(output_filename);
    
    // Time
    file->get_dataset("simulation-fixed/int/time")->append(t);
    file->get_dataset("simulation-fixed/float/time")->append(t_float);
    
    // Storage for state-variables and assignments:
    % for eqn in eqns_assignments:
    file->get_dataset("simulation-fixed/int/variables/${eqn.lhs}")->append( d.${eqn.lhs} );
    file->get_dataset("simulation-fixed/float/variables/${eqn.lhs}")->append( to_float(  d.${eqn.lhs},  ${eqn.lhs_annotation.fixed_scaling_power} ) );
    % endfor   
    
    % for eqn in eqns_timederivatives:
    file->get_dataset("simulation-fixed/int/variables/${eqn.lhs}")->append( d.${eqn.lhs} );
    file->get_dataset("simulation-fixed/float/variables/${eqn.lhs}")->append( to_float(  d.${eqn.lhs},  ${eqn.lhs_annotation.fixed_scaling_power} ) );
    % endfor   
    /* -------------------------------------------------------------------------------------------- */
    
    
    
    
    
    


}
"""








import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase 


class VarDef(object):
    def __init__(self, name, annotation):
        self.name = name
        self.annotation = annotation
        self.datatype = 'int'
class Eqn(object):
    def __init__(self, lhs, rhs, lhs_annotation, rhs_annotation):
        self.lhs = lhs
        self.rhs = rhs
        
        self.lhs_annotation = lhs_annotation 
        self.rhs_annotation = rhs_annotation












class CBasedFixedWriter(ASTVisitorBase):
    
    def __init__(self, annotations, component, node_int_labels):
        self.annotations = annotations
        
       
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
        scale_lhs = self.annotations[o.lhs].fixed_scaling_power
        scale_rhs = self.annotations[o.rhs].fixed_scaling_power  
        scale_self = self.annotations[o].fixed_scaling_power
        expr_lhs = self.visit(o.lhs)
        expr_rhs = self.visit(o.rhs)
        expr_num = self.intlabels[o]
        print expr_num,  scale_self
        res = "do_%s_op( %s, %d, %s, %d, %d, %d)" % (
                                            op,
                                            expr_lhs, scale_lhs,
                                            expr_rhs, scale_rhs,
                                            scale_self, expr_num,
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
                    self.annotations[o.if_true_ast].fixed_scaling_power,
                    self.visit(o.if_false_ast),
                    self.annotations[o.if_false_ast].fixed_scaling_power,
                    self.annotations[o].fixed_scaling_power,
                ) 
        
        
        
        

    def VisitInEquality(self, o):
        ann_lt = self.annotations[o.less_than]
        ann_gt = self.annotations[o.greater_than]   
        return "(to_float(%s, %d) < to_float(%s, %d) )" % ( self.visit(o.less_than), ann_lt.fixed_scaling_power,  self.visit(o.greater_than), ann_gt.fixed_scaling_power )


    def VisitFunctionDefInstantiation(self,o):        
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'
        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast)
        ann_func = self.annotations[o]
        ann_param = self.annotations[param.rhs_ast]
        expr_num = self.intlabels[o]
        
        return """ int_exp( %s, %d, %d, %d )""" %(param_term, ann_param.fixed_scaling_power, ann_func.fixed_scaling_power, expr_num ) 

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
        return "%d" % self.annotations[o].value_as_int
        #return (o.value.float_in_si())

    def VisitAssignedVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        return "%d" % self.annotations[o].value_as_int
        #return "%e" % (o.value.float_in_si())

    def VisitSuppliedValue(self, o):
        return o.symbol


class CBasedEqnWriterFixed(object):
    def __init__(self, component, output_filename, annotations, nbits):
        
        
        
        from neurounits.visitors.common.node_label_with_integers import NodeToIntLabeller
        
        node_labeller = NodeToIntLabeller(component)
        
        
        self.component = component
        self.float_type = 'int'
        self.annotations = annotations

        self.writer = CBasedFixedWriter(annotations=annotations, component=component, node_int_labels=node_labeller.node_to_int)


        self.parameter_defs =[ VarDef(p.symbol, annotation=self.annotations[p]) for p in self.component.parameters]
        self.state_var_defs =[ VarDef(sv.symbol, annotation=self.annotations[sv]) for sv in self.component.state_variables]
        self.assignment_defs =[ VarDef(ass.symbol, annotation=self.annotations[ass]) for ass in self.component.assignedvalues]

        ordered_assignments = self.component.ordered_assignments_by_dependancies
        self.ass_eqns =[ Eqn(td.lhs.symbol, self.writer.to_c(td.rhs_map), lhs_annotation=self.annotations[td.lhs], rhs_annotation=self.annotations[td.rhs_map]) for td in ordered_assignments]
        self.td_eqns = [ Eqn(td.lhs.symbol, self.writer.to_c(td.rhs_map), lhs_annotation=self.annotations[td.lhs], rhs_annotation=self.annotations[td.rhs_map]) for td in self.component.timederivatives]
        self.td_eqns = sorted(self.td_eqns, key=lambda o: o.lhs.lower())
                

        def_DATASTRUCT = self.build_data_structure()
        def_UPDATEFUNC = self.build_update_function()

      
        cfile = Template(c_prog).render(
                    DEF_DATASTRUCT = def_DATASTRUCT,
                    DEF_UPDATE_FUNC = def_UPDATEFUNC ,
                    output_filename = output_filename,
                    state_var_defs = self.state_var_defs,
                    assignment_defs = self.assignment_defs,
                    nbits=nbits
                    )

        # Compile and run:
        for f in ['sim1.cpp','a.out',output_filename, 'debug.log',]:
            if os.path.exists(f):
                os.unlink(f)

        with open( 'sim1.cpp','w') as f:
            f.write(cfile)
        print 
        print 'Compiling & Running:'
        
        
        
        hdfjive_path_incl = os.path.expanduser("~/hw/hdf-jive/include")
        hdfjive_path_lib = os.path.expanduser("~/hw/hdf-jive/lib/")
        
        
        c1 = "g++ -g sim1.cpp -lgmpxx -lgmp -Wall -Werror -std=gnu++0x -I%s -L%s -lhdfjive -lhdf5 -lhdf5_hl " % (hdfjive_path_incl, hdfjive_path_lib)
        c2 = 'export LD_LIBRARY_PATH="%s:$LD_LIBRARY_PATH"; ./a.out' % hdfjive_path_lib
        
        #os.system("g++ -g sim1.cpp -lgmpxx -lgmp -Wall -Werror && ./a.out > /dev/null")
        subprocess.check_call(c1, shell=True)
        subprocess.check_call(c2, shell=True)



        return 


        import pylab
        import numpy as np
        from collections import defaultdict
        import shutil

        if os.path.exists('output/'):
            shutil.rmtree("output/")
        if not os.path.exists('output/'):
            os.makedirs('output/')
        



        import numpy as np
        data_int = np.genfromtxt('res_int.txt_int', names=True, delimiter=',', dtype=int)
        
        
        
        #pylab.show()
        #pylab.plot(data_int['i'], data_int['tau_kf_n'] )
        #pylab.show()
        
        
        for index,name in enumerate(data_int.dtype.names):
            if name in ['i', 'f0']:
                continue
            
            print 'Plotting:', name
            res = data_int[name]
            
            f = pylab.figure()
            ax = f.add_subplot(211)
            
            pc_of_dyn_range_used = ( float(np.ptp(res)) / 2**nbits ) * 100.0
            
            node = component.get_terminal_obj(name)
            ann = self.annotations[node]
            t1 = 'Distribution of values of: %s. (Using %.2f%% of possible range)' % (name,pc_of_dyn_range_used)
            t2 = "Infered range: %s to %s" % (ann.val_min,  ann.val_max) 
            f.suptitle(t1 + "\n" + t2)
            ext = 2**(nbits-1)-1
            ax.hist(res, range=(-ext,ext), bins=50 )
            ax.axvspan( np.min(res), np.max(res), alpha=0.3, color='green')
            #ax.set_xlim(-ext,ext)
            ax.set_xlim(-ext*1.1,ext*1.1)
            ax.axvline(-ext)
            ax.axvline(ext)
            
            ax = f.add_subplot(212)
            ax.plot(data_int['i'], res )
            
            pylab.savefig('output/variables_dynamicranges_%03d.png' % index)
            pylab.close()
            
        print data_int
        
        #res_int.txt_int
        










        import re
        r = re.compile(r"""OP\{(\d+)\}: (.*) => (.*) """, re.VERBOSE)
        # Lets plot the graphs of ranges of each operation:
        op_data = defaultdict(list)
        with open('debug.log') as f:
            for l in f.readlines():
                m = r.match(l)
                #print 
                op, operands, res = int(m.group(1)), m.group(2), int(m.group(3))
                 
                op_data[ op ].append( (operands, res) )
                #assert m
        op_data = [ (op, zip(*t)) for (op,t) in sorted(op_data.items()) ]
        
        
        

        
            
            
        for index, (op, (operands,res) ) in enumerate(op_data):    
            print 'Operator: ', op, 'Results found:', len(res)
            node = node_labeller.int_to_node[op]
            ann = self.annotations[node] 
            print node
            
            res = np.array( [int(r) for r in res] )
            
            
            pc_of_dyn_range_used = ( float(np.ptp(res)) / 2**nbits ) * 100.0
            f = pylab.figure()
            ax = f.add_subplot(111)
            
            t1 = 'Distribution of values from operator: %s -- %.2f%% of range used -- [%d]' % ( repr(node), pc_of_dyn_range_used, op) 
            t2 = "Infered range: %s to %s" % (ann.val_min,  ann.val_max)
            f.suptitle(t1 + '\n' + t2)
             
            
            #res_index = np.linspace( 0, 1.0, num=len(res)  )
            print res
            
            
            
            ext = 2**(nbits-1)-1
            ax.hist(res, range=(-ext,ext), bins=50 )
            ax.axvspan( np.min(res), np.max(res), alpha=0.3, color='green')
            ax.set_xlim(-ext*1.1,ext*1.1)
            ax.axvline(-ext)
            ax.axvline(ext)
            
            
            pylab.savefig('output/operators_dynamicrange_%03d.png' % index)
            
            pylab.close()
            #ax.scatter(res_index, res)
            #pylab.show()
            
         
         
         
        
      
        
        
        
        
        
        #assert False
        
        


    def build_data_structure(self):

        ds = Template(nrn_data_blk).render(
                parameter_defs = self.parameter_defs,
                state_var_defs = self.state_var_defs,
                assignment_defs = self.assignment_defs,
                floattype = self.float_type,
                )
        return ds



    def build_update_function(self, ):
        
        



        func = Template(update_func).render(
                eqns_timederivatives = self.td_eqns,
                eqns_assignments = self.ass_eqns,
                floattype = self.float_type,
                )
        return func






