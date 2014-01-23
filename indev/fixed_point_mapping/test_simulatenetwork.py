

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.SVG]

import os
import neurounits

import numpy as np
import random
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork, NumberFormat
from hdfjive import HDF5SimulationResultFile
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *

import cPickle as pickle

from mreorg import PM


import neurounitscontrib.components.tadpole
dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')
MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN')
RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput')




#nbits=24




network = Network()
pop_components = {
        'NondINs': MN_comp,
        'dINs': dIN_comp,
        }
pop_params = {
    'dINs': {
            'nmda_multiplier': 1.0,
            #'ampa_multiplier': '~uniform(min=0.5,max=1.5)[]'
            'ampa_multiplier': 1.0,
            'inj_current':'0pA',
            },
    'NondINs': {}
}

with open('mh_reduced_connectome.pickle') as f:
    pop_sizes, connections, pop_breakdowns, cell_positions = pickle.load(f)



network = Network()
pops_by_name = {}
for pop_name, pop_size in pop_sizes.items():
    p = Population(name=pop_name, component=pop_components[pop_name], size=pop_size, parameters=pop_params[pop_name] )
    network.add(p)
    assert not pop_name in pops_by_name
    pops_by_name[pop_name] = p


for syn_index, ((pop1_name, pop2_name, (syn_type, strength) ), conns) in enumerate(connections.items()):
    print 'Adding connection: %s -> %s [type:%s strength:%s, num:%d]' % (pop1_name, pop2_name, syn_type, strength, len(conns))
    p1 = pops_by_name[pop1_name]
    p2 = pops_by_name[pop2_name]
    synpop_name='SynPop%02d' % syn_index
    weight = '%f nS'%strength
    network.add(
            EventPortConnector(p1,p2,
                src_port_name='spike',
                dst_port_name='recv_%s_spike' %syn_type,
                name=synpop_name,
                delay='1ms',
                connector=ExplicitIndicesSet(conns),
                parameter_map= {'weight': FixedValue(weight)} )
        )











#network.provide_events( pops_by_name['pop1'], event_port='recv_ampa_spike', evt_details = [50,60,70] )
non_dINs = pops_by_name['NondINs']
pop_LHS_MN  = non_dINs.get_subpopulation(start_index=0,   end_index=169, subname='LHS_MN',  autotag=['LHS','MN'])
pop_LHS_RB  = non_dINs.get_subpopulation(start_index=169, end_index=232, subname='LHS_RB',  autotag=['LHS','RB'])
pop_LHS_aIN = non_dINs.get_subpopulation(start_index=232, end_index=300, subname='LHS_aIN', autotag=['LHS','aIN'])
pop_LHS_cIN = non_dINs.get_subpopulation(start_index=300, end_index=492, subname='LHS_cIN', autotag=['LHS','cIN'])
pop_LHS_dla = non_dINs.get_subpopulation(start_index=492, end_index=521, subname='LHS_dla', autotag=['LHS','dla'])
pop_LHS_dlc = non_dINs.get_subpopulation(start_index=521, end_index=573, subname='LHS_dlc', autotag=['LHS','dlc'])


pop_RHS_MN  = non_dINs.get_subpopulation(start_index=573,  end_index=742,  subname='RHS_MN',  autotag=['RHS','MN'])
pop_RHS_RB  = non_dINs.get_subpopulation(start_index=742,  end_index=805,  subname='RHS_RB',  autotag=['RHS','RB'])
pop_RHS_aIN = non_dINs.get_subpopulation(start_index=805,  end_index=873,  subname='RHS_aIN', autotag=['RHS','aIN'])
pop_RHS_cIN = non_dINs.get_subpopulation(start_index=873,  end_index=1065, subname='RHS_cIN', autotag=['RHS','cIN'])
pop_RHS_dla = non_dINs.get_subpopulation(start_index=1065, end_index=1094, subname='RHS_dla', autotag=['RHS','dla'])
pop_RHS_dlc = non_dINs.get_subpopulation(start_index=1094, end_index=1146, subname='RHS_dlc', autotag=['RHS','dlc'])


dINs = pops_by_name['dINs']
pop_LHS_dIN = dINs.get_subpopulation(start_index=0,   end_index=118,  subname='LHS_dIN',  autotag=['LHS','dIN'] )
pop_RHS_dIN = dINs.get_subpopulation(start_index=118, end_index=236,  subname='RHS_dIN',  autotag=['RHS','dIN'] )


rhs_subpops = [pop_RHS_MN, pop_RHS_RB, pop_RHS_aIN, pop_RHS_cIN, pop_RHS_dla, pop_RHS_dlc, pop_RHS_dIN]
lhs_subpops = [pop_LHS_MN, pop_LHS_RB, pop_LHS_aIN, pop_LHS_cIN, pop_LHS_dla, pop_LHS_dlc, pop_LHS_dIN]


