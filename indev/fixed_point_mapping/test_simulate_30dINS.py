

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG] #,mreorg.FigFormat.SVG]

import os
import neurounits

import numpy as np
import random
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFileSet
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *

import components
import cPickle as pickle

from mreorg import PM
import hashlib




import components
dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')
MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN')
RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput')





def get_results():

    network = Network()

    
    dINs = network.create_population(
            name='dINs',
            component=dIN_comp,
            size=30,
            parameters= {
                'nmda_multiplier': 1.0, 
                'ampa_multiplier': 1.0, 
                'inj_current':'20pA',
            },

            )

    network.create_eventportconnector(
                src_population=dINs,
                dst_population=dINs,
                src_port_name='spike',
                dst_port_name='recv_nmda_spike',
                name="dIN_dIN_NMDA", delay='1ms',
                connector=AllToAllConnector(0.2),
                parameter_map= {'weight': FixedValue("200pS")}
            )

    network.create_electricalsynapseprojection(
        src_population=dINs,
        dst_population=dINs,
        connector=AllToAllConnector(0.3),
        strength_S = 0.3e-9,
        injected_port_name='i_injected',
        name='E_Couple')




    network.record_input_events(dINs, 'recv_nmda_spike' )
    network.record_input_events(dINs, 'recv_inh_spike' )
    network.record_input_events(dINs, 'recv_ampa_spike' )
    network.record_output_events(dINs, 'spike' )
    network.record_traces(dINs, '*' )
    #network.record_traces(dINs, 'V' )


   # op_filename = 'output_float.hd5'
   # if os.path.exists(op_filename):
   #        os.unlink(op_filename)
   #
   # results1 = CBasedEqnWriterFixedNetwork(
   #                     network,
   #                     output_filename=op_filename,
   #                     CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
   #                     step_size=0.1e-3,
   #                     run_until=1.0,
   #                     as_float=True,
   #                     nbits=24,
   #                     ).results


    op_filename = 'output_fixed.hd5'
    if os.path.exists(op_filename):
        os.unlink(op_filename)

    results2 = CBasedEqnWriterFixedNetwork(
                        network,
                        output_filename=op_filename,
                        CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                        step_size=0.1e-3,
                        run_until=1.0,
                        as_float=False,
                        ).results

get_results()
results = HDF5SimulationResultFileSet(['output_fixed.hd5'])


pylab.margins(0.1)


filters_traces = [
    'ALL{POPINDEX:0000,V}',
    'ALL{V}',

    'ALL{POPINDEX:0001,V}',
    'ALL{POPINDEX:0002,V}',
    'ALL{POPINDEX:0003,V}',
    
    #'ALL{fixed,V}',
    ]


for symbol in sorted(dIN_comp.terminal_symbols, key=lambda o:o.symbol):
    filters_traces.append( "ALL{POPINDEX:0000} AND ANY{%s}" % symbol.symbol )


results.plot(trace_filters=filters_traces,  legend=True )#, xlim = (0.075,0.20)  )
#results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0851,0.08545)  )



pylab.show()
