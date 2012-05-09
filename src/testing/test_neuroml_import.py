# Chl Comparison New

#from util import get_chl_info_dir
import shutil
import os
from os.path import join as Join
from Cheetah.Template import Template
from mhlibs.test_data.neuroml import NeuroMLDataLibrary
from neurounits.importers.neuroml.errors import NeuroUnitsImportNeuroMLNotImplementedException
from neurounits.importers.neuroml import ChannelMLReader
#from mredoc import Document, PageBreak

        
from neurounits.writers.writer_ast_to_mredoc import MRedocWriterVisitor
from mredoc.writers import LatexWriter
from mredoc.objects import TableOfContents
from mredoc.util.removeemptysections import EmptySectionRemover, NormaliseHierachyScope
from neurounits.tools import nmodl
from mredoc.writers.html import HTMLWriter
from mredoc.objects.core import Document
#from testing.test_locations import TestLocations

from test_locations import TestLocations



def main():

    redocs = []
    
    for i,xmlfile in enumerate(NeuroMLDataLibrary.getChannelMLV1FilesWithSingleChannel()):

        try:
            print "XMLFILE:", xmlfile
            eqnset, chl_info, default_filename = ChannelMLReader.BuildEqnset(xmlfile)
            
            # Build the pdf for the channel:
            redoc = MRedocWriterVisitor.build(eqnset)
            redocs.extend([redoc])
            
            #Build the NModl for the channel:
            txt, buildparameters = nmodl.WriteToNMODL(eqnset)
            
            
            
        except NeuroUnitsImportNeuroMLNotImplementedException, e:
            pass
        
        #break
    
        if i > 2:
            break
    
    
    doc =  Document( TableOfContents(), *redocs)
    EmptySectionRemover().Visit(doc)       
    NormaliseHierachyScope().Visit(doc)
    
    
    opdir = os.path.join( TestLocations.getTestOutputDir(), 'neuroml' )
    
    HTMLWriter.BuildHTML(doc, os.path.join(opdir, 'html') )
    LatexWriter.BuildPDF(doc, os.path.join(opdir, 'all.pdf') )



main()
