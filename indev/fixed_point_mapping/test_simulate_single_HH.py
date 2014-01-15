

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.SVG]

import os
import pylab
import cPickle as pickle
import hashlib
import shutil
import subprocess

import neurounits
from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork, NumberFormat
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *


import neurounitscontrib.components.tadpole







#import components

def _build_sim(number_format):
    HH_comp = neurounits.ComponentLibrary.instantiate_component('HH')
    network = Network()
    dINs = network.create_population(
            name=('HH_%s'%number_format),
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
                    number_format = number_format,
                    ).results
    return results

def build_sim(number_format):
    try:
        return _build_sim(number_format=number_format)
    except subprocess.CalledProcessError:
        return None



import hdfjive
number_formats = [
        #NumberFormat.Int28,
        NumberFormat.GMP,
        #NumberFormat.Double,
        ]
results = [ build_sim(number_format=number_format) for number_format in number_formats ]
results = [r for r in results if r is not None]
results = hdfjive.HDF5SimulationResultFileSet(results)




filters_traces = [
   "ALL{V}",
   "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
   "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",

]

filters_spikes = [
    "ALL{spike}",
]





f1,f2 = results.plot(trace_filters=filters_traces,
             spike_filters=filters_spikes,
             legend=True,
             xlim = (0.0,0.7),
             fig_trace_kwargs= dict(figsize=(85/25.4, 2) ),
             fig_event_kwargs= dict(figsize=(85/25.4, 1) ),
               )


f1[0].savefig('_build/res_hh1_newA.svg')
f2[0].savefig('_build/res_hh1_newB.svg')

pylab.show()
