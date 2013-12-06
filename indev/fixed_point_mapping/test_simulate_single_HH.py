

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG]

import os
import pylab
import cPickle as pickle
import hashlib
import shutil
import subprocess

import neurounits
from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *










import components

def _build_sim(nbits):
    HH_comp = neurounits.ComponentLibrary.instantiate_component('HH')
    network = Network()
    dINs = network.create_population(
            name=('HH%03d'%nbits) if nbits is not None else 'HHfloat',
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
                    CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                    step_size=0.01e-3,
                    run_until=1.0,
                    nbits=nbits or 24,
                    as_float = nbits is not None
                    ).results
    return results

def build_sim(nbits):
    try:
        return _build_sim(nbits=nbits)
    except subprocess.CalledProcessError:
        return None
        
    

import hdfjive
results = [ build_sim(nbits=nbits) for nbits in [None, 12, 14, 16, 18, 24, 30, 32, 34 ] ]
results = [r for r in results if r is not None]
results = hdfjive.HDF5SimulationResultFileSet(results)

results1 = build_sim(nbits=8)
results1 = build_sim(nbits=8)
results1 = build_sim(nbits=8)

results2 = build_sim(nbits=20)



filters_traces = [
   "ALL{V}",
   "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
   "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",

]

filters_spikes = [
    "ALL{spike}",
]





results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0,0.7)  )



pylab.show()
