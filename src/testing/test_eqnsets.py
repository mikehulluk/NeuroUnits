
import os
from test_locations import TestLocations
from neurounits.neurounitparser import NeuroUnitParser
from neurounits.writers.writer_ast_to_mredoc import MRedocWriterVisitor
from mhlibs.mredoc.writers.latex import LatexWriter
from mhlibs.mredoc.objects import Document, PageBreak



outputdir = '/home/michael/Desktop/_output/'
if os.path.exists(outputdir):
    for dirpath, dirname,files in os.walk(outputdir):
        for f in files:
            os.unlink(dirpath+'/'+f)
            
op_dir = TestLocations.getTestOutputDir()
      
      
      
print 'Testing Eqnsets'


redocs = []
      
for f in TestLocations.getEqnSetFiles():
    print f
    library_manager = NeuroUnitParser.File( open(f).read() )
    
    for eqnset in library_manager.eqnsets + library_manager.libraries:
        
            redoc = MRedocWriterVisitor.build(eqnset)
            redocs.append( redoc)
            redocs.append( PageBreak() )
            
    
    LatexWriter.BuildPDF(Document(redocs), '/tmp/output1.pdf')
        