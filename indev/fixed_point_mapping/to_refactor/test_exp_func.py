

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


import dIN_model
import mn_model
import rb_input_model


import neurounits
from neurounits.ast_annotations.common import  NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


hdffile = __file__ + '.output.hdf5'
if os.path.exists(hdffile):
    os.unlink(hdffile)



nbits = 24

var_annots_tags = {}


src_text = """
define_component simple_hh {
    from std.math import exp, ln

    <=> TIME t:(ms)

    x = exp( t/{1s} / 10. )
    }
"""

var_annots_ranges = {
        't'             : NodeRange(min="0ms", max = "1.1s"),
        }


library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
comp = library_manager['simple_hh']
comp.expand_all_function_calls()


# Optimise the equations, to turn constant-divisions into multiplications:
from neurounits.visitors.common.equation_optimisations import OptimiseEquations
OptimiseEquations(comp)

comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))
RangeExpander().visit(comp)
#RangeExpander(expand_by=4).visit(comp)


comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

from neurounits.ast_annotations.common import NodeTagger
NodeTagger(var_annots_tags).visit(comp)










network = Network()

dINs = network.create_population(name='dINs', component=comp, size=1)




network.record_traces(dINs, 'x' )

results1 = CBasedEqnWriterFixedNetwork(network,
                                      output_filename='text_exp-Seq.hdf', 
                                      CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ', 
                                      step_size=0.05e-3, run_until=15.).results

results2 = CBasedEqnWriterFixedNetwork(network,
                                      output_filename='text_exp-BV.hdf', 
                                      CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=true ', 
                                      step_size=0.05e-3, run_until=15.).results


import hdfjive
results = hdfjive.HDF5SimulationResultFileSet(['text_exp-Seq.hdf', 'text_exp-BV.hdf']) 
filters_traces = [
   "ALL{x}",
]



results.plot(trace_filters=filters_traces, spike_filters=None, legend=True) #, xlim = (0.0,0.07)  )



pylab.show()
