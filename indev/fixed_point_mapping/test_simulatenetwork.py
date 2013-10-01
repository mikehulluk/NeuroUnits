

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG] #,mreorg.FigFormat.SVG]

import os
import neurounits

import numpy as np
import random
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *


import dIN_model
import mn_model
import rb_input_model
import cPickle as pickle

from mreorg import PM
import hashlib


src_string = open('dIN_model.py').read() + open('mn_model.py').read()
md5_str = hashlib.md5(src_string).hexdigest()


use_cache=True
#use_cache=False
cache_file = 'caches/.din_model_cache_%s'%(md5_str)
if not os.path.exists('caches/'):
    os.makedirs('caches')
# Delete the cache-file if we are not using it:
if not use_cache:
    if os.path.exists(cache_file):
        os.unlink(cache_file)

if not os.path.exists(cache_file):
    MN_comp = mn_model.get_MN(nbits=24)
    RB_input = rb_input_model.get_rb_input(nbits=24)
    dIN_comp = dIN_model.get_dIN(nbits=24)
    with open(cache_file,'w') as f:
        pickle.dump([dIN_comp, MN_comp, RB_input], f, )

    # For ddebugging:
    MRedocWriterVisitor().visit(dIN_comp).to_pdf("op_dIN.pdf")
    MRedocWriterVisitor().visit(MN_comp).to_pdf("op_MN.pdf")

    del dIN_comp
    del MN_comp
    del RB_input

with open(cache_file) as f:
    dIN_comp,MN_comp,RB_input = pickle.load(f)














network = Network()
pop_components = {
        'NondINs': MN_comp,
        'dINs': dIN_comp,
        }


with open('mh_reduced_connectome.pickle') as f:
    pop_sizes, connections, pop_breakdowns, cell_positions = pickle.load(f)



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
    weight = '%f nS'%strength
    network.add(
            EventPortConnector(p1,p2, src_port_name='spike', dst_port_name='recv_%s_spike' %syn_type, name=synpop_name, delay='1ms', connector=ExplicitIndicesSet(conns), parameter_map= {'weight': FixedValue(weight)} )
        )
#assert False










#network.provide_events( pops_by_name['pop1'], event_port='recv_ampa_spike', evt_details = [50,60,70] )

pop_LHS_MN  = pops_by_name['NondINs'].get_subpopulation(start_index=0,   end_index=169, subname='LHS_MN',  autotag=['LHS','MN'])
pop_LHS_RB  = pops_by_name['NondINs'].get_subpopulation(start_index=169, end_index=232, subname='LHS_RB',  autotag=['LHS','RB'])
pop_LHS_aIN = pops_by_name['NondINs'].get_subpopulation(start_index=232, end_index=300, subname='LHS_aIN', autotag=['LHS','aIN'])
pop_LHS_cIN = pops_by_name['NondINs'].get_subpopulation(start_index=300, end_index=492, subname='LHS_cIN', autotag=['LHS','cIN'])
pop_LHS_dla = pops_by_name['NondINs'].get_subpopulation(start_index=492, end_index=521, subname='LHS_dla', autotag=['LHS','dla'])
pop_LHS_dlc = pops_by_name['NondINs'].get_subpopulation(start_index=521, end_index=573, subname='LHS_dlc', autotag=['LHS','dlc'])


pop_RHS_MN  = pops_by_name['NondINs'].get_subpopulation(start_index=573,  end_index=742,  subname='RHS_MN',  autotag=['RHS','MN'])
pop_RHS_RB  = pops_by_name['NondINs'].get_subpopulation(start_index=742,  end_index=805,  subname='RHS_RB',  autotag=['RHS','RB'])
pop_RHS_aIN = pops_by_name['NondINs'].get_subpopulation(start_index=805,  end_index=873,  subname='RHS_aIN', autotag=['RHS','aIN'])
pop_RHS_cIN = pops_by_name['NondINs'].get_subpopulation(start_index=873,  end_index=1065, subname='RHS_cIN', autotag=['RHS','cIN'])
pop_RHS_dla = pops_by_name['NondINs'].get_subpopulation(start_index=1065, end_index=1094, subname='RHS_dla', autotag=['RHS','dla'])
pop_RHS_dlc = pops_by_name['NondINs'].get_subpopulation(start_index=1094, end_index=1146, subname='RHS_dlc', autotag=['RHS','dlc'])


dINs = pops_by_name['dINs']
pop_LHS_dIN = dINs.get_subpopulation(start_index=0,   end_index=118,  subname='LHS_dIN',  autotag=['LHS','dIN'] )
pop_RHS_dIN = dINs.get_subpopulation(start_index=118, end_index=236,  subname='RHS_dIN',  autotag=['RHS','dIN'] )


rhs_subpops = [pop_RHS_MN, pop_RHS_RB, pop_RHS_aIN, pop_RHS_cIN, pop_RHS_dla, pop_RHS_dlc, pop_RHS_dIN]
lhs_subpops = [pop_LHS_MN, pop_LHS_RB, pop_LHS_aIN, pop_LHS_cIN, pop_LHS_dla, pop_LHS_dlc, pop_LHS_dIN]


