
import os
import sys
import glob

from neurounits.nineml import build_compound_component, auto_plot
from neurounits.nineml import simulate_component

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

    # Load from all the include directories, but only add files once 
    # to prevent duplicate entries in the library_manager
    src_files = []
    for incl_path in args.include:
        assert os.path.exists(incl_path)
        # Add all the files in a directory:
        if os.path.isdir(incl_path):
            new_files = sorted([ os.path.abspath(fname)  for fname in glob.glob(incl_path+'/*.9ml') ] )
            for fname in new_files:
                if not fname in src_files:
                    src_files.append(fname)
        # Add an individual file:
        elif os.path.isfile(incl_path):
            if not fname in src_files:
                src_files.append(fname)


    # Read all the input files:
    library_manager = NeuroUnitParser.Parse9MLFiles(filenames=src_files)


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
    res = simulate_component( component=component, times = np.arange(0, t_end,dt),)

    print 'Simulating'
    for arg, arg_value in vars(args).items():
        print arg, arg_value
    
    # and plot:
    auto_plot(res)


    # Shall we pop up?
    if args.show_plot:
        pylab.show()



    print 'Simulating'
    for arg, arg_value in vars(args).items():
        print arg, arg_value

    
