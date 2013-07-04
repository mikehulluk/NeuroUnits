



import neurounits

import numpy as np
import pylab
from neurounits.units_backends.mh import MMQuantity, MMUnit
from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst



from fixed_point_annotations import VarAnnot, ASTDataAnnotator, CalculateInternalStoragePerNode












src_text = """
define_component simple_hh {
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

    initial {
        V = -60mV
        na_m = 1.0
        ca_m = 1.0
        na_h = 1.0
        ks_n = 1.0
        kf_n = 1.0
    }

}


define_component simple_test {

    <=> INPUT t:(ms)


    iInj = ([50pA] if [t > 100ms] else [0pA])
    Cap = 10 pF
    gLk = 1.25 nS
    eLk = -50mV

    iLk = gLk * (eLk-V) + ({0 pA/ms} * t)

    
    
    
    V' = (1/Cap) * (iInj + iLk )

    eK = -80mV
    gKf = 12.5 nS

    AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + std.math.exp( (D+v)/E))
    alpha_kf_n = AlphaBetaFunc(v=V, A=5.06ms-1, B=0.0666ms-1 mV-1, C=5.12, D=-18.396mV,E=-25.42mV)
    beta_kf_n =  AlphaBetaFunc(v=V, A=0.505ms-1, B=0.0ms-1 mV-1, C=0.0, D=28.7mV, E=34.6mV)
    inf_kf_n = alpha_kf_n / (alpha_kf_n + beta_kf_n)
    tau_kf_n = 1.0 / (alpha_kf_n + beta_kf_n)
    kf_n' = (inf_kf_n - kf_n) / tau_kf_n
    iKf = gKf * (eK-V) * kf_n*kf_n * kf_n*kf_n
    


    
    


    initial {
        V = -60mV
        #V2 = -60mV
        kf_n = 1.0
    }


    }
    
    
define_component simple_exp {  
    <=> INPUT t:(ms)  
    a = [0] if [t<100ms] else [1.5]
    A' = (a-A)/{20ms}

    initial {
        A = 0.0
    }


}




"""



var_annots_dIN = {
    't'             : VarAnnot(val_min="0ms", val_max = "1.1s"),
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

var_annots_test = {
    't'    : VarAnnot(val_min="0ms", val_max = "1s"),
    #'a'    : VarAnnot(val_min=None, val_max = None),
    #'b'    : VarAnnot(val_min=None, val_max = None),

    'iInj' : VarAnnot(val_min=None, val_max = None),
    'iLk'  : VarAnnot(val_min=None, val_max = None),
    'V'    : VarAnnot(val_min="-100mV", val_max = "60mV"),
    #'V2'    : VarAnnot(val_min="-100mV", val_max = "60mV"),

    'alpha_kf_n'   : VarAnnot(val_min=None, val_max = None),
    'beta_kf_n'    : VarAnnot(val_min=None, val_max = None),
    'inf_kf_n'     : VarAnnot(val_min="0.0", val_max = "1.0"),
    'tau_kf_n'     : VarAnnot(val_min="0.0ms", val_max = "10ms"),
    'iKf'          : VarAnnot(val_min=None, val_max = None),
    'iKf2'          : VarAnnot(val_min=None, val_max = None),
    'kf_n'          : VarAnnot(val_min="0", val_max = "1"),
}




var_annots_exp = {
    't'    : VarAnnot(val_min="0ms", val_max = "1s"),
    'A'          : VarAnnot(val_min="0", val_max = "1.75"),
    'a'          : VarAnnot(val_min="0", val_max = "1.75"),
}








#component_name = 'simple_hh'
component_name = 'simple_test'
#component_name = 'simple_test'
#component_name = 'simple_exp'


library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
comp = library_manager[component_name]
comp.expand_all_function_calls()



var_annots = {
              'simple_hh': var_annots_dIN,
              'simple_test': var_annots_test,
              'simple_exp': var_annots_exp,
             }[component_name]








## Check it works:
#simulate = False
simulate = True
res = None
if simulate:
    res = comp.simulate( times = np.arange(0, 0.2,0.0001) )
    res.auto_plot()
    #pylab.show()


















#import os
#from neurounits.visitors.bases.base_visitor import ASTVisitorBase











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



























print
print
print 'Looking at mappings:'
print '===================='


nbits = 24
annotations = ASTDataAnnotator( comp, annotations_in = var_annots)
CalculateInternalStoragePerNode(annotations=annotations, nbits=nbits).visit(comp)







import os
import time


print
print
print 'Writing out to C-file'
print '===================='


from neurounits.tools.fixed_point import CBasedEqnWriterFixed
CBasedEqnWriterFixed(comp, output_filename='res_int.txt',  annotations=annotations, nbits=nbits )

#data_int = np.loadtxt('res_int.txt')
with open('res_int.txt') as f:
    d = f.read()
os.unlink('res_int.txt')
with open('res_int.txt', 'w') as f:
    f.write( d.replace(",\n","\n") )


import numpy as np
data_int = np.genfromtxt('res_int.txt', names=True, delimiter=',', dtype=float)


print data_int
print type(data_int)
print data_int.shape




def plot_set(data, x, ys, plot_index, plot_total, figure):

    ax = figure.add_subplot(plot_total, 1, plot_index, )
    for y in ys:
        try:
            ax.plot(data_int[x], data_int[y], label=y )
        except KeyError, e:
            print e
        except ValueError, e:
            print e

    ax.legend()






# 
# t = np.linspace(0,0.3,num=3000)
# correct = 1.5 * (1.-np.exp(-t/20e-3) )
# 
# pylab.plot(data_int['i']/10000., data_int['a'], 'x',label='fixed-a' )
# pylab.plot(data_int['i']/10000., data_int['A'], 'x',label='fixed-A' )
# 
# pylab.plot(t+0.1,correct,'r-')
# pylab.legend()
# pylab.show()
# assert False













fig = pylab.figure()



plot_set(data_int, 'i', ['alpha_kf_n', 'beta_kf_n'], 1, 5, fig)

plot_set(data_int, 'i', ['kf_n', 'inf_kf_n'],  2, 5, fig)
plot_set(data_int, 'i', ['iInj','iLk','iKf'], 3, 5, fig)

plot_set(data_int, 'i', ['tau_kf_n'],  4, 5, fig)
plot_set(data_int, 'i', ['V','V2'],  5, 5, fig )










for data_name in [ 'V' ,'V2', 'alpha_kf_n', 'beta_kf_n', 'A','a', 'iInj','iLk','iKf','kf_n', 'inf_kf_n', 'tau_kf_n'  ]:
    did_plot = False
    try:
        pylab.figure()
        if res:
            pylab.plot(res.get_time(), res.get_data(data_name),'-', label='ref-%s'%data_name )
        pylab.plot(data_int['i']/10000., data_int[data_name], 'x',label='fixed-%s'%data_name )
        pylab.legend()
        did_plot=True
    except KeyError, e:
        print e
    except ValueError, e:
        print e
    except AssertionError, e:
        print e
    if not did_plot:
        pylab.close()

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

