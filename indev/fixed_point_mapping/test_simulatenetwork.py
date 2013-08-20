

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG,mreorg.FigFormat.SVG]

import neurounits

import numpy as np
import pylab

from neurounits.tools.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile

from neurounits.ast_annotations.common import NodeRangeAnnotator, NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator, _NodeRangeFloat, RangeExpander





src_text = """
define_component simple_hh {
    from std.math import exp, ln

    iInj_local = [{50pA} * k] if [t > 75ms and t< 85ms or t<1ms] else [0pA]
    Cap = 10 pF

    V' = (1/Cap) * (iInj_local + i_injected + iLk + iKs + iKf +iNa + i_nmda)



    # NMDA noise:

    syn_nmda_A_tau = 4ms
    syn_nmda_B_tau = 80ms
    i_nmda = g_nmda * (syn_nmda_B - syn_nmda_A) * (e_NMDA - V) * nmda_vdep  * 0.5
    syn_nmda_A' = -syn_nmda_A / syn_nmda_A_tau
    syn_nmda_B' = -syn_nmda_B / syn_nmda_B_tau
    # TOOO:
    #nmda_tc_max = (syn_nmda_A_tau * syn_nmda_B_tau) * ln( syn_nmda_B_tau / syn_nmda_A_tau)
    g_nmda = 300pS
    e_NMDA = 0mV

    v_scale = V * {-0.08mV-1}
    nmda_vdep =  1./(1. + 0.05 * exp(v_scale) )


    noise_min = 0.5
    noise_max = 1.5

    glk_noise1 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]
    glk_noise2 =  ~uniform(min=noise_min, max=noise_max + eK/{1V})[when=SIM_INIT, share=PER_POPULATION]
    glk_noise3 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_POPULATION]
    glk_noise4 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]


    glk_noise = (glk_noise1 + glk_noise2 ) / 4.0



    AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))

    eK = -80mV
    eNa = 50mV
    gKs = 10.0 nS
    gKf = 12.5 nS
    gNa = 250 nS
    gLk = 1.25 nS
    eLk = -50mV

    # Leak
    iLk = gLk * (eLk-V) * glk_noise

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
    iKf = gKf * (eK-V) * kf_n2 #kf_n*kf_n * kf_n*kf_n
    kf_n2 = kf_n*kf_n * kf_n * kf_n

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

    iNa = gNa * (eNa-V) * na_m * na_m * na_m * na_h * glk_noise1


    # Calcium:
    #alpha_ca_m = AlphaBetaFunc(v=V, A=4.05ms-1, B=0.0ms-1 mV-1, C=1.0, D=-15.32mV,E=-13.57mV)
    #beta_ca_m_1 =  AlphaBetaFunc(v=V, A=1.24ms-1, B=0.093ms-1 mV-1, C=-1.0, D=10.63mV, E=1.0mV)
    #beta_ca_m_2 =  AlphaBetaFunc(v=V, A=1.28ms-1, B=0.0ms-1 mV-1, C=1.0, D=5.39mV, E=12.11mV)
    #beta_ca_m =  [beta_ca_m_1] if [ V<-25mV] else [beta_ca_m_2]
    #inf_ca_m = alpha_ca_m / (alpha_ca_m + beta_ca_m)
    #tau_ca_m = 1.0 / (alpha_ca_m + beta_ca_m)
    #ca_m' = (inf_ca_m - ca_m) / tau_ca_m

    pca = {0.16 (m m m)/s} * 1e-6
    F = 96485 C / mol
    R = 8.3144 J/ (mol K)
    T = 300K
    Cai = 100 nM
    Cao = 10 mM
    #nu = ( (2.0 *  F) / (R*T) ) * V ;
    #exp_neg_nu = exp( -1. * nu );
    #iCa2 =  -2.0 * 1.e-3 * pca * nu * F * ( Cai - Cao*exp_neg_nu) / (1-exp_neg_nu) *  ca_m * ca_m
    iCa2 = [4pA] if [t < 0ms] else [4pA]
    iCa =  -3pA


    <=> INPUT t:(ms)
    <=> INPUT i_injected:(mA)

    k'=0 s-1



    regime sub{
        on (V > 0V) {
            k=0
            emit spike()
            transition_to super
        };
    }
    regime super{
       on (V < 0V) {
           k=1
        transition_to sub
        };
    }


    on recv_nmda_spike(){

        syn_nmda_A = syn_nmda_A + 1.0
        syn_nmda_B = syn_nmda_B + 1.0
    }






    initial {
        V = -60mV
        k=1
        na_m = 0.0
        #ca_m = 0.0
        na_h = 1.0
        ks_n = 0.0
        kf_n = 0.0

       syn_nmda_B = 0.0
        syn_nmda_A = 0.0
        regime sub
    }


}



"""




var_annots_dIN = {
    't'             : NodeRange(min="0ms", max = "1.1s"),
    'i_injected'    : NodeRange(min="0nA", max = "10nA"),
    'V'             : NodeRange(min="-100mV", max = "50mV"),
    'k'             : NodeRange(min="0", max = "1.1"),
    'ca_m'          : NodeRange(min="0", max = "1.5"),
    'kf_n'          : NodeRange(min="0", max = "1.5"),
    'ks_n'          : NodeRange(min="0", max = "1.5"),
    'na_h'          : NodeRange(min="0", max = "1.5"),
    'na_m'          : NodeRange(min="0", max = "1.5"),
    'syn_nmda_A'    : NodeRange(min='0', max ='30'),
    'syn_nmda_B'    : NodeRange(min='0', max ='30'),
    }




library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
comp = library_manager['simple_hh']
comp.expand_all_function_calls()


nbits = 24


