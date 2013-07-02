



import neurounits

import numpy as np
import pylab
from neurounits.units_backends.mh import MMQuantity, MMUnit
from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst




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
comp.expand_all_function_calls()





## Check it works:
simulate = False
if simulate:
    res = comp.simulate(
                    times = np.arange(0, 0.1,0.00001),
                    initial_state_values={
                        'V':'-60mV',
                        'na_m':'1.0',
                        'ca_m':'1.0',
                        'na_h':'1.0',
                        'ks_n':'1.0',
                        'kf_n':'1.0',
                        'V':'-60mV',
                        },
                    parameters={'glk_noise': '1.2'},
                    )
    res.auto_plot()
    pylab.show()


















import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase 











test_c = False
if test_c:
    from neurounits.tools.fixed_point import CBasedEqnWriter
    CBasedEqnWriter(comp, float_type='float',  output_filename='res_float.txt',  annotations=[] )
    CBasedEqnWriter(comp, float_type='double', output_filename='res_double.txt',  annotations=[] )
    CBasedEqnWriter(comp, float_type='mpf_class', output_filename='res_gmp.txt',  annotations=[] )
    
    
    
    data_float = np.loadtxt('res_gmp.txt')
    data_double = np.loadtxt('res_double.txt')
    data_gmp = np.loadtxt('res_gmp.txt')
    
    pylab.plot(data_float[:,0], data_float[:,1], label='float' )
    pylab.plot(data_double[:,0], data_double[:,1], label='double' )
    pylab.plot(data_gmp[:,0], data_gmp[:,1], label='gmp' )
    pylab.show()

























#for term in comp.terminal_symbols:
#    print repr(term)


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
    't'             : VarAnnot(val_min="0ms", val_max = "1s"),
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
    'inf_ca_m'      : VarAnnot(val_min="0", val_max = "1" ),
    'inf_kf_n'      : VarAnnot(val_min="0", val_max = "1" ),
    'inf_ks_n'      : VarAnnot(val_min="0", val_max = "1" ),
    'inf_na_h'      : VarAnnot(val_min="0", val_max = "1" ),
    'inf_na_m'      : VarAnnot(val_min="0", val_max = "1" ),
    'nu'            : VarAnnot(val_min="0", val_max = "1" ),
    'tau_ca_m'      : VarAnnot(val_min="0.0ms", val_max = None),
    'tau_kf_n'      : VarAnnot(val_min="0.0ms", val_max = None),
    'tau_ks_n'      : VarAnnot(val_min="0.0ms", val_max = None),
    'tau_na_h'      : VarAnnot(val_min="0.0ms", val_max = None),
    'tau_na_m'      : VarAnnot(val_min="0.0ms", val_max = None),
    'V'             : VarAnnot(val_min="-100mV", val_max = "50mV"),
    'ca_m'          : VarAnnot(val_min="0", val_max = "1"),
    'kf_n'          : VarAnnot(val_min="0", val_max = "1"),
    'ks_n'          : VarAnnot(val_min="0", val_max = "1"),
    'na_h'          : VarAnnot(val_min="0", val_max = "1"),
    'na_m'          : VarAnnot(val_min="0", val_max = "1"),
}





