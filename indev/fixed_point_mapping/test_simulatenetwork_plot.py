
from hdfjive import HDF5SimulationResultFile, RasterGroup, RasterSubgroup

results = HDF5SimulationResultFile("neuronits.results.hdf")


def build_raster_plot_obj(name, side):
        return RasterGroup('%s\n%s' % (name, side), [
            RasterSubgroup("OUT:Spike", "ALL{spike,%s,%s}"%(name,side), {'color':'black', 'marker':'x', 's':2}),
            RasterSubgroup("IN: AMPA", "ALL{recv_ampa_spike,%s,%s}"%(name,side), {'color':'blue', 'marker':'o', 's':1}),
            RasterSubgroup("IN: NMDA", "ALL{recv_nmda_spike,%s,%s}"%(name,side), {'color':'green', 'marker':'o', 's':1}),
            RasterSubgroup("IN: Inhib", "ALL{recv_inh_spike,%s,%s} "%(name,side), {'color':'red', 'marker':'o', 's':1}),
            ] )




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


        ],

        xlim=(95e-3,200e-3) )




