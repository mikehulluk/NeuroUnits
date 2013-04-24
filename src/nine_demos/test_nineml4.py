#!/usr/bin/python
# -*- coding: utf-8 -*-

import neurounits
import sys
import numpy as np
import itertools

import pylab
from neurounits.nineml import build_compound_component, auto_plot
from neurounits.nineml import simulate_component
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
sys.stdout = Proxy(sys.stdout)
















from yapsy.IPlugin import IPlugin
class PluginOne(IPlugin):
    def get_name(self):
        return '4'

    def run_demo(self, ):
        test4()






def test4():



    src_files = sorted( glob.glob("/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/std/*.9ml" ))


    library_manager = neurounits.NeuroUnitParser.Parse9MLFiles( src_files)

    for obj in library_manager.objects:
        print "Summarising", obj
        obj.to_redoc()

    


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


    auto_plot(res)


def main():
    warnings.simplefilter('error', UserWarning)
    warnings.simplefilter('error', Warning)

    level='WARNING'
    from logbook import FileHandler, StreamHandler

    log_handler1 = FileHandler('application.log')
    log_handler1.push_application()

    test4()
    pylab.show()


if __name__=='__main__':
    main()