import operator
def do_op(a,b,op):
    if a is None or b is None:
        return None
    try:
        return op(a,b)
    except ZeroDivisionError:
        return None



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
        
        for i in range(2):
            for o in component.symbolicconstants:
                self.visit(o)
            for o in component.ordered_assignments_by_dependancies:
                self.visit(o)
            for o in component.timederivatives:
                self.visit(o)




    def VisitEqnAssignmentByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)
        
        
        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs_map]
        
        #Min:
        if ann_lhs.val_min is None and  ann_rhs.val_min is not None:
            ann_lhs.val_min = ann_rhs.val_min
            
        if ann_lhs.val_max is None and  ann_rhs.val_max is not None:
            ann_lhs.val_max = ann_rhs.val_max
        
        
        

    def VisitTimeDerivativeByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)
        
        
        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs_map]
        
        #Min:
        if ann_lhs.val_min is None and  ann_rhs.val_min is not None:
            ann_lhs.val_min = ann_rhs.val_min
            
        if ann_lhs.val_max is None and  ann_rhs.val_max is not None:
            ann_lhs.val_max = ann_rhs.val_max
        
        


    def VisitRegimeDispatchMap(self, o):
        assert len(o.rhs_map) == 1
        # Don't worry about regime maps:
        for v in o.rhs_map.values():
            self.visit( v )
            
        var_annots = [ self.annotations[v] for v in  o.rhs_map.values() ]
        mins =   sorted( [ann.val_min for ann in var_annots if ann.val_min is not None] )
        maxes =  sorted( [ann.val_max for ann in var_annots if ann.val_max is not None] )
        
        if not mins:
            mins = [None]
        if not maxes:
            maxes = [None]
        
        self.annotations[o] = VarAnnot( mins[0], maxes[-1] )
        #self.annotations[o] = self.visit( o.rhs_map.values()[0])
        


    def VisitFunctionDefInstantiation(self,o):
        print 
        for p in o.parameters.values():
            self.visit(p)
        # We should only have builtin functions by this point
        assert o.function_def.is_builtin()
        
        # Handle exponents:
        assert o.function_def.funcname is '__exp__'
        param_node_ann = self.annotations[ o.parameters.values()[0].rhs_ast ]
        print param_node_ann
        
        min=None
        max=None
        if param_node_ann.val_min is not None:
            v = param_node_ann.val_min.dimensionless()
            min = MMQuantity( np.exp(v),  MMUnit() )
        if param_node_ann.val_max is not None:
            v = param_node_ann.val_max.dimensionless()
            max = MMQuantity( np.exp(v),  MMUnit() )
        
        self.annotations[o] = VarAnnot(val_min=min, val_max=max)
        #assert False
        
        

    def VisitFunctionDefInstantiationParater(self, o):
        self.visit(o.rhs_ast)
        ann = self.annotations[o.rhs_ast]
        self.annotations[o] =  VarAnnot(val_min=ann.val_min, val_max=ann.val_max)

    
    
    
    
    
    def _VisitBinOp(self, o, op):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]
                
        extremes = [
            do_op(ann1.val_min, ann2.val_min, op ),
            do_op(ann1.val_min, ann2.val_max, op ),
            do_op(ann1.val_max, ann2.val_min, op ),
            do_op(ann1.val_max, ann2.val_max, op ),                
            ]
        extremes = sorted([e for e in extremes if e is not None])
        
        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]
        
        self.annotations[o] = VarAnnot(val_min=min, val_max=max)

    

    def VisitAddOp(self, o):
        self._VisitBinOp(o, op=operator.add)

    def VisitSubOp(self, o):
        self._VisitBinOp(o, op=operator.sub)

    def VisitMulOp(self, o):
        self._VisitBinOp(o, op=operator.mul)
     
    def VisitDivOp(self, o):
        self._VisitBinOp(o, op=operator.div)
       
       
       
       
    def VisitIfThenElse(self, o):
        self.visit(o.if_true_ast)
        self.visit(o.if_false_ast)
        ann1 = self.annotations[o.if_true_ast]
        ann2 = self.annotations[o.if_false_ast]
                
        extremes = [
            ann1.val_min,
            ann1.val_max,
            ann2.val_min,
            ann2.val_max,
                ]
        extremes = sorted([e for e in extremes if e is not None])
        
        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]
        
        self.annotations[o] = VarAnnot(val_min=min, val_max=max)
        
        
       

    def VisitInEquality(self, o):
        pass

    def VisitParameter(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)


    # Handled in the __init__ function:
    def VisitStateVariable(self, o):
        pass

    def VisitAssignedVariable(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)

    def VisitSuppliedValue(self, o):
        pass
        #return o.symbol

annotations = ASTDataAnnotator( comp, annotations_in = var_annots)



print
print 'Results:'
print '--------'

for term in comp.terminal_symbols:
    ann = annotations.annotations[term]
    print repr(term), annotations.annotations[term]
    print ann.val_min is not None and ann.val_max is not None 


print
print 'Results:'
print '--------'

for k,v in annotations.annotations.items():
    print repr(k), '\t\t->', v
    


 
for term in comp.terminal_symbols:
    ann = annotations.annotations[term]




