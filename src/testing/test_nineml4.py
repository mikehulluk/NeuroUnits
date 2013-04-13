#!/usr/bin/python
# -*- coding: utf-8 -*-

import neurounits
import sys
import numpy as np
import itertools

import pylab
from neurounits.nineml import build_compound_component
from neurounits.nineml import simulate_component
import glob
#pylab.ion()







def test0():
    
    src_files = sorted( glob.glob("/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/std/*.9ml" ))



    library_manager = None
    for s in src_files:
        print 'Loading from:', s
        text = open(s).read()
        library_manager = neurounits.NeuroUnitParser.Parse9MLFile( text, library_manager=library_manager)



    print
    print 'Available Interfaces:'
    for comp in library_manager.compound_port_defs:
        print '  ',  repr(comp)
    print

    print 'Available Components:'
    for comp in library_manager.components:
        print '  ', repr(comp)
    print

test0()