# Drive to LHS RBS:
rb_drivers = Population('RBInput', component = RB_input, size=10, autotag=['RBINPUT'])
network.add(rb_drivers)
network.add(
        EventPortConnector(
            rb_drivers,
            pop_RHS_RB.get_subpopulation(start_index=0,end_index=1,subname='triggered',autotag=[]),
            src_port_name='spike',
            dst_port_name='recv_ampa_spike',
            name='RBDrives' ,
            connector=AllToAllConnector(connection_probability=1.0),
            delay='0ms',
            parameter_map= {'weight': FixedValue('1nS')}
            )
        )




# Work out the electrical coupling indices:
gap_junction_indices =   []
for dIN_pop in [(pop_LHS_dIN), (pop_RHS_dIN)]:
    print dIN_pop
    for i in range(dIN_pop.start_index, dIN_pop.end_index):
        for j in range(dIN_pop.start_index, i):
            i_x = cell_positions['dINs'][i]
            j_x = cell_positions['dINs'][j]
            if abs(i_x -j_x) > 200:
                continue
            if random.uniform(0,1) > 0.2:
                continue
            gap_junction_indices.append( (i,j) )

            #ax.plot([i],[j], 'x')
            #ax.plot([j],[i], 'x')



GJ_comp =  neurounits.ComponentLibrary.instantiate_component('GJ')
assert not GJ_comp.has_state()





network.add(
    AnalogPortConnector(
        src_population =  dINs,
        dst_population =  dINs,
        port_map = [
            ('conn.v1', 'src.V'),
            ('conn.i1', 'src.i_injected'),
            ('conn.v2', 'dst.V'),
            ('conn.i2', 'dst.i_injected'),
            ],
        connector=ExplicitIndicesLoop(gap_junction_indices),
        connection_object=GJ_comp,
        connection_properties={
            'g': "2nS",
            },
        name='Ecoupling'
        )
)






network.record_output_events( [rb_drivers] , 'spike' )
network.record_output_events( lhs_subpops+rhs_subpops , 'spike' )
network.record_traces(lhs_subpops+rhs_subpops , 'V' )
network.record_traces([pop_LHS_dIN,pop_RHS_dIN], 'nmda_vdep')




results = CBasedEqnWriterFixedNetwork(
                    network,
                    CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                    step_size=0.1e-3 / 2.,
                    run_until=0.4,
                    number_format = NumberFormat.Int28,
                    #as_float=False,
                    output_filename="/local/scratch/mh735/neuronits.results-Seq-float.hdf",
                    output_c_filename='op-seq.cpp',
                    record_rate=1
                    ).results




#import test_simulatenetwork_plot



from hdfjive import HDF5SimulationResultFile, RasterGroup, RasterSubgroup

#results = HDF5SimulationResultFile("/local/scratch/mh735/neuronits.results-Seq-float.hdf")

import mreorg
#mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG] # , mreorg.FigFormat.SVG]

def build_raster_plot_obj(name, side):
        alpha=0.3
        size = 0.5
        return RasterGroup('%s\n%s' % (name, side), [
            RasterSubgroup("OUT:Spike", "ALL{spike,%s,%s}"%(name,side), {'color':'black', 'marker':'x', 's':2}),
            RasterSubgroup("IN: AMPA", "ALL{recv_ampa_spike,%s,%s}"%(name,side), {'color':'blue', 'marker':'.', 's':size }),
            #RasterSubgroup("IN: NMDA", "ALL{recv_nmda_spike,%s,%s}"%(name,side), {'color':'green', 'marker':'.', 's':size }),
            #RasterSubgroup("IN: Inhib", "ALL{recv_inh_spike,%s,%s} "%(name,side), {'color':'red', 'marker':'.', 's':size }),
            ] )




#xlim=(95e-3,750e-3)
#xlim=(95e-3,300e-3)
xlim=(45e-3,300e-3)
#xlim=(30e-3,1000e-3)


