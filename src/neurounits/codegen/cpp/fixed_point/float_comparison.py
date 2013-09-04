


import mako
from mako.template import Template



c_prog = r"""

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <gmpxx.h>

// Define the data-structures:
${DEF_DATASTRUCT}




mpf_class exp(const mpf_class& x)
{
    double X = x.get_d();
    double res = exp(X);
    ##std::cout  << "exp(" << X << ") ->" << res << "\n";
    return mpf_class(res);



}



// User functions
${DEF_USERFUNCS_DECL}
${DEF_USERFUNCS}

// Update-function
${DEF_UPDATE_FUNC}


// Save-data function


int main()
{
    //mpf_set_default_prec (1000);
    mpf_set_default_prec (64);
    //setprecision(100)

    NrnData data;


    std::ofstream results_file("${output_filename}");

    for(int i=0;i<10000;i++)
    {
        std::cout << "Loop: " << i << "\n";
        sim_step(data, i);
        //results_file << i << " "

        results_file << i << " ";
        results_file << data.V << " ";              // 1
        results_file << data.iNa << " ";            // 2
        results_file << data.iCa2 << " ";           // 3
        results_file << data.ca_m << " ";           // 4
        results_file << data.beta_ca_m << " ";      // 5
        results_file << "\n";

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
    ${p_def.datatype} ${p_def.name};
% endfor

    // Assignments:
% for a_def in assignment_defs:
    ${a_def.datatype} ${a_def.name};
% endfor

    // States:
% for sv_def in state_var_defs:
    ${sv_def.datatype} ${sv_def.name};
    ${sv_def.datatype} d_${sv_def.name};
% endfor
};



"""







nrn_update_internal_function = r"""
<% params = ','.join([ "%s %s" %(floattype, p) for p in sorted(func.parameters)] )
%>
inline ${floattype} user_${func.funcname}(${params})
% if not forward_declare:
{
    ##%for p in sorted(func.parameters):
    ##std::cout << "${p}:" << ${p} << "\n" ;
    ##% endfor

    return ${func_body};
}
% else:
;
% endif """




update_func = """
void sim_step(NrnData& d, int time_step)
{
    const ${floattype}  dt = 0.1e-3;
    const ${floattype} t = time_step * dt;

    // Calculate assignments:
% for eqn in eqns_assignments:
    d.${eqn.lhs} = ${eqn.rhs};
% endfor

    // Calculate delta's for all state-variables:
% for eqn in eqns_timederivatives:
    d.d_${eqn.lhs} = ${eqn.rhs};
    d.${eqn.lhs} += d.d_${eqn.lhs} * dt;
% endfor

}
"""








import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase 


class VarDef(object):
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype

class Eqn(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs





class CBasedFloatWriter(ASTVisitorBase):
    def to_c(self, obj):
        return self.visit(obj)

    def VisitRegimeDispatchMap(self, o):
        assert len (o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0])


    def get_var_str(self, name):
        return "d.%s" % name

    def VisitAddOp(self, o):
        return "( %s + %s )" % (self.visit(o.lhs), self.visit(o.rhs))
    def VisitSubOp(self, o):
        return "( %s - %s )" % (self.visit(o.lhs), self.visit(o.rhs))
    def VisitMulOp(self, o):
        return "( %s * %s )" % (self.visit(o.lhs), self.visit(o.rhs))
    def VisitDivOp(self, o):
        return "( %s / %s )" % (self.visit(o.lhs), self.visit(o.rhs))


    def VisitIfThenElse(self, o):
        return "( (%s) ? (%s) : (%s) )" % (
                    self.visit(o.predicate),
                    self.visit(o.if_true_ast),
                    self.visit(o.if_false_ast),
                )

    def VisitInEquality(self, o):
        return "(%s < %s)" % ( self.visit(o.lesser_than), self.visit(o.greater_than) )

    def VisitFunctionDefUserInstantiation(self,o):
        print o.parameters
        param_list = sorted(o.parameters.values(), key=lambda p:p.symbol)
        func_name = "user_%s" %  o.function_def.funcname


        return "%s(%s)" % (
                func_name,
                ",".join([self.visit(p.rhs_ast) for p in param_list])
                )

    def VisitFunctionDefBuiltInInstantiation(self,o):
        print o.parameters
        param_list = sorted(o.parameters.values(), key=lambda p:p.symbol)
    
        func_name = {
            '__exp__': 'exp'
            }[o.function_def.funcname]

        return "%s(%s)" % (
                func_name,
                ",".join([self.visit(p.rhs_ast) for p in param_list])
                )






    def VisitFunctionDefInstantiationParameter(self, o):
        return o.symbol

    def VisitFunctionDefParameter(self, o):
        return o.symbol

    def VisitStateVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitParameter(self, o):
        return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        return (o.value.float_in_si())

    def VisitAssignedVariable(self, o):
        return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        return "%e" % (o.value.float_in_si())

    def VisitSuppliedValue(self, o):
        return o.symbol


class CBasedEqnWriterFloat(object):
    def __init__(self, component, float_type, output_filename, annotations):
        self.component = component
        self.float_type = float_type







        def_DATASTRUCT = self.build_data_structure()
        def_UPDATEFUNC = self.build_update_function()

        func_tmpl = Template(nrn_update_internal_function)
        writer = CBasedFloatWriter()
        def_USERFUNCS = "\n".join( [func_tmpl.render(func=func, floattype=self.float_type, func_body=writer.visit(func.rhs)) for func in self.component.functiondefs] )
        def_USERFUNCS_DECL = "\n".join( [func_tmpl.render(func=func, floattype=self.float_type, func_body=writer.visit(func.rhs), forward_declare=True) for func in self.component.functiondefs] )


        cfile = Template(c_prog).render(
                    DEF_DATASTRUCT = def_DATASTRUCT,
                    DEF_UPDATE_FUNC = def_UPDATEFUNC ,
                    DEF_USERFUNCS = def_USERFUNCS ,
                    DEF_USERFUNCS_DECL = def_USERFUNCS_DECL ,
                    output_filename = output_filename,
                    )



        # Compile and run:
        for f in ['sim1.cpp','a.out',output_filename]:
            if os.path.exists(f):
                os.unlink(f)

        with open( 'sim1.cpp','w') as f:
            f.write(cfile)
        os.system("g++ -g sim1.cpp -lgmpxx -lgmp && ./a.out > /dev/null")





    def build_data_structure(self):
        parameter_defs =[ VarDef(p.symbol, self.float_type) for p in self.component.parameters]
        state_var_defs =[ VarDef(sv.symbol, self.float_type) for sv in self.component.state_variables]
        assignment_defs =[ VarDef(ass.symbol, self.float_type) for ass in self.component.assignedvalues]
        ds = Template(nrn_data_blk).render(
                parameter_defs = parameter_defs,
                state_var_defs = state_var_defs,
                assignment_defs = assignment_defs,
                floattype = self.float_type,
                )
        return ds



    def build_update_function(self, ):
        writer = CBasedFloatWriter()
        ordered_assignments = self.component.ordered_assignments_by_dependancies

        ass_eqns =[ Eqn(td.lhs.symbol, writer.to_c(td.rhs_map) ) for td in ordered_assignments]
        td_eqns = [ Eqn(td.lhs.symbol, writer.to_c(td.rhs_map) ) for td in self.component.timederivatives]

        func = Template(update_func).render(
                eqns_timederivatives = td_eqns,
                eqns_assignments = ass_eqns,
                floattype = self.float_type,
                )
        return func





