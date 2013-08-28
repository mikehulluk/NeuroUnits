

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



#nbits = 24
dIN_comp = dIN_model.get_dIN(nbits=24)


from neurounits.writers import MRedocWriterVisitor
MRedocWriterVisitor().visit(dIN_comp).to_pdf("op.pdf")



from neurounits.tools.population_infrastructure import *
network = Network()
p1 = Population(name='dINs', component=dIN_comp, size=100 )
p2 = Population(name='NondINs', component=dIN_comp, size=30 )
network.add(p1)
#network.add(p2)

#p3 = Population(name='RHSNeurons2', component=dIN_comp, size=700 )
#p4 = Population(name='RHSNeurons3', component=dIN_comp, size=700 )
#network.add(p3)
#network.add(p4)
#
#
## Electrical synapses:
#e1 = ElectricalSynapseProjection(src_population=p1, dst_population=p1, connection_probability=0.2, strength_ohm=300e6, name='ElecLHSdIN', injected_port_name='i_injected')
#network.add(e1)
#
## Chemical Synapses:
#network.add(
#        EventPortConnector(p1,p1, src_port_name='spike', dst_port_name='recv_nmda_spike', name='Conn01', connector=AllToAllConnector(connection_probability=0.3) )
#        )
#
#network.add( 
#        EventPortConnector(p3,p4, src_port_name='spike', dst_port_name='recv_nmda_spike', name='ConnX02', connector=AllToAllConnector(connection_probability=0.3) )
#        )
#network.add( 
#        EventPortConnector(p4,p3, src_port_name='spike', dst_port_name='recv_nmda_spike',  name='ConnX03', connector=AllToAllConnector(connection_probability=0.3) )
#        )
#



pop_components = {
        'pop1': dIN_comp,
        'pop2': dIN_comp,
        }

import cPickle as pickle
with open('mh_reduced_connectome.pickle') as f:
    pop_sizes, connections, pop_breakdowns = pickle.load(f)



network = Network()
pops_by_name = {}
for pop_name, pop_size in pop_sizes.items():
    p = Population(name=pop_name, component=pop_components[pop_name], size=pop_size)
    network.add(p)
    assert not pop_name in pops_by_name
    pops_by_name[pop_name] = p


for syn_index, ((pop1_name, pop2_name, (syn_type, strength) ), conns) in enumerate(connections.items()):
    print 'Adding connection: %s -> %s [type:%s strength:%s, num:%d]' % (pop1_name, pop2_name, syn_type, strength, len(conns))

    p1 = pops_by_name[pop1_name]
    p2 = pops_by_name[pop2_name]
    synpop_name='SynPop%02d' % syn_index
    network.add(
        EventPortConnector(p1,p2, src_port_name='spike', dst_port_name='recv_%s_spike' %syn_type, name=synpop_name , connector=ExplicitIndices(conns) )
        )

network.provide_events( pops_by_name['pop1'], event_port='recv_ampa_spike', evt_details = [50,60,70] )




#assert False




record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','iInj_local','i_nmda', 'nmda_vdep', 'iLk','iKf']
record_symbols = ['syn_nmda_A', 'syn_nmda_B', 'V','k','i_nmda', 'nmda_vdep' , 'iLk','iKf','kf_n' , 'iInj_local']
record_symbols = ['nu', 'exp_neg_nu',   'V','iCa', 'ca_m','ca_m_inf','tau_ca_m', 'tau_ca_m_cl','alpha_ca_m','beta_ca_m','iNa','iKf','iKs', 'beta_ca_m_2', 'beta_ca_m_1',]
record_symbols = ['V','syn_ampa_A', 'syn_ampa_B']
# Just generate the file:
CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', run=False, output_c_filename='/auto/homes/mh735/Desktop/tadpole1.cpp', compile=False, CPPFLAGS='-DON_NIOS=true', record_symbols=record_symbols )



fixed_sim_res = CBasedEqnWriterFixedNetwork(network, output_filename='output.hd5', CPPFLAGS='-DON_NIOS=false', record_symbols=record_symbols).results
results = HDF5SimulationResultFile("output.hd5")

for symbol in record_symbols:
    pylab.figure(figsize=(20,16))
    print 'Plotting:', symbol

    for res in results.filter(" ALL{%s} AND ANY{POPINDEX:000, POPINDEX:001,POPINDEX:002,POPINDEX:003, POPINDEX:118, POPINDEX:119,POPINDEX:120,POPINDEX:168,POPINDEX:169,POPINDEX:170}" % symbol):
    #for res in results.filter("ALL{%s,POPINDEX:001}" % symbol):
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts, label=','.join(res.tags), ms='x'  )
        #print np.min(res), np.max(res)
    pylab.ylabel(symbol)
    pylab.legend()

pylab.figure(figsize=(20,16))
pylab.ylabel('Currents (pA)')
for symbol in record_symbols:
    if symbol[0] != 'i':
        continue
    #if symbol=='iCa':
    #    continue

    for res in results.filter(symbol):
        pylab.plot(res.raw_data.time_pts, res.raw_data.data_pts * 1e12, label=symbol  )

pylab.show()

#f = pylab.figure(figsize=(20,16))
#ax1 = f.add_subplot(211)
#ax2 = f.add_subplot(212)
#voltage = results.filter('V')[0].raw_data
#beta_ca = results.filter('beta_ca_m')[0].raw_data
#beta_ca_1 = results.filter('beta_ca_m_1')[0].raw_data
#beta_ca_2 = results.filter('beta_ca_m_2')[0].raw_data
#
#
#R = (voltage.data_pts + 25e-3) > 0
#switches = np.logical_xor(R, np.roll(R,1) )
##switch_points = (np.diff( (voltage.data_pts - (-25e-3)) > 0 ) ** 2 ) > 0.5
#switch_points = np.where( switches)[0]
#print switch_points
#
#ax1.plot(voltage.time_pts, voltage.data_pts, label='Voltage')
#ax2.plot(beta_ca.time_pts, beta_ca.data_pts, label='Beta')
#ax2.plot(beta_ca_1.time_pts, beta_ca_1.data_pts, label='Beta1')
#ax2.plot(beta_ca_2.time_pts, beta_ca_2.data_pts, label='Beta2')
#
#ax1.set_xlim((0.07, 0.1))
#ax2.set_xlim((0.07, 0.1))
#
#for ax in [ax1,ax2]:
#    for sw in switch_points:
#        ax.axvline( voltage.time_pts[sw], ls='--',color='k')
#pylab.legend()
#
#
#
#
#pylab.figure()
#pylab.plot( 
#        beta_ca.data_pts[switch_points[0]+1:switch_points[1]-1 ],
#        beta_ca_2.data_pts[switch_points[0]+1:switch_points[1]-1 ] )
#
#
#dy = beta_ca.data_pts[ switch_points[1] -1 ] - beta_ca.data_pts[ switch_points[0] +1 ] 
#dx = beta_ca_2.data_pts[ switch_points[1] -1 ] - beta_ca_2.data_pts[ switch_points[0] +1 ] 
#
#print 'dy:', dy
#print 'dx:', dx
#
#print dy/dx
#
#
#
#
#pylab.legend()



pylab.show()
