# Chl Comparison New

#from util import get_chl_info_dir
import shutil
import os
from os.path import join as Join
from Cheetah.Template import Template
from mhlibs.test_data.neuroml import NeuroMLDataLibrary
from neurounits.importers.neuroml.errors import NeuroUnitsImportNeuroMLNotImplementedException
from neurounits.importers.neuroml import ChannelMLReader
html_output_dir = "/home/michael/Desktop/chl_comp"
from morphforge.core import LocMgr

import lxml.etree as etree

import pylab

from morphforge.stdimports import NeuronSimulationEnvironment,MorphologyTree, unit
from morphforge.stdimports import PassiveProperty, ApplyPassiveEverywhereUniform, StdRec
from morphforge.stdimports import  ApplyMechanismEverywhereUniform, pq

import random as R
from morphforge.simulation.core.segmentation.cellsegmenter import CellSegmenter_SingleSegment
import numpy as np
import traceback
import StringIO
        
        





def main():

    ## Clear out the old directory:
    #if os.path.exists(html_output_dir):
    ##    shutil.rmtree(html_output_dir)
    #LocMgr.EnsureMakeDirs(html_output_dir)

    root_html = Join(html_output_dir,"index.html")


    for xmlfile in NeuroMLDataLibrary.getChannelMLV1FilesWithSingleChannel():

        try:
            eqnset, chl_info, default_filename = ChannelMLReader.BuildEqnset(xmlfile)
        
        except NeuroUnitsImportNeuroMLNotImplementedException, e:
            pass
        
            
        



main()
