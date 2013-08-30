

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG,mreorg.FigFormat.SVG]

import os
import neurounits

import numpy as np
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *


import dIN_model
import cPickle as pickle




use_cache=True
cache_file = '.din_model_cache'
# Delete the cache-fiel if we are not using it:
if not use_cache:
    if os.path.exists(cache_file):
        os.unlink(cache_file)
    
if not os.path.exists(cache_file):
    dIN_comp = dIN_model.get_dIN(nbits=24)
    with open(cache_file,'w') as f:
        pickle.dump(dIN_comp, f, )
    del dIN_comp

with open(cache_file) as f:
    dIN_comp = pickle.load(f) 




# For ddebugging:
#MRedocWriterVisitor().visit(dIN_comp).to_pdf("op.pdf")









network = Network()
pop_components = {
        'pop1': dIN_comp,
        'pop2': dIN_comp,
        }


with open('mh_reduced_connectome.pickle') as f:
    pop_sizes, connections, pop_breakdowns = pickle.load(f)



network = Network()
pops_by_name = {}
for pop_name, pop_size in pop_sizes.items():
    p = Population(name=pop_name, component=pop_components[pop_name], size=pop_size)
    network.add(p)
    assert not pop_name in pops_by_name
    pops_by_name[pop_name] = p


for syn_index, ((pop1_name, pop2_name, (syn_type, strength) ), conns) in enumerate(connections.items()):
    print 'Adding connection: %s -> %s [type:%s strength:%s, num:%d]' % (pop1_name, pop2_name, syn_type, strength, len(conns))

    p1 = pops_by_name[pop1_name]
    p2 = pops_by_name[pop2_name]
    synpop_name='SynPop%02d' % syn_index
    network.add(
        EventPortConnector(p1,p2, src_port_name='spike', dst_port_name='recv_%s_spike' %syn_type, name=synpop_name , connector=ExplicitIndices(conns) )
        )





network.provide_events( pops_by_name['pop1'], event_port='recv_ampa_spike', evt_details = [50,60,70] )

pop_LHS_MN  = pops_by_name['pop1'].get_subpopulation(start_index=0,   end_index=169, subname='LHS_MN',  autotag=['LHS','MN'])
pop_LHS_RB  = pops_by_name['pop1'].get_subpopulation(start_index=169, end_index=232, subname='LHS_RB',  autotag=['LHS','RB'])
pop_LHS_aIN = pops_by_name['pop1'].get_subpopulation(start_index=232, end_index=300, subname='LHS_aIN', autotag=['LHS','aIN'])
pop_LHS_cIN = pops_by_name['pop1'].get_subpopulation(start_index=300, end_index=492, subname='LHS_cIN', autotag=['LHS','cIN'])
pop_LHS_dla = pops_by_name['pop1'].get_subpopulation(start_index=492, end_index=521, subname='LHS_dla', autotag=['LHS','dla'])
pop_LHS_dlc = pops_by_name['pop1'].get_subpopulation(start_index=521, end_index=573, subname='LHS_dlc', autotag=['LHS','dlc'])


pop_RHS_MN  = pops_by_name['pop1'].get_subpopulation(start_index=573,  end_index=742,  subname='RHS_MN',  autotag=['RHS','MN'])
pop_RHS_RB  = pops_by_name['pop1'].get_subpopulation(start_index=742,  end_index=805,  subname='RHS_RB',  autotag=['RHS','RB'])
pop_RHS_aIN = pops_by_name['pop1'].get_subpopulation(start_index=805,  end_index=873,  subname='RHS_aIN', autotag=['RHS','aIN'])
pop_RHS_cIN = pops_by_name['pop1'].get_subpopulation(start_index=873,  end_index=1065, subname='RHS_cIN', autotag=['RHS','cIN'])
pop_RHS_dla = pops_by_name['pop1'].get_subpopulation(start_index=1065, end_index=1094, subname='RHS_dla', autotag=['RHS','dla'])
pop_RHS_dlc = pops_by_name['pop1'].get_subpopulation(start_index=1094, end_index=1146, subname='RHS_dlc', autotag=['RHS','dlc'])


 


rhs_subpops = [pop_RHS_MN, pop_RHS_RB, pop_RHS_aIN, pop_RHS_cIN, pop_RHS_dla, pop_RHS_dlc] 
lhs_subpops = [pop_LHS_MN, pop_LHS_RB, pop_LHS_aIN, pop_LHS_cIN, pop_LHS_dla, pop_LHS_dlc]