# Drive to LHS RBS:
rb_drivers = Population('RBInput', component = RB_input, size=10, autotag=['RBINPUT'])
network.add(rb_drivers)
network.add(
        EventPortConnector(
            rb_drivers, 
            pop_LHS_RB.get_subpopulation(start_index=0,end_index=1,subname='triggered',autotag=[]),
            src_port_name='spike', 
            dst_port_name='recv_ampa_spike', 
            name='RBDrives' , 
            connector=AllToAllConnector(connection_probability=1.0), 
            delay='0ms', 
            parameter_map= {'weight': FixedValue('1nS')}  
            )
        )




# Work out the electrical coupling indices:
f = pylab.figure()
ax = f.add_subplot(111)
gap_junction_indices =   []
for dIN_pop in [(pop_LHS_dIN), (pop_RHS_dIN)]:
    print dIN_pop
    for i in range(dIN_pop.start_index, dIN_pop.end_index):
        for j in range(dIN_pop.start_index, i):
            #print i
            i_x = cell_positions['dINs'][i]
            j_x = cell_positions['dINs'][j]
            if abs(i_x -j_x) > 200:
                continue
            if random.uniform(0,1) > 0.4:
                continue
            gap_junction_indices.append( (i,j) )

            ax.plot([i],[j], 'x')
            ax.plot([j],[i], 'x')

#pylab.show()
#sys.exit(0)


network.add(
    ElectricalSynapseProjection( src_population =  dINs, dst_population =  dINs, connector=ExplicitIndicesLoop(gap_junction_indices), strength_S = 0.2e-9 * 10 * 10 * 10, injected_port_name = 'i_injected', name='E_Couple')
)


#for sp in rhs_subpops + lhs_subpops:
#    network.record_traces(sp , '*' )


# Recording:
#network.record_traces( rhs_subpops+lhs_subpops, 'V' )
#network.record_traces(pop_LHS_RB , 'syn_ampa_open' )
#network.record_traces(pop_LHS_RB , 'syn_ampa_i' )

network.record_traces([pop_LHS_dIN, pop_RHS_dIN], 'V' )
network.record_traces([pop_LHS_dIN, pop_RHS_dIN], 'i_injected' )
#network.record_traces([dINs, 'i_injected' )


#network.record_traces(pop_LHS_RB , 'syn_ampa_g' )
network.record_input_events( rhs_subpops+lhs_subpops , 'recv_nmda_spike' )
network.record_output_events( rhs_subpops+lhs_subpops + [rb_drivers] , 'spike' )


#network.finalise()


### Generate for NIOS:
##fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', output_c_filename='/tmp/nu/compilation/sim_WITHOUTBLUE.cpp', CPPFLAGS='-DON_NIOS=false -DUSE_BLUEVEC=false ', compile=True, output_exec_filename='/tmp/nu/compilation/sim_WITHOUTBLUE.x', run=False)
##fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', output_c_filename='/tmp/nu/compilation/sim_WITHBLUE.cpp', CPPFLAGS='-DON_NIOS=false -DUSE_BLUEVEC=true ',  compile=True, output_exec_filename='/tmp/nu/compilation/sim_WITHBLUE.x', run=False)
##assert False
fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ').results
results = HDF5SimulationResultFile("output.hd5")


filters_traces = [
   # "ALL{noise}",
   # "ALL{V_noisy}",
   # "ALL{V_vnoisy}",
   "ALL{V,dIN,LHS}",
   "ALL{V,dIN,RHS}",
   "ALL{i_injected,dIN,LHS}",
   "ALL{i_injected,dIN,RHS}",

   # "ALL{V,RB,LHS}",
   # "ALL{V,RB,RHS}",

   # "ALL{V,dla,LHS}",
   # "ALL{V,dla,RHS}",

   # "ALL{V,dlc,LHS}",
   # "ALL{V,dlc,RHS}",

   #"ALL{V,dIN,LHS}",
   #"ALL{V,dIN,RHS}",

   # "ALL{V,aIN,LHS}",
   # "ALL{V,aIN,RHS}",

   # "ALL{V,cIN,LHS}",
   # "ALL{V,cIN,RHS}",

   # "ALL{V,MN,LHS}",
   # "ALL{V,MN,RHS}",

   # "ALL{syn_ampa_open,RB,LHS}",
   # "ALL{syn_ampa_g,RB,LHS}",
   # "ALL{syn_ampa_i,RB,LHS}",


        ]

filters_spikes = [

    "ALL{EVENT:spike,RBINPUT}",
    "ALL{EVENT:spike,RB,LHS}",
    "ALL{EVENT:spike,RB,RHS}",

    "ALL{EVENT:spike,dIN,LHS}",
    "ALL{EVENT:spike,dIN,RHS}",

#    "ALL{EVENT:spike,dla,LHS}",
#    "ALL{EVENT:spike,dla,RHS}",
#    "ALL{EVENT:spike,dlc,LHS}",
#    "ALL{EVENT:spike,dlc,RHS}",
#
#    "ALL{EVENT:spike,MN,LHS}",
#    "ALL{EVENT:spike,MN,RHS}",
#
#    "ALL{EVENT:spike,aIN,LHS}",
#    "ALL{EVENT:spike,aIN,RHS}",
#
#    "ALL{EVENT:spike,cIN,LHS}",
#    "ALL{EVENT:spike,cIN,RHS}",

    "ALL{EVENT:spike,dIN}",
    "ALL{EVENT:spike,MN}",
]

sim_start = 0
sim_end = 1.0


#results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, xlim = (0,1) )
results.plot(trace_filters=filters_traces, spike_filters=None, xlim = (0,1) )



pylab.show()
