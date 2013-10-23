

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

    # For debugging:
    MRedocWriterVisitor().visit(dIN_comp).to_pdf("op_dIN.pdf")
    MRedocWriterVisitor().visit(MN_comp).to_pdf("op_MN.pdf")

    del dIN_comp
    del MN_comp
    del RB_input

with open(cache_file) as f:
    dIN_comp,MN_comp,RB_input = pickle.load(f)














network = Network()

dINs = network.create_population(name='dINs', component=dIN_comp, size=30)

network.create_eventportconnector(
            src_population=dINs,
            dst_population=dINs,
            src_port_name='spike',
            dst_port_name='recv_nmda_spike',
            name="dIN_dIN_NMDA", delay='1ms',
            connector=AllToAllConnector(0.3),
            parameter_map= {'weight': FixedValue("0.002nS")}
        )

network.create_electricalsynapseprojection(
    src_population=dINs,
    dst_population=dINs,
    connector=AllToAllConnector(0.3),
    strength_S = 0.3e-9,
    injected_port_name='i_injected',
    name='E_Couple')
    


network.record_output_events(dINs, 'spike' )
network.record_traces(dINs, 'V' )
network.record_traces(dINs, 'iCa iNa iKf iKs iLk syn_nmda_i' )
network.record_traces(dINs, 'nmda_vdep' )
#network.record_traces(dINs, 'exp_neg_nu nu' )


fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ').results
results = HDF5SimulationResultFile("output.hd5")









filters_traces = [
   "ALL{V}",
   "ALL{POPINDEX:0000} AND ANY{iCa,iNa,iLk,iKf,iKs,syn_nmda_i}",
   "ALL{POPINDEX:0000} AND ANY{nmda_vdep}",
]

filters_spikes = [

    "ALL{EVENT:spike}",
]


results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True )#, xlim = (0.075,0.20)  )
#results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0851,0.08545)  )



pylab.show()
