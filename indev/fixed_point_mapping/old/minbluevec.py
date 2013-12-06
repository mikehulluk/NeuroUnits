


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



import neurounits
from neurounits.ast_annotations.common import  NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander







































def get_comp(nbits):
    src_text = """
    define_component simple_hh {
        V' = {1mV/s}
        k = V *2
        S' = -k/{10ms}
        initial {
            V = -36mV
            S = -56mV
        }
    }
    """




    var_annots_ranges = {
        '__t__'             : NodeRange(min="0ms", max = "1.1s"),
        'V'             : NodeRange(min="-100mV", max = "60mV"),
        'S'             : NodeRange(min="-100mV", max = "60mV"),
        }

    var_annots_tags = {
        'V': 'Voltage',
        'S': 'Voltage',
        }



    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_hh']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)



    #comp.annotate_ast( NodeRangeAnnotator(var_annots_ranges) )
    RangeExpander().visit(comp)

    # New range optimiser:
    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))


    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    #from neurounits.ast_annotations.common import NodeTagger
    #NodeTagger(var_annots_tags).visit(comp)

    return comp












comp = get_comp(24)

network = Network()
p = Population(name='Pop1', component=comp, size=1)
network.add(p)

network.record_traces( p, 'V' )
network.record_traces( p, 'S' )

network.finalise()


# Generate for NIOS:
#fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', output_c_filename='/tmp/nu/compilation/sim_WITHOUTBLUE.cpp', CPPFLAGS='-DON_NIOS=false -DUSE_BLUEVEC=false ', compile=True, output_exec_filename='/tmp/nu/compilation/sim_WITHOUTBLUE.x', run=False)
#fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', output_c_filename='/tmp/nu/compilation/sim_WITHBLUE.cpp', CPPFLAGS='-DON_NIOS=false -DUSE_BLUEVEC=true ',  compile=True, output_exec_filename='/tmp/nu/compilation/sim_WITHBLUE.x', run=False)

#assert False
fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=true').results
results = HDF5SimulationResultFile("output.hd5")


filters_traces = [
    "ALL{V}",
    "ALL{S}",
        ]

filters_spikes = [
]

sim_start = 0
sim_end = 1.0



for filt in filters_traces:
    pylab.figure(figsize=(20,16))
    trs = results.filter_traces(filt)
    print 'Plotting:', filt, len(trs)
    for res in trs:
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts, label=','.join(res.tags), ms='x'  )
    pylab.xlim(sim_start, sim_end)
    pylab.ylabel(filt)
    #pylab.legend()
    PM.save_active_figures()


for filt in filters_spikes:
    pylab.figure(figsize=(20,16))
    trs = results.filter_events(filt)
    print 'Plotting:', filt, len(trs)
    for i,res in enumerate(trs):
        evt_times = res.evt_times
        pylab.plot( evt_times, i+ 0*evt_times, 'x', label=','.join(res.tags))
    pylab.xlim(sim_start, sim_end)
    pylab.ylabel(filt)
    #pylab.legend()
    PM.save_active_figures()



pylab.show()
