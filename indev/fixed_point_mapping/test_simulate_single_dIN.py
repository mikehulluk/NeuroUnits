

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG]

import os
import pylab
import cPickle as pickle
import hashlib
import shutil


import neurounits
from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *












import components
dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')
MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN')
RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput')

nbits=24










network = Network()

dINs = network.create_population(name='dINs', component=dIN_comp, size=1)

#network.create_eventportconnector(
#            src_population=dINs,
#            dst_population=dINs,
#            src_port_name='spike',
#            dst_port_name='recv_nmda_spike',
#            name="dIN_dIN_NMDA", delay='1ms',
#            connector=AllToAllConnector(0.3),
#            parameter_map= {'weight': FixedValue("0.2nS")}
#        )
#
#network.create_electricalsynapseprojection(
#    src_population=dINs,
#    dst_population=dINs,
#    connector=AllToAllConnector(0.3),
#    strength_S = 0.3e-9,
#    injected_port_name='i_injected',
#    name='E_Couple')



network.record_output_events(dINs, 'spike' )
network.record_traces(dINs, 'V' )
network.record_traces(dINs, 'iCa iNa iKf iKs iLk syn_nmda_i iInj_local' )
network.record_traces(dINs, 'ks_n kf_n na_m na_h ca_m' )
network.record_traces(dINs, '' )
network.record_traces(dINs, 'nmda_vdep' )


results = CBasedEqnWriterFixedNetwork(network, CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ', step_size=0.01e-3).results
shutil.copy(hdffile, os.path.expanduser("~/debugging/") )


filters_traces = [
   "ALL{V}",
   "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
   "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",
   #"ALL{POPINDEX:0000} AND ANY{iCa,iNa,iLk,iKf,iKs,syn_nmda_i}",
   #"ALL{POPINDEX:0000} AND ANY{nmda_vdep}",
]

filters_spikes = [

    "ALL{EVENT:spike}",
]


results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0,0.07)  )



pylab.show()
