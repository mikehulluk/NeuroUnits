



import neurounits

import numpy as np
import pylab




src_text = """
define_component simple_leak {
    from std.math import exp

    iInj = [50pA] if [t > 50ms] else [0pA]
    Cap = 10 pF
    gLk = 1.25 nS
    eLk = -50mV

    iLk = gLk * (eLk-V) * glk_noise
    #V' = (1/Cap) * (iInj + iLk + iKs + iKf + iNa + iCa)
    V' = (1/Cap) * (iInj + iLk + iKs + iKf + iNa)


    glk_noise = 1.1

    AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))

    eK = -80mV
    eNa = 50mV
    gKs = 10.0 nS
    gKf = 12.5 nS
    gNa = 250 nS

    # Slow Potassium (Ks):
    alpha_ks_n = AlphaBetaFunc(v=V, A=0.462ms-1, B=8.2e-3ms-1 mV-1, C=4.59, D=-4.21mV,E=-11.97mV)
    beta_ks_n =  AlphaBetaFunc(v=V, A=0.0924ms-1, B=-1.353e-3ms-1 mV-1, C=1.615, D=2.1e5mV, E=3.3e5mV)
    inf_ks_n = alpha_ks_n / (alpha_ks_n + beta_ks_n)
    tau_ks_n = 1.0 / (alpha_ks_n + beta_ks_n)
    ks_n' = (inf_ks_n - ks_n) / tau_ks_n
    iKs = gKs * (eK-V) * ks_n*ks_n


    # Fast potassium (Kf):
    alpha_kf_n = AlphaBetaFunc(v=V, A=5.06ms-1, B=0.0666ms-1 mV-1, C=5.12, D=-18.396mV,E=-25.42mV)
    beta_kf_n =  AlphaBetaFunc(v=V, A=0.505ms-1, B=0.0ms-1 mV-1, C=0.0, D=28.7mV, E=34.6mV)
    inf_kf_n = alpha_kf_n / (alpha_kf_n + beta_kf_n)
    tau_kf_n = 1.0 / (alpha_kf_n + beta_kf_n)
    kf_n' = (inf_kf_n - kf_n) / tau_kf_n
    iKf = gKf * (eK-V) * kf_n*kf_n * kf_n*kf_n

    # Sodium (Kf):
    alpha_na_m = AlphaBetaFunc(v=V, A=8.67ms-1, B=0.0ms-1 mV-1, C=1.0, D=-1.01mV,E=-12.56mV)
    beta_na_m =  AlphaBetaFunc(v=V, A=3.82ms-1, B=0.0ms-1 mV-1, C=1.0, D=9.01mV, E=9.69mV)
    inf_na_m = alpha_na_m / (alpha_na_m + beta_na_m)
    tau_na_m = 1.0 / (alpha_na_m + beta_na_m)
    na_m' = (inf_na_m - na_m) / tau_na_m

    alpha_na_h = AlphaBetaFunc(v=V, A=0.08ms-1, B=0.0ms-1 mV-1, C=0.0, D=38.88mV,E=26.0mV)
    beta_na_h =  AlphaBetaFunc(v=V, A=4.08ms-1, B=0.0ms-1 mV-1, C=1.0, D=-5.09mV, E=-10.21mV)
    inf_na_h = alpha_na_h / (alpha_na_h + beta_na_h)
    tau_na_h = 1.0 / (alpha_na_h + beta_na_h)
    na_h' = (inf_na_h - na_h) / tau_na_h

    iNa = gNa * (eNa-V) * na_m * na_m * na_m * na_h


    # Calcium:
    alpha_ca_m = AlphaBetaFunc(v=V, A=4.05ms-1, B=0.0ms-1 mV-1, C=1.0, D=-15.32mV,E=-13.57mV)
    beta_ca_m_1 =  AlphaBetaFunc(v=V, A=1.24ms-1, B=0.093ms-1 mV-1, C=-1.0, D=10.63mV, E=1.0mV)
    beta_ca_m_2 =  AlphaBetaFunc(v=V, A=1.28ms-1, B=0.0ms-1 mV-1, C=1.0, D=5.39mV, E=12.11mV)
    beta_ca_m =  [beta_ca_m_1] if [ V<-25mV] else [beta_ca_m_2]
    inf_ca_m = alpha_ca_m / (alpha_ca_m + beta_ca_m)
    tau_ca_m = 1.0 / (alpha_ca_m + beta_ca_m)
    ca_m' = (inf_ca_m - ca_m) / tau_ca_m

    pca = {0.16 (m m m)/s} * 1e-6
    F = 96485 C / mol
    R = 8.3144 J/ (mol K)
    T = 300K
    Cai = 100 nM
    Cao = 10 mM
    nu = ( (2.0 *  F) / (R*T) ) * V ;
    exp_neg_nu = exp( -1. * nu );
    #iCa2 =  -2.0 * 1.e-3 * pca * nu * F * ( Cai - Cao*exp_neg_nu) / (1-exp_neg_nu) *  ca_m * ca_m
    iCa2 = [4pA] if [t < 0ms] else [4pA]
    iCa =  -3pA


    <=> INPUT t:(ms)

}

"""












