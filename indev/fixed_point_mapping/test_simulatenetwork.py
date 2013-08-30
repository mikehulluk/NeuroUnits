

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



dINs = pops_by_name['pop2']
 


rhs_subpops = [pop_RHS_MN, pop_RHS_RB, pop_RHS_aIN, pop_RHS_cIN, pop_RHS_dla, pop_RHS_dlc] 
lhs_subpops = [pop_LHS_MN, pop_LHS_RB, pop_LHS_aIN, pop_LHS_cIN, pop_LHS_dla, pop_LHS_dlc]

network.record_traces( rhs_subpops+lhs_subpops + [dINs], 'V' )

network.record_input_events( rhs_subpops+lhs_subpops, 'recv_nmda_spike' )
network.record_output_events( rhs_subpops+lhs_subpops + [dINs], 'spike' )


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
        #print res.raw_data.time_pts.shape, res.raw_data.data_pts
        #print type(res.raw_data.data_pts)
        #print res.group
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts, label=','.join(res.tags), ms='x'  )
        #print np.min(res), np.max(res)
    pylab.ylabel(symbol)
    pylab.legend()


pop_sizes = {'pop1':1146, 'pop2':235}



for pop_name, size in pop_sizes.items():
    pylab.figure(figsize=(20,16))
    
    r = results.h5file.root.simulation_fixed.double
    
    p = getattr(r, pop_name)
    
    for i in range(size):
        node = getattr(p, '%04d'%i)
        spikes = node.output_events.spike.read()
        indices = [i] * len(spikes)
        print spikes
        pylab.plot(spikes, indices,'x')
    
    

    
    






pylab.show()
