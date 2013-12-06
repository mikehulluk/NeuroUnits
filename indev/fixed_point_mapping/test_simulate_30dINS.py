

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


import dIN_model
import mn_model
import rb_input_model
import cPickle as pickle

from mreorg import PM
import hashlib

#~ 
#~ src_string = open('dIN_model.py').read() + open('mn_model.py').read()
#~ md5_str = hashlib.md5(src_string).hexdigest()
#~ 
#~ 
#~ use_cache=True
#~ #use_cache=False
#~ cache_file = 'caches/.din_model_cache_%s'%(md5_str)
#~ if not os.path.exists('caches/'):
    #~ os.makedirs('caches')
#~ # Delete the cache-file if we are not using it:
#~ if not use_cache:
    #~ if os.path.exists(cache_file):
        #~ os.unlink(cache_file)
#~ 
#~ if not os.path.exists(cache_file):
    #~ MN_comp = mn_model.get_MN(nbits=24)
    #~ RB_input = rb_input_model.get_rb_input(nbits=24)
    #~ dIN_comp = dIN_model.get_dIN(nbits=24)
    #~ with open(cache_file,'w') as f:
        #~ pickle.dump([dIN_comp, MN_comp, RB_input], f, )
#~ 
    #~ # For debugging:
    #~ MRedocWriterVisitor().visit(dIN_comp).to_pdf("op_dIN.pdf", single_page=True)
    #~ MRedocWriterVisitor().visit(MN_comp).to_pdf("op_MN.pdf", single_page=True)
#~ 
    #~ del dIN_comp
    #~ del MN_comp
    #~ del RB_input
#~ 
#~ with open(cache_file) as f:
    #~ dIN_comp,MN_comp,RB_input = pickle.load(f)
#~ 
#~ 
#~ 


import components
dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN', nbits=24)
MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN', nbits=24)
RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput', nbits=24)

nbits=24
#for comp in [dIN_comp, MN_comp, RB_input]:
#    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
#    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )






def get_results():

    network = Network()

    #dINs = network.create_population(name='dINs', component=dIN_comp, size=30)
    dINs = network.create_population(name='dINs', component=dIN_comp, size=30)

    network.create_eventportconnector(
                src_population=dINs,
                dst_population=dINs,
                src_port_name='spike',
                dst_port_name='recv_nmda_spike',
                name="dIN_dIN_NMDA", delay='1ms',
                connector=AllToAllConnector(0.2),
                parameter_map= {'weight': FixedValue("100pS")}
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
    network.record_traces(dINs, 'V' )


    op_filename = 'output_float.hd5'
    if os.path.exists(op_filename):
        os.unlink(op_filename)

    results1 = CBasedEqnWriterFixedNetwork(
                        network,
                        output_filename=op_filename,
                        CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                        step_size=0.1e-3,
                        run_until=1.0,
                        as_float=True,
                        ).results


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
results = HDF5SimulationResultFileSet(['output_float.hd5', 'output_fixed.hd5'])


pylab.margins(0.1)


filters_traces = [
    'ALL{POPINDEX:0000,V}',
    'ALL{float,V}',
    'ALL{fixed,V}',
    ]
for symbol in sorted(dIN_comp.terminal_symbols, key=lambda o:o.symbol):
    filters_traces.append( "ALL{POPINDEX:0000} AND ANY{%s}" % symbol.symbol )

#filters_traces = [
#   "ALL{V}",
#
#
#   "ALL{POPINDEX:0000} AND ANY{iLk}",
#   "ALL{POPINDEX:0000} AND ANY{iCa}",
#   "ALL{POPINDEX:0000} AND ANY{iNa}",
#   "ALL{POPINDEX:0000} AND ANY{iKf}",
#   "ALL{POPINDEX:0000} AND ANY{iKs}",
#
#]











#filters_traces = [
#   "ALL{V}",
#   "ALL{POPINDEX:0000} AND ANY{iLk,iKs,iKf,iNa}",
#   "ALL{POPINDEX:0000} AND ANY{kf_n,ks_n,na_h,na_m}",
#
#   "ALL{POPINDEX:0000} AND ANY{alpha_kf_n,beta_kf_n}",
#   "ALL{POPINDEX:0000} AND ANY{alpha_ks_n,beta_ks_n}",
#   #"ALL{POPINDEX:0000} AND ANY{ks_n}",
#   #"ALL{POPINDEX:0000} AND ANY{syn_nmda_i}",
#   #"ALL{POPINDEX:0000} AND ANY{syn_nmda_A,syn_nmda_B}",
#   #"ALL{POPINDEX:0000} AND ANY{syn_nmda_g_raw}",
#]
#
#filters_spikes = [
#
#    "ALL{EVENT:spike}",
#]
#
##"ALL{POPINDEX:0000} AND ANY{iCa,iNa,iLk,iKf,iKs,syn_nmda_i}",
##"ALL{POPINDEX:0000} AND ANY{nmda_vdep}",

results.plot(trace_filters=filters_traces,  legend=True )#, xlim = (0.075,0.20)  )
#results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0851,0.08545)  )



pylab.show()