library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
comp = library_manager['simple_leak']





from neurounits.visitors import ASTVisitorBase
import  neurounits.ast as ast
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing




    ##def VisitFunctionDefInstantiation(self, o):
    #def do_visit(self, o):
    #    print '    == Cloning Subfunction!'

    #    # Clone the parameters:
    #    parameters_new = {}
    #    for param_name, func_call_param in o.parameters.items():

    #        parameters_new[param_name] = self.visit(func_call_param.rhs_ast)
#ast#.FunctionDefParameterInstantiation(
    #                                        #rhs_ast=self.visit(func_call_param.rhs_ast),
    #                                        #symbol=func_call_param.symbol,
    #                                        #function_def_parameter = func_call_param._function_def_parameter
    #                                        #)

    #    new_f = ast.FunctionDefInstantiation(
    #                parameters=parameters_new,
    #                function_def = o.function_def
    #            )
    #    return new_f







class FunctionCloner(ASTVisitorBase):

    def __init__(self, functiondef_instantiation):

        print '\n\n'
        self.functiondef_instantiation = functiondef_instantiation
        print 'Cloning function-def rhs:', repr(self.functiondef_instantiation)

        print 'Copying parameters:'
        self.params_old_to_new = {}
        for sym, param_obj in functiondef_instantiation.parameters.items():
            self.params_old_to_new[param_obj.get_function_def_parameter()] = param_obj.rhs_ast


        self.new_node = self.visit(self.functiondef_instantiation.function_def.rhs)


    def VisitFunctionDefInstantiation(self, o):

        if o.function_def.is_builtin():

            params_new = {}
            # Clone the parameter objects:
            for param_name, func_call_param in o.parameters.items():
                pnew = ast.FunctionDefParameterInstantiation(
                                            rhs_ast=self.visit(func_call_param.rhs_ast),
                                            symbol=func_call_param.symbol,
                                            function_def_parameter = func_call_param._function_def_parameter
                                            )
                params_new[param_name] = pnew

            return ast.FunctionDefInstantiation( 
                        function_def = o.function_def,
                        parameters = params_new )

        print 'Function call:', repr(o)
        assert False, 'We shoudl not get here! we are doing depth first search'

    def VisitFunctionDefParameter(self, o ):
        print 'Searching:', o, 'in', self.params_old_to_new
        assert o in self.params_old_to_new
        return self.params_old_to_new[o]
        assert False

    def VisitAddOp(self, o):
        return ast.AddOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitSubOp(self, o):
        return ast.SubOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitMulOp(self, o):
        return ast.MulOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitDivOp(self, o):
        return ast.DivOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )





class FunctionExpander(ASTActionerDefaultIgnoreMissing):

    def __init__(self, component):
        self.component = component
        super(FunctionExpander,self).__init__()

    

    def ActionNode(self, n, **kwargs):
        #print 'Skipping', n
        pass

    def ActionFunctionDefInstantiation(self,n):
        print 'ACTIONING!' , n
        if n.function_def.is_builtin():
            print 'Skipping Builtin!'
            return


        print 'Expanding out:', n.function_def.funcname
        new_node = FunctionCloner(n).new_node
        
        # Replace the node:
        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        ReplaceNode.replace_and_check(n, new_node, root=self.component)

        # Make sure all the units are still OK:
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self.component)

        print '\n\n'

        pass



FunctionExpander(comp).visit(comp)



















### Check it works:
#res = comp.simulate(
#                times = np.arange(0, 0.1,0.00001),
#                initial_state_values={
#                    'V':'-60mV',
#                    'na_m':'1.0',
#                    'ca_m':'1.0',
#                    'na_h':'1.0',
#                    'ks_n':'1.0',
#                    'kf_n':'1.0',
#                    'V':'-60mV',
#                    },
#                parameters={'glk_noise': '1.2'},
#                )
#res.auto_plot()
#pylab.show()




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






class VariableAnnotation(object):
    pass




#CBasedEqnWriter(comp, float_type='float',  output_filename='res_float.txt',  annotations=[] )
#CBasedEqnWriter(comp, float_type='double', output_filename='res_double.txt',  annotations=[] )
#CBasedEqnWriter(comp, float_type='mpf_class', output_filename='res_gmp.txt',  annotations=[] )
#
#
#
#data_float = np.loadtxt('res_gmp.txt')
#data_double = np.loadtxt('res_double.txt')
#data_gmp = np.loadtxt('res_gmp.txt')
#
#pylab.plot(data_float[:,0], data_float[:,1], label='float' )
#pylab.plot(data_double[:,0], data_double[:,1], label='double' )
#pylab.plot(data_gmp[:,0], data_gmp[:,1], label='gmp' )
#pylab.show()

























for term in comp.terminal_symbols:
    print repr(term)


class VarAnnot(object):
    def __init__(self, val_min = None, val_max = None ):
        from neurounits import NeuroUnitParser
        if isinstance(val_min, basestring):
            val_min = NeuroUnitParser.QuantitySimple(val_min)
        if isinstance(val_max, basestring):
            val_max = NeuroUnitParser.QuantitySimple(val_max)

        self.val_min = val_min
        self.val_max = val_max

    def __str__(self):
        return "Bounds( min:{%s} max:{%s} )" % (self.val_min, self.val_max)