fig=results.raster_plot([
        RasterGroup('RB', [
            RasterSubgroup('Spike', "ALL{spike,RBINPUT}", {'color':'red'})
            ] ),
        build_raster_plot_obj('RB', 'RHS'),
        #build_raster_plot_obj('RB', 'LHS'),

        build_raster_plot_obj('dla', 'RHS'),
        #build_raster_plot_obj('dla', 'LHS'),

        build_raster_plot_obj('dlc', 'RHS'),
        #build_raster_plot_obj('dlc', 'LHS'),

        build_raster_plot_obj('dIN', 'RHS'),
        build_raster_plot_obj('dIN', 'LHS'),

        build_raster_plot_obj('aIN', 'RHS'),
        build_raster_plot_obj('aIN', 'LHS'),

        build_raster_plot_obj('cIN', 'RHS'),
        build_raster_plot_obj('cIN', 'LHS'),

        #build_raster_plot_obj('MN', 'RHS'),
        #build_raster_plot_obj('MN', 'LHS'),

        RasterGroup('MN\nLHS', [
            RasterSubgroup("MN:LHS", "ALL{spike,MN,LHS}", {'color':'blue', 'marker':'x', 's':2}),
            ] ),
        RasterGroup('MN\nRHS', [
            RasterSubgroup("MN:RHS", "ALL{spike,MN,RHS}", {'color':'green', 'marker':'x', 's':2}),
            ] ),

        #RasterGroup('MN', [
        #    RasterSubgroup("MN:LHS", "ALL{spike,MN,LHS}", {'color':'blue', 'marker':'x', 's':2}),
        #    RasterSubgroup("MN:RHS", "ALL{spike,MN,RHS}", {'color':'green', 'marker':'x', 's':2}),
        #    ] )

        ],

        xlim=xlim,
        fig_kwargs=dict(figsize=(185/25.4, 4) ),
        
        )
fig.subplots_adjust(left=0.1,top=0.95)        

from matplotlib.ticker import MaxNLocator

for ax in fig.get_axes():
    ax.yaxis.set_major_locator(MaxNLocator(3))
    
fig.savefig("_build/fig_res_tadpole1.svg")


filters_traces = [
   "ALL{V,dIN,LHS} AND ANY{POPINDEX:0000,POPINDEX:0001,POPINDEX:0002}",
   "ALL{nmda_vdep,dIN,LHS} AND ANY{POPINDEX:0000,POPINDEX:0001,POPINDEX:0002}",
   #~ "ALL{V,RB,LHS}",
   #~ "ALL{V,dla,RHS}",
   #~ "ALL{V,dla,LHS}",
   #~ "ALL{V,dlc,RHS}",
   #~ "ALL{V,dlc,LHS}",
   #~ "ALL{V,aIN,RHS}",
   #~ "ALL{V,aIN,LHS}",
   #~ "ALL{V,cIN,RHS}",
   #~ "ALL{V,cIN,LHS}",
   #~ "ALL{V,dIN,RHS}",
   #~ "ALL{V,dIN,LHS}",
   #~ "ALL{V,MN,RHS}",
   #~ "ALL{V,MN,LHS}",
#~ 
   #~ "ALL{dIN,V_vnoisy,RHS}",
   #~ "ALL{dIN,V_vnoisy,LHS}",
   #~ "ALL{dIN,noise,RHS}",
   #~ "ALL{dIN,noise,LHS}",
   #~ "ALL{dIN,noise_raw,RHS}",
   #~ "ALL{dIN,noise_raw,LHS}",
   #~ "ALL{V,MN,LHS}",
]



def plot_graph(filt, xlabel=None, ylabel=None, legend=False):
        fig = pylab.figure(figsize=(85/25.4, 2.5))
        fig.subplots_adjust(left=0.15)
        trs = results.filter_traces(filt)

        xlim = (0.25,0.35)
        print 'Plotting:', filt, len(trs)
        for res in trs:
            if xlim:
                time_mask = np.logical_and(
                                res.raw_data.time_pts>xlim[0],
                                res.raw_data.time_pts<xlim[1],
                        )
                time, data = res.raw_data.time_pts[time_mask], res.raw_data.data_pts[time_mask]
            else:
                time, data = res.raw_data.time_pts, res.raw_data.data_pts

            #if xscale is not None:
            #    time = time * xscale
            pylab.plot(time, data,'x-', label=','.join(res.tags), ms=2 )


        pylab.ylabel(ylabel)
        if legend:
            pylab.legend()

        pylab.autoscale(axis='y')
        if xlabel is not None:
            pylab.xlabel(xlabel)


        return fig


f1 = plot_graph( "ALL{V,dIN,LHS} AND ANY{POPINDEX:0000,POPINDEX:0001,POPINDEX:0002}", ylabel='Voltage (V)' )
f2 = plot_graph( "ALL{nmda_vdep,dIN,LHS} AND ANY{POPINDEX:0000,POPINDEX:0001,POPINDEX:0002}",ylabel='NMDA-vdep' )


f1.get_axes()[0].set_yticks([-60e-3, -30e-3, 0e-3, 30e-3])
f1.get_axes()[0].set_yticklabels(['-60','-30','0','30'])

                
f1.savefig("_build/fig_res_tadpole2a.svg")
f2.savefig("_build/fig_res_tadpole2b.svg")












pylab.show()
