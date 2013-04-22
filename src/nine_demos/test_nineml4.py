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







from yapsy.IPlugin import IPlugin
class PluginOne(IPlugin):
    def get_name(self):
        return '4'

    def run_demo(self, ):
        test4()






def test4():



    src_files = sorted( glob.glob("/home/michael/hw_to_come//NeuroUnits/src/test_data/l4-9ml/std/*.9ml" ))



    library_manager = None
    for s in src_files:
        #print 'Loading from:', s
        text = open(s).read()
        library_manager = neurounits.NeuroUnitParser.Parse9MLFile( text, library_manager=library_manager)



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


    res = simulate_component(
                #component=general_neuron,
                component=general_neuron_with_step_inj,
                times = np.arange(0, 0.1,0.00001),
                close_reduce_ports=True,
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
