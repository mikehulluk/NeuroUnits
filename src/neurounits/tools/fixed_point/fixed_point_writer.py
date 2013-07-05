


import mako
from mako.template import Template



c_prog = r"""

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <gmpxx.h>
#include <iomanip>


#include <fenv.h>


const int nbits = ${nbits};
const int range_max = (1<<(nbits-1)) ;  


// Save-data function

double to_float(int val, int upscale)
{
    //double res =  ( double(val) * (1<<(upscale-bits+1) ) );
    double res =  ( double(val) * pow(2.0, upscale) / double(range_max) );
    std::cout << "to_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res; 
}

int from_float(double val, int upscale, int whoami=0)
{
    int res =  int(val * (double(range_max) / pow(2.0, upscale) ) ) ;
    std::cout << "from_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res;
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





NrnData data;



int main()
{

    //feenableexcept(-1);
    feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    
    


    
    std::ofstream results_file("${output_filename}");
    header(results_file);




    for(int i=0;i<3000;i++)
    {
        std::cout << "Loop: " << i << "\n";
        sim_step(data, i);

        
        // Results:
        //if( i%10==0)
        results_file << i << "," << data << "\n";
    }

    results_file.close();

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
    //const double t = time_step * dt;
    const int t = from_float(time_step * dt, 1);

    std::cout << "t: " << t << "\n";

    // Calculate assignments:
% for eqn in eqns_assignments:
    d.${eqn.lhs} = from_float( to_float( ${eqn.rhs},  ${eqn.rhs_annotation.fixed_scaling_power}), ${eqn.lhs_annotation.fixed_scaling_power}) ;
    ##//d.${eqn.lhs} =  ${eqn.rhs};
% endfor

    // Calculate delta's for all state-variables:
% for eqn in eqns_timederivatives:
    ##//d.d_${eqn.lhs} = from_float( to_float( ${eqn.rhs}, ${eqn.rhs_annotation.fixed_scaling_power}), ${eqn.lhs_annotation.fixed_scaling_power}, 2) ;
    float d_${eqn.lhs} = to_float( ${eqn.rhs} , ${eqn.rhs_annotation.fixed_scaling_power}) * dt;
    d.${eqn.lhs} += from_float( ( d_${eqn.lhs} ),  ${eqn.lhs_annotation.fixed_scaling_power} );
% endfor

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
    
    def __init__(self, annotations):
        self.annotations = annotations
        super(CBasedFixedWriter, self).__init__()
        
    def to_c(self, obj):
        return self.visit(obj)

    def VisitRegimeDispatchMap(self, o):
        assert len (o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0])

    def get_var_str(self, name):
        return "d.%s" % name



    def build_shift_string(self, src, shift):
        if shift == 0:
            return "(%s)" % src
        else:
            return "((%s) << %d )" % (src, shift)


    def DoOpSimple(self, o, symbol):
        print 'Creating AddSubOp', symbol
        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs]
        ann = self.annotations[o]
        return " from_float(to_float(%s, %d) %s to_float(%s, %d), %s) " % (self.visit(o.lhs), ann_lhs.fixed_scaling_power, symbol, self.visit(o.rhs), ann_rhs.fixed_scaling_power, ann.fixed_scaling_power )
    
    
    def VisitAddOp(self, o):
        return self.DoOpSimple(o, '+')
    def VisitSubOp(self, o):
        return self.DoOpSimple(o, '-')
    def VisitMulOp(self, o):
        return self.DoOpSimple(o, '*')
    def VisitDivOp(self, o):
        return self.DoOpSimple(o, '/')



    def VisitIfThenElse(self, o):
        #return "( (%s) ? (%s) : (%s) )" % (
        #            self.visit(o.predicate),
        #            self.visit(o.if_true_ast),
        #            self.visit(o.if_false_ast),
        #        )
       
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
        #ann = self.annotations[o]
        
        return "(to_float(%s, %d) < to_float(%s, %d) )" % ( self.visit(o.less_than), ann_lt.fixed_scaling_power,  self.visit(o.greater_than), ann_gt.fixed_scaling_power )

    def VisitFunctionDefInstantiation(self,o):
        
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'
        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast)
        ann_func = self.annotations[o]
        ann_param = self.annotations[param.rhs_ast]
        return """ from_float( exp( to_float( %s, %d) ), %d )""" %(param_term, ann_param.fixed_scaling_power, ann_func.fixed_scaling_power ) 
        
#         assert False
#         print o.parameters
#         param_list = sorted(o.parameters.values(), key=lambda p:p.symbol)
#         assert o.function_def.is_builtin()
#         func_name = {
#             '__exp__': 'exp'
#             }[o.function_def.funcname]
# 
#         return "%s(%s)" % (
#                 func_name,
#                 ",".join([self.visit(p.rhs_ast) for p in param_list])
#                 )
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
        
        print
        print 'Time derivatives:'
        for td in component.timederivatives:
            print 'Time Derivative:', repr(td)
            ann_lhs = annotations[td.lhs]
            ann_rhs = annotations[td.rhs_map]
            print '  Ann-LHS:', ann_lhs
            print '  Ann-RHS:', ann_rhs
        
        print
        #assert False
        
        
        self.component = component
        self.float_type = 'int'
        self.annotations = annotations

        self.writer = CBasedFixedWriter(annotations=annotations)


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
        for f in ['sim1.cpp','a.out',output_filename]:
            if os.path.exists(f):
                os.unlink(f)

        with open( 'sim1.cpp','w') as f:
            f.write(cfile)
        print 
        print 'Compiling & Running:'
        os.system("g++ -g sim1.cpp -lgmpxx -lgmp -Wall -Werror && ./a.out > /dev/null")





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






