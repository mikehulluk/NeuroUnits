

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



hdffile = __file__ + '.output.hdf5'
if os.path.exists(hdffile):
    os.unlink(hdffile)







import components
HH_comp = neurounits.ComponentLibrary.instantiate_component('HH', nbits=24)

nbits=24
#for comp in [HH_comp]:
#    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
#    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )





network = Network()

dINs = network.create_population(
        name='HH',
        component=HH_comp,
        size=1,
        parameters={
            'nmda_multiplier': 1.0, 
            'ampa_multiplier': 1.0,
            'inj_current': "50pA",
            
            },
        )

network.record_output_events(dINs, 'spike' )
network.record_traces(dINs, 'V' )

results = CBasedEqnWriterFixedNetwork(
                network,
                output_filename=hdffile,
                CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                step_size=0.01e-3).results

                


filters_traces = [
   "ALL{V}",
   "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
   "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",

]

filters_spikes = [
    "ALL{EVENT:spike}",
]


results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0,0.7)  )



pylab.show()
