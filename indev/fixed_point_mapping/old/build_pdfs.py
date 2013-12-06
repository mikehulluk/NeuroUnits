

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG]#, mreorg.FigFormat.SVG]

import os
import neurounits

import numpy as np
import random
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork
from hdfjive import HDF5SimulationResultFile
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *


import dIN_model
import mn_model
import rb_input_model
import cPickle as pickle

from mreorg import PM
import hashlib





dIN_comp = dIN_model.get_dIN(nbits=24)
MN_comp = mn_model.get_MN(nbits=24)
RB_input = rb_input_model.get_rb_input(nbits=24)
    # For debugging:
MRedocWriterVisitor().visit(dIN_comp).to_pdf("op_dIN.pdf")
MRedocWriterVisitor().visit(MN_comp).to_pdf("op_MN.pdf")















