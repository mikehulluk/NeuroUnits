



import neurounits

import numpy as np
import pylab




src_text = """
define_component simple_leak {
    from std.math import exp

    iInj = [4pA] if [t > 50ms] else [0pA]
    Cap = 10 pF
    gLk = 1.25 nS
    eLk = -50mV

    iLk = gLk * (eLk-V) #* glk_noise
    V' = (1/Cap) * (iInj + iLk)


    
    AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))
  
    alpha_n = AlphaBetaFunc(v=V, A=0.462ms-1, B=8.2e-3ms-1 mV-1, C=4.59, D=-4.21mV,E=-11.97mV)
    beta_n =  AlphaBetaFunc(v=V, A=0.0924ms-1, B=-1.353e-3ms-1 mV-1, C=1.615, D=2.1e5mV, E=3.3e5mV)
    inf_n = alpha_n / (alpha_n + beta_n)
    tau_n = 1.0 / (alpha_n + beta_n)
    n' = (inf_n - n) / tau_n
    iKs = gKs * (eK-V) * n*n
    gKs = 10 nS
    eK = -70mV

 <=> INPUT t:(ms)
 #<=> PARAMETER glk_noise:()

}

"""












library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
comp = library_manager['simple_leak']






## Check it works:
#res = comp.simulate(
#                times = np.arange(0, 0.1,0.00001),
#                initial_state_values={'V':'-60mV'},
#                parameters={'glk_noise': '1.2'},
#                )
#res.auto_plot()



import mako
from mako.template import Template







c_prog = r"""

#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>


// Define the data-structures:
${DEF_DATASTRUCT}



// User functions
${DEF_USERFUNCS_DECL}
${DEF_USERFUNCS}

// Update-function
${DEF_UPDATE_FUNC}


// Save-data function


int main()
{

    NrnData data;


    std::ofstream results_file("${output_filename}");

    for(int i=0;i<10000;i++)
    {
        sim_step(data, i);
        results_file << i << " " << data.V << "\n";
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



class VarDef(object):
    def __init__(self, name, datatype):
        self.name = name
        self.datatype = datatype

class Eqn(object):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs





from neurounits.visitors import ASTVisitorBase
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
        return "(%s < %s)" % ( self.visit(o.less_than), self.visit(o.greater_than) )

    def VisitFunctionDefInstantiation(self,o):
        print o.parameters
        param_list = sorted(o.parameters.values(), key=lambda p:p.symbol)
        if o.function_def.is_builtin():
            func_name = {
                '__exp__': 'exp'
                }[o.function_def.funcname]
        
        else:
            func_name = "user_%s" %  o.function_def.funcname


        return "%s(%s)" % (
                func_name,
                ",".join([self.visit(p.rhs_ast) for p in param_list]) 
                )
    def VisitFunctionDefInstantiationParater(self, o):
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


class CBasedEqnWriter(object):
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
        os.system("g++ sim1.cpp && ./a.out")





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

        from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
        from neurounits.units_misc import LookUpDict
        ordered_assigned_values =  VisitorFindDirectSymbolDependance.get_assignment_dependancy_ordering(self.component)
        ordered_assignments =  [LookUpDict(self.component.assignments).get_single_obj_by(lhs=av) for av in ordered_assigned_values]
        
        ass_eqns =[ Eqn(td.lhs.symbol, writer.to_c(td.rhs_map) ) for td in ordered_assignments]
        td_eqns = [ Eqn(td.lhs.symbol, writer.to_c(td.rhs_map) ) for td in self.component.timederivatives]

        func = Template(update_func).render(
                eqns_timederivatives = td_eqns,
                eqns_assignments = ass_eqns,
                floattype = self.float_type,
                )
        return func






class VariableAnnotation(object):
    pass




CBasedEqnWriter(comp, float_type='float',  output_filename='res_float.txt',  annotations=[] )
CBasedEqnWriter(comp, float_type='double', output_filename='res_double.txt',  annotations=[] )

data_float = np.loadtxt('res_float.txt')
pylab.plot(data_float[:,0], data_float[:,1], label='float' )

data_double = np.loadtxt('res_double.txt')
pylab.plot(data_double[:,0], data_double[:,1], label='double' )
pylab.legend()


pylab.show()