network.record_traces( rhs_subpops+lhs_subpops, 'V' )

network.record_input_events( rhs_subpops+lhs_subpops, 'recv_nmda_spike' )
network.record_output_events( rhs_subpops+lhs_subpops, 'spike' )


network.finalise()



record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','iInj_local','i_nmda', 'nmda_vdep', 'iLk','iKf']
record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','i_nmda', 'nmda_vdep' , 'iLk','iKf','kf_n' , 'iInj_local']
record_symbols = ['nu', 'exp_neg_nu',   'V','iCa', 'ca_m','ca_m_inf','tau_ca_m', 'tau_ca_m_cl','alpha_ca_m','beta_ca_m','iNa','iKf','iKs', 'beta_ca_m_2', 'beta_ca_m_1',]
record_symbols = ['V']
record_symbols = ['V']
# Just generate the file:
CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', run=False, output_c_filename='/auto/homes/mh735/Desktop/tadpole1.cpp', compile=False, CPPFLAGS='-DON_NIOS=true', record_symbols=record_symbols )



fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false', record_symbols=record_symbols).results
results = HDF5SimulationResultFile("output.hd5")

for symbol in record_symbols:
    pylab.figure(figsize=(20,16))
    print 'Plotting:', symbol

    for res in results.filter(" ALL{%s} AND ANY{POPINDEX:000, POPINDEX:001,POPINDEX:002,POPINDEX:003, POPINDEX:118, POPINDEX:119,POPINDEX:120,POPINDEX:168,POPINDEX:169,POPINDEX:170}" % symbol):
    #for res in results.filter("ALL{%s,POPINDEX:001}" % symbol):
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts, label=','.join(res.tags), ms='x'  )
        #print np.min(res), np.max(res)
    pylab.ylabel(symbol)
    pylab.legend()

pylab.figure(figsize=(20,16))
pylab.ylabel('Currents (pA)')
for symbol in record_symbols:
    if symbol[0] != 'i':
        continue
    #if symbol=='iCa':
    #    continue

    for res in results.filter(symbol):
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts * 1e12, label=symbol  )

pylab.show()

#f = pylab.figure(figsize=(20,16))
#ax1 = f.add_subplot(211)
#ax2 = f.add_subplot(212)
#voltage = results.filter('V')[0].raw_data
#beta_ca = results.filter('beta_ca_m')[0].raw_data
#beta_ca_1 = results.filter('beta_ca_m_1')[0].raw_data
#beta_ca_2 = results.filter('beta_ca_m_2')[0].raw_data
#
#
#R = (voltage.data_pts + 25e-3) > 0
#switches = np.logical_xor(R, np.roll(R,1) )
##switch_points = (np.diff( (voltage.data_pts - (-25e-3)) > 0 ) ** 2 ) > 0.5
#switch_points = np.where( switches)[0]
#print switch_points
#
#ax1.plot(voltage.time_pts, voltage.data_pts, label='Voltage')
#ax2.plot(beta_ca.time_pts, beta_ca.data_pts, label='Beta')
#ax2.plot(beta_ca_1.time_pts, beta_ca_1.data_pts, label='Beta1')
#ax2.plot(beta_ca_2.time_pts, beta_ca_2.data_pts, label='Beta2')
#
#ax1.set_xlim((0.07, 0.1))
#ax2.set_xlim((0.07, 0.1))
#
#for ax in [ax1,ax2]:
#    for sw in switch_points:
#        ax.axvline( voltage.time_pts[sw], ls='--',color='k')
#pylab.legend()
#
#
#
#
#pylab.figure()
#pylab.plot( 
#        beta_ca.data_pts[switch_points[0]+1:switch_points[1]-1 ],
#        beta_ca_2.data_pts[switch_points[0]+1:switch_points[1]-1 ] )
#
#
#dy = beta_ca.data_pts[ switch_points[1] -1 ] - beta_ca.data_pts[ switch_points[0] +1 ] 
#dx = beta_ca_2.data_pts[ switch_points[1] -1 ] - beta_ca_2.data_pts[ switch_points[0] +1 ] 
#
#print 'dy:', dy
#print 'dx:', dx
#
#print dy/dx
#
#
#
#
#pylab.legend()



pylab.show()
