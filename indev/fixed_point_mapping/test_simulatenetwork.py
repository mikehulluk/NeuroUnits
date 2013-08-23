

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG,mreorg.FigFormat.SVG]

import neurounits

import numpy as np
import pylab

from neurounits.tools.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile

#from neurounits.ast_annotations.common import NodeRangeAnnotator, NodeFixedPointFormatAnnotator,\
#    NodeRange, NodeToIntAnnotator, _NodeRangeFloat, RangeExpander



import dIN_model



nbits = 24
dIN_comp = dIN_model.get_dIN(nbits=nbits)







from neurounits.tools.population_infrastructure import *
network = Network()
p1 = Population(name='LHSdIN', component=dIN_comp, size=30 )
p2 = Population(name='RHSdIN', component=dIN_comp, size=30 )
network.add(p1)
network.add(p2)

p3 = Population(name='RHSNeurons2', component=dIN_comp, size=700 )
p4 = Population(name='RHSNeurons3', component=dIN_comp, size=700 )
network.add(p3)
network.add(p4)


# Electrical synapses:
e1 = ElectricalSynapseProjection(src_population=p1, dst_population=p1, connection_probability=0.2, strength_ohm=300e6, name='ElecLHSdIN', injected_port_name='i_injected')
network.add(e1)

# Chemical Synapses:
network.add(
        EventPortConnector(p1,p1, src_port_name='spike', dst_port_name='recv_nmda_spike', name='Conn01', connector=AllToAllConnector(connection_probability=0.3) )
        )

network.add( 
        EventPortConnector(p3,p4, src_port_name='spike', dst_port_name='recv_nmda_spike', name='ConnX02', connector=AllToAllConnector(connection_probability=0.3) )
        )
network.add( 
        EventPortConnector(p4,p3, src_port_name='spike', dst_port_name='recv_nmda_spike',  name='ConnX03', connector=AllToAllConnector(connection_probability=0.3) )
        )








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
    pylab.ylabel(symbol)
    #pylab.legend()

pylab.show()
