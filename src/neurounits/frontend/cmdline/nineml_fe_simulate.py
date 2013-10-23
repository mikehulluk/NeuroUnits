
import os
import sys
import glob

#from neurounits.nineml import build_compound_component, auto_plot
#from neurounits.nineml import simulate_component

import numpy as np
import pylab


def resolve_filename_interpolation(src_name, output):
    # USE '%(9:c)' -- short component name
    # USE '%(9:C)' -- long component name
    # USE '%(dt:component)'
    pass


def cmdline_simulate(args):

    print 'Simulating'
    for arg, arg_value in vars(args).items():
        print arg, arg_value

    from neurounits import NeuroUnitParser, MQ1

    src_files =  [pkg_resources.resource_stream('neurounits',f) for f in neurounits.Locations.get_default_9ml_locations()]
    library_manager = neurounits.NeuroUnitParser.Parse9MLFiles( src_files)
    
    # Get the component:
    component = library_manager.get(args.component)

    component.summarise()


    # Get the start and end times:
    t_end = NeuroUnitParser.QuantitySimple(args.endt)
    assert t_end.is_compatible( MQ1('1s').units)
    t_end = t_end.float_in_si()
    dt = NeuroUnitParser.QuantitySimple(args.dt)
    assert dt.is_compatible( MQ1('1s').units)
    dt = dt.float_in_si()

    # OK lets simulate!
    res = component.simulate(  times = np.arange(0, t_end,dt),)

    print 'Simulating'
    for arg, arg_value in vars(args).items():
        print arg, arg_value
    
    # and plot:
    res.auto_plot()


    # Shall we pop up?
    if args.show_plot:
        pylab.show()



    print 'Simulating'
    for arg, arg_value in vars(args).items():
        print arg, arg_value

    
