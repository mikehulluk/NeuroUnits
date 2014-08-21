
from hdfjive import HDF5SimulationResultFile, RasterGroup, RasterSubgroup

results = HDF5SimulationResultFile("/tmp/neuronits.results-Seq-float.hdf")

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG] # , mreorg.FigFormat.SVG]

def build_raster_plot_obj(name, side):
        #alpha=0.3
        size = 0.5
        return RasterGroup('%s\n%s' % (name, side), [
            RasterSubgroup("OUT:Spike", "ALL{spike,%s,%s}"%(name,side), {'color':'black', 'marker':'x', 's':2}),
            RasterSubgroup("IN: AMPA", "ALL{recv_ampa_spike,%s,%s}"%(name,side), {'color':'blue', 'marker':'.', 's':size }),
            #RasterSubgroup("IN: NMDA", "ALL{recv_nmda_spike,%s,%s}"%(name,side), {'color':'green', 'marker':'.', 's':size }),
            #RasterSubgroup("IN: Inhib", "ALL{recv_inh_spike,%s,%s} "%(name,side), {'color':'red', 'marker':'.', 's':size }),
            ] )


xlim=(30e-3,1000e-3)


results.raster_plot([
        RasterGroup('RB', [
            RasterSubgroup('Spike', "ALL{spike,RBINPUT}", {'color':'red'})
            ] ),
        build_raster_plot_obj('RB', 'RHS'),
        build_raster_plot_obj('RB', 'LHS'),

        build_raster_plot_obj('dla', 'RHS'),
        build_raster_plot_obj('dla', 'LHS'),

        build_raster_plot_obj('dlc', 'RHS'),
        build_raster_plot_obj('dlc', 'LHS'),

        build_raster_plot_obj('dIN', 'RHS'),
        build_raster_plot_obj('dIN', 'LHS'),

        build_raster_plot_obj('aIN', 'RHS'),
        build_raster_plot_obj('aIN', 'LHS'),

        build_raster_plot_obj('cIN', 'RHS'),
        build_raster_plot_obj('cIN', 'LHS'),

        build_raster_plot_obj('MN', 'RHS'),
        build_raster_plot_obj('MN', 'LHS'),


        RasterGroup('MN', [
            RasterSubgroup("MN:LHS", "ALL{spike,MN,LHS}", {'color':'blue', 'marker':'x', 's':2}),
            RasterSubgroup("MN:RHS", "ALL{spike,MN,RHS}", {'color':'green', 'marker':'x', 's':2}),
            ] )

        ],

        xlim=xlim
        )


filters_traces = [
   "ALL{V,RB,RHS}",
   "ALL{V,RB,LHS}",
   "ALL{V,dla,RHS}",
   "ALL{V,dla,LHS}",
   "ALL{V,dlc,RHS}",
   "ALL{V,dlc,LHS}",
   "ALL{V,aIN,RHS}",
   "ALL{V,aIN,LHS}",
   "ALL{V,cIN,RHS}",
   "ALL{V,cIN,LHS}",
   "ALL{V,dIN,RHS}",
   "ALL{V,dIN,LHS}",
   "ALL{V,MN,RHS}",
   "ALL{V,MN,LHS}",

   "ALL{dIN,V_vnoisy,RHS}",
   "ALL{dIN,V_vnoisy,LHS}",
   "ALL{dIN,noise,RHS}",
   "ALL{dIN,noise,LHS}",
   "ALL{dIN,noise_raw,RHS}",
   "ALL{dIN,noise_raw,LHS}",
   "ALL{V,MN,LHS}",
   ]


results.plot(trace_filters=filters_traces, legend=False, xlim=xlim )