from itertools import chain







Nbits = 16
Nrange = 2**Nbits

class CalculateInternalStoragePerNode(ASTActionerDepthFirst):
    
    
    def encode_value(self, value, upscaling_pow):
        print
        print 'Encoding', value, "using upscaling power:", upscaling_pow 
        value_scaled = value * ( 2**(-upscaling_pow) ) 
        print ' --Value Scaled:', value_scaled 
        res = int( value_scaled * (2**Nbits) )
        print ' --Value int:', res
        return res 
        
        
    
    
    def ActionNodeStd(self, o):
        print
        print repr(o)
        print '-' * len(repr(o))
        ann = annotations.annotations[o]
        print ann
        
        # Lets go symmetrical, about 0:
        vmin = ann.val_min.float_in_si()
        vmax = ann.val_max.float_in_si()
        ext = max( [np.abs(vmin),np.abs(vmax) ] )
        if ext != 0.0:
            upscaling_pow = int( np.ceil( np.log2(ext) ) )
        else:
            upscaling_pow = 0 
        
        # Lets remap the limits:
        upscaling_val = 2 ** (-upscaling_pow)
        vmin_scaled  = vmin * upscaling_val
        vmax_scaled  = vmax * upscaling_val
        
        print 'vMin, vMax', vmin, vmax
        print 'Scaling:', '2**', upscaling_pow, ' ->', upscaling_val
        print 'vMin_scaled, vMax_scaled', vmin_scaled, vmax_scaled
        
        
        ann.fixed_scaling_power = upscaling_pow 
        
        
        
    
    

    

    def ActionAddOp(self, o):
        self.ActionNodeStd(o)
    def ActionSubOp(self, o):
        self.ActionNodeStd(o)
    def ActionMulOp(self, o):
        self.ActionNodeStd(o)
    def ActionDivOp(self, o):
        self.ActionNodeStd(o)

    def ActionFunctionDefInstantiation(self, o):
        pass

    def ActionFunctionDefInstantiationParater(self,o):
        self.ActionNodeStd(o)
    
    
    def ActionInEquality(self, o):
        pass
        
    def ActionIfThenElse(self, o ):
        self.ActionNodeStd(o)
        
        
    
    def ActionFunctionDefParameter(self, o):
        pass
        
    def ActionBuiltInFunction(self, o):
        pass
        
    def ActionAssignedVariable(self, o):
        self.ActionNodeStd(o)
    def ActionStateVariable(self, o, **kwargs):
        self.ActionNodeStd(o)
        
    def ActionSuppliedValue(self, o):
        self.ActionNodeStd(o)
        
    def ActionConstant(self, o):
        print
        print 'Converting: ', o, o.value
        
        v = o.value.float_in_si()        
        
        if o.value.magnitude == 0.0:
            upscaling_pow = 0
            ann.fixed_scaling_power = upscaling_pow 
            ann.value_as_int = self.encode_value(v, upscaling_pow) 
            
        else:
            upscaling_pow = int( np.ceil( np.log2(np.fabs(v)) ) )
            ann.fixed_scaling_power = upscaling_pow 
            ann.value_as_int = self.encode_value(v, upscaling_pow) 
        
    def ActionSymbolicConstant(self, o):
        self.ActionConstant(o)
    
    def ActionRegimeDispatchMap(self, o):
        self.ActionNodeStd(o)
    
    def ActionEqnAssignmentByRegime(self, o):
        pass
    def ActionTimeDerivativeByRegime(self, o):
        pass
    

       
        
    def ActionRegime(self,o):
        pass
    def ActionRTGraph(self, o):
        pass
    def ActionNineMLComponent(self, o):
        pass



print
print
print 'Looking at mappings:'
print '===================='

CalculateInternalStoragePerNode().visit(comp)



    




print
print
print 'Writing out to C-file'
print '===================='


from neurounits.tools.fixed_point import CBasedEqnWriterFixed
CBasedEqnWriterFixed(comp, output_filename='res_int.txt',  annotations=[] )

data_int = np.loadtxt('res_int.txt')
pylab.plot(data_int[:,0], data_int[:,1], label='int' )
pylab.show()























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

