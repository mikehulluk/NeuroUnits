
import os
from test_locations import TestLocations
from neurounits.neurounitparser import NeuroUnitParser
from neurounits.writers.writer_ast_to_mredoc import MRedocWriterVisitor
from mredoc.writers import LatexWriter
from mredoc import Document
from mredoc.util.removeemptysections import EmptySectionRemover
from mredoc import TableOfContents


import os
import glob

from os.path import join as Join


      
      
      
print 'Testing Eqnsets'



def getStdLibFiles():
    root= "/home/michael/hw_to_come//libs/NeuroUnits"
    loc = Join(root, "src/stdlib" )
    files = glob.glob( loc+"/*.eqn" )
    return files



all_redocs = []
      
for f in getStdLibFiles():

    library_manager = NeuroUnitParser.File( open(f).read() )
    
    local_redocs = []
    for eqnset in library_manager.eqnsets + library_manager.libraries:        
        redoc = MRedocWriterVisitor.build(eqnset)
        local_redocs.append( redoc)

            

    d = Document(TableOfContents(), local_redocs)
    EmptySectionRemover().Visit(d)
    
    op_dir = TestLocations.getTestOutputDir()
    op_loc = os.path.join( op_dir, 'libs', os.path.splitext( os.path.basename(f))[0] + ".pdf"  )
    LatexWriter.BuildPDF(d, op_loc)
    
    all_redocs.extend( local_redocs )

    

d = Document( TableOfContents(), all_redocs)
EmptySectionRemover().Visit(d)
op_dir = TestLocations.getTestOutputDir()
op_loc = os.path.join( op_dir, 'eqnsets', "all.pdf" )
LatexWriter.BuildPDF(d, op_loc)  
