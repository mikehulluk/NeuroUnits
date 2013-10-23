#!/usr/bin/python
# -*- coding: utf-8 -*-
import mreorg
import neurounits
import sys
import numpy as np
import itertools

import pylab

import glob
import warnings



import os, sys, traceback
 
class Proxy(object):
    def __init__(self, target_object):
        self._count = {}
        self._obj = target_object
 
    def __getattr__(self, attr):
        if attr in self._count: 
            self._count[attr]+=1
        else: 
            self._count[attr]=1
        return getattr(self._obj, attr)
 
    def write(self, *args, **kwargs):
        rv = self._obj.write(*args, **kwargs)
        for filename, lineno, function, line in traceback.extract_stack():
            if 'print' in line:
                if os.environ.get('TRACE_PRINT', None) == 'traceback':
                    traceback.print_stack()
                else:
                    sys.stderr.write("%s:%d (%s): %s\n" % (filename, lineno, function, line))
                break
 
if os.environ.get('TRACE_PRINT', None):
    sys.stdout = Proxy(sys.stdout)
#sys.stdout = Proxy(sys.stdout)










from neurounitscontrib.demo import DemoPluginBase
class Demo4(DemoPluginBase):
    
    
    def get_name(self, ):
        return '4'
                
    def run(self, args):
        test4()
        





import pkg_resources


def test4():
    import neurounits

    src_files =  [pkg_resources.resource_stream('neurounits',f) for f in neurounits.Locations.get_default_9ml_locations()]
    library_manager = neurounits.NeuroUnitParser.Parse9MLFiles( src_files)

    print
    print 'Available Interfaces:'
    for comp in library_manager.interfaces:
        print '  ',  repr(comp)
    print

    print 'Available Components:'
    for comp in library_manager.components:
        print '  ', repr(comp)
    print




    #general_neuron = library_manager.get('general_neuron')
    #general_neuron.summarise()

    general_neuron_with_step_inj = library_manager.get('general_neuron_with_step_inj')


    res = general_neuron_with_step_inj.simulate(
                times = np.arange(0, 0.1,0.00001),
                )


    res.auto_plot()


def main():
    warnings.simplefilter('error', UserWarning)
    warnings.simplefilter('error', Warning)

    #level='WARNING'
    #from logbook import FileHandler, StreamHandler

    #log_handler1 = FileHandler('application.log')
    #log_handler1.push_application()

    test4()
    pylab.show()


if __name__=='__main__':
    main()
