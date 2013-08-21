

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG,mreorg.FigFormat.SVG]

import neurounits

import numpy as np
import pylab

from neurounits.tools.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile

from neurounits.ast_annotations.common import NodeRangeAnnotator, NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator, _NodeRangeFloat, RangeExpander



import dIN_model



nbits = 24
comp = dIN_model.get_dIN(nbits=nbits)

#from neurounits.writers import MRedocWriterVisitor
#MRedocWriterVisitor().visit(comp).to_pdf('op.pdf')
#
## Setup the annotations:
#comp.annotate_ast( NodeRangeAnnotator(var_annots_ranges) )
#RangeExpander().visit(comp)
#comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
#comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )



#assert False






from neurounits.tools.population_infrastructure import *
network = Network()
p1 = Population(name='LHSdIN', component=comp, size=30 )
p2 = Population(name='RHSdIN', component=comp, size=30 )
network.add(p1)
network.add(p2)

p3 = Population(name='RHSNeurons2', component=comp, size=700 )
p4 = Population(name='RHSNeurons3', component=comp, size=700 )
network.add(p3)
network.add(p4)


# Electrical synapses:
e1 = ElectricalSynapseProjection(src_population=p1, dst_population=p1, connection_probability=0.2, strength_ohm=300e6, name='ElecLHSdIN', injected_port_name='i_injected')
network.add(e1)

# Chemical Synapses:
s1 = EventPortConnector(p1,p1, src_port_name='spike', dst_port_name='recv_nmda_spike', connection_probability=0.1, name='Conn01' )
network.add(s1)

network.add( 
        EventPortConnector(p3,p4, src_port_name='spike', dst_port_name='recv_nmda_spike', connection_probability=0.0, name='ConnX02' )
        )
#network.add( 
#        EventPortConnector(p4,p3, src_port_name='spike', dst_port_name='recv_nmda_spike', connection_probability=0.1, name='ConnX03' )
#        )








record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','iInj_local','i_nmda', 'nmda_vdep', 'iLk','iKf']
record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','i_nmda', 'nmda_vdep' , 'iLk','iKf','kf_n' , 'iInj_local']
record_symbols = ['V']
# Just generate the file:
CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', run=False, output_c_filename='/auto/homes/mh735/Desktop/tadpole1.cpp', compile=False, CPPFLAGS='-DON_NIOS=true', record_symbols=record_symbols )



fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false', record_symbols=record_symbols).results
results = HDF5SimulationResultFile("output.hd5")

for symbol in record_symbols:
    pylab.figure(figsize=(20,16))
    print 'Plotting:', symbol

    for res in results.filter(symbol):
    #for res in results.filter("ALL{%s,POPINDEX:001}" % symbol):
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts, label=','.join(res.tags)  )
        print np.min(res), np.max(res)
    pylab.legend()

pylab.show()