var_annots = {
    't'             : VarAnnot(val_min=None, val_max = None),
    'alpha_ca_m'    : VarAnnot(val_min=None, val_max = None),
    'alpha_kf_n'    : VarAnnot(val_min=None, val_max = None),
    'alpha_ks_n'    : VarAnnot(val_min=None, val_max = None),
    'alpha_na_h'    : VarAnnot(val_min=None, val_max = None),
    'alpha_na_m'    : VarAnnot(val_min=None, val_max = None),
    'beta_ca_m'     : VarAnnot(val_min=None, val_max = None),
    'beta_ca_m_1'   : VarAnnot(val_min=None, val_max = None),
    'beta_ca_m_2'   : VarAnnot(val_min=None, val_max = None),
    'beta_kf_n'     : VarAnnot(val_min=None, val_max = None),
    'beta_ks_n'     : VarAnnot(val_min=None, val_max = None),
    'beta_na_h'     : VarAnnot(val_min=None, val_max = None),
    'beta_na_m'     : VarAnnot(val_min=None, val_max = None),
    'exp_neg_nu'    : VarAnnot(val_min=None, val_max = None),
    'iCa2'          : VarAnnot(val_min=None, val_max = None),
    'iInj'          : VarAnnot(val_min=None, val_max = None),
    'iKf'           : VarAnnot(val_min=None, val_max = None),
    'iKs'           : VarAnnot(val_min=None, val_max = None),
    'iLk'           : VarAnnot(val_min=None, val_max = None),
    'iNa'           : VarAnnot(val_min=None, val_max = None),
    'inf_ca_m'      : VarAnnot(val_min=None, val_max = None),
    'inf_kf_n'      : VarAnnot(val_min=None, val_max = None),
    'inf_ks_n'      : VarAnnot(val_min=None, val_max = None),
    'inf_na_h'      : VarAnnot(val_min=None, val_max = None),
    'inf_na_m'      : VarAnnot(val_min=None, val_max = None),
    'nu'            : VarAnnot(val_min=None, val_max = None),
    'tau_ca_m'      : VarAnnot(val_min=None, val_max = None),
    'tau_kf_n'      : VarAnnot(val_min=None, val_max = None),
    'tau_ks_n'      : VarAnnot(val_min=None, val_max = None),
    'tau_na_h'      : VarAnnot(val_min=None, val_max = None),
    'tau_na_m'      : VarAnnot(val_min=None, val_max = None),
    'V'             : VarAnnot(val_min="-100mV", val_max = "50mV"),
    'ca_m'          : VarAnnot(val_min=None, val_max = None),
    'kf_n'          : VarAnnot(val_min=None, val_max = None),
    'ks_n'          : VarAnnot(val_min=None, val_max = None),
    'na_h'          : VarAnnot(val_min=None, val_max = None),
    'na_m'          : VarAnnot(val_min=None, val_max = None),
}










class ASTDataAnnotator(ASTVisitorBase):
    def __init__(self, component, annotations_in):
        self.component = component
        self.annotations = {}

        # Change string to node:
        for ann,val in annotations_in.items():
            if isinstance(ann, basestring):
                self.annotations[component.get_terminal_obj(ann)] = val
            else:
                self.annotations[ann] = val



        self.visit(component)

    def VisitNineMLComponent(self, component):

        for o in component.ordered_assignments_by_dependancies:
            self.visit(o)
        for o in component.timederivatives:
            self.visit(o)



    def VisitEqnAssignmentByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)
        print 'Need to make assignment'

    def VisitTimeDerivativeByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)
        print 'Need to make assignment'


    def VisitRegimeDispatchMap(self, o):
        assert len(o.rhs_map) == 1
        # Don't worry about regime maps:
        return self.visit( o.rhs_map.values()[0])


    def VisitFunctionDefInstantiation(self,o):
        pass

    def VisitFunctionDefInstantiationParater(self, o):
        pass

    def VisitFunctionDefParameter(self, o):
        pass


    def VisitAddOp(self, o):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]
        print ann1, ann2, repr(o.lhs), repr(o.rhs)
        assert False

    def VisitSubOp(self, o):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]
        print ann1, ann2
        assert False

    def VisitMulOp(self, o):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]
        print ann1, ann2
        assert False

    def VisitDivOp(self, o):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]
        print ann1, ann2
        assert False



    def VisitIfThenElse(self, o):
        pass
        #return "( (%s) ? (%s) : (%s) )" % (
        #            self.visit(o.predicate),
        #            self.visit(o.if_true_ast),
        #            self.visit(o.if_false_ast),
        #        )

    def VisitInEquality(self, o):
        pass
        return "(%s < %s)" % ( self.visit(o.less_than), self.visit(o.greater_than) )
    def VisitStateVariable(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitParameter(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)


    def VisitAssignedVariable(self, o):

        pass
        #return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)

    def VisitSuppliedValue(self, o):
        pass
        #return o.symbol

annotations = ASTDataAnnotator( comp, annotations_in = var_annots)











#pylab.figure()
#pylab.plot(data_float[:,0], data_float[:,2], label='na' )
#pylab.plot(data_float[:,0], data_float[:,3], label='na' )
#
#pylab.figure()
#pylab.plot(data_float[:,0], data_float[:,4], label='na' )

#
#data_double = np.loadtxt('res_double.txt')
#pylab.legend()
#
#
#pylab.show()
#