from neurounits.writers import MRedocWriterVisitor
MRedocWriterVisitor().visit(comp).to_pdf('op.pdf')

# Setup the annotations:
comp.annotate_ast( NodeRangeAnnotator(var_annots_dIN) )
RangeExpander().visit(comp)


comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )



#assert False






from neurounits.tools.population_infrastructure import *
network = Network()
p1 = Population(name='LHSdIN', component=comp, size=30 )
p2 = Population(name='RHSdIN', component=comp, size=1 )
network.add(p1)
network.add(p2)

# Electrical synapses:
e1 = ElectricalSynapseProjection(src_population=p1, dst_population=p1, connection_probability=0.2, strength_ohm=300e6, name='ElecLHSdIN', injected_port_name='i_injected')
network.add(e1)

# Chemical Synapses:
s1 = EventPortConnector(p1,p1, src_port_name='spike', dst_port_name='recv_nmda_spike', connection_probability=0.1, name='Conn01' )
network.add(s1)









record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','iInj_local','i_nmda', 'nmda_vdep', 'iLk','iKf']
record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','i_nmda', 'nmda_vdep' , 'iLk','iKf','kf_n' , 'iInj_local']
# Just generate the file:
CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', run=False, output_c_filename='/auto/homes/mh735/Desktop/tadpole1.cpp', compile=False, CPPFLAGS='-DON_NIOS=true', record_symbols=record_symbols )

#assert False


fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false', record_symbols=record_symbols).results



results = HDF5SimulationResultFile("output.hd5")





time_array = results.h5file.root._f_getChild('/simulation_fixed/double/time').read()



for symbol in record_symbols:
    pylab.figure(figsize=(20,16))
    print 'Plotting:', symbol
    for i in range(30):
        res = results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/%03d/variables/%s' % (i, symbol)).read()
        pylab.plot(time_array, res, label='%s:lhs-%03d' % (symbol, i) )
        print np.min(res), np.max(res)
    pylab.legend()




#pylab.figure()
#for i in range(30):
#    pylab.plot(time_array, results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/%03d/variables/V' % i).read(), label='V:lhs-%03d' % i)
#pylab.legend()
#
#pylab.figure()
#for i in range(30):
#    pylab.plot(time_array, results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/%03d/variables/k' % i).read(), label='k:lhs-%03d' % i)
#pylab.legend()
#
#pylab.figure()
#for i in range(30):
#    pylab.plot(time_array, results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/%03d/variables/iInj_local' % i).read(), label='iInj-%03d' % i)
#pylab.legend()
#
#pylab.figure()
#for i in range(30):
#    pylab.plot(time_array, results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/%03d/variables/i_nmda' % i).read(), label='i_nmda-%03d' % i)
#pylab.legend()



pylab.show()







V_LHS000 = results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/000/variables/V').read()
V_LHS001 = results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/001/variables/V').read()
V_LHS002 = results.h5file.root._f_getChild('/simulation_fixed/double/LHSdIN/002/variables/V').read()



V_RHS = results.h5file.root._f_getChild('/simulation_fixed/double/RHSdIN/000/variables/V').read()

print 'time: ', time_array.shape
print 'V_LHS: ', V_LHS000.shape
print 'V_RHS: ', V_RHS.shape

pylab.plot(time_array, V_LHS000, label='lhs-000')
pylab.plot(time_array, V_LHS001, label='lhs-001')
pylab.plot(time_array, V_LHS002, label='lhs-002')

pylab.plot(time_array, V_RHS, label='rhs')
pylab.legend()
pylab.show()






#
#
#
# float_group = results.h5file.root._f_getChild('/simulation_fixed/double/variables/')
# time_array = results.h5file.root._f_getChild('/simulation_fixed/double/time')
#
# def plot_set( ys, plot_index, plot_total, figure):
#
#     ax = figure.add_subplot(plot_total, 1, plot_index, )
#     for y in ys:
#         try:
#             #ax.plot(data_int[x], data_int[y], label=y )
#             ax.plot(time_array.read(), float_group._f_getChild(y).read(), label=y )
#         except KeyError, e:
#             print e
#         except ValueError, e:
#             print e
#         except tables.exceptions.NoSuchNodeError,e:
#             print e
#
#     ax.legend()
#
#
#
#
#
# fig = pylab.figure()
#
#
#
# plot_set( ['alpha_kf_n', 'beta_kf_n'], 1, 5, fig)
# plot_set( ['kf_n', 'inf_kf_n'],  2, 5, fig)
# plot_set( ['iInj','iLk','iKf'], 3, 5, fig)
# plot_set( ['tau_kf_n'],  4, 5, fig)
# plot_set( ['V','V2'],  5, 5, fig )
#
#
#
#
#
#
#
#
#
# data_names1 = [ass.symbol for ass in comp.assignedvalues]
# data_names2 = [sv.symbol for sv in comp.state_variables]
# data_names = data_names1 + data_names2
#
#
# data_names = ['V']
#
#
# for data_name in data_names:
#     did_plot = False
#     try:
#         pylab.figure()
#         if res:
#             pylab.plot(res.get_time(), res.get_data(data_name),'r-',  alpha=0.4, lw=10 )
#             pylab.plot(res.get_time(), res.get_data(data_name),'r-x', label='ref-%s'%data_name, )
#         #pylab.plot(data_int['i']/10000., data_int[data_name], 'bx',label='fixed-%s'%data_name )
#         pylab.plot(time_array.read()+0.1e-3, float_group._f_getChild(data_name).read(), label='fixed-%s'%data_name )
#
#         pylab.legend()
#         did_plot=True
#     except KeyError, e:
#         print e
#     except ValueError, e:
#         print e
#     except AssertionError, e:
#         print e
#     if not did_plot:
#         pylab.close()
#
# pylab.show()
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

