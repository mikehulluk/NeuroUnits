



from neurounits.neurounitparser import NeuroUnitParser
from mredoc.objects.core import Document, Table
from mredoc.writers.html import HTMLWriter
from mredoc.writers.latex import LatexWriter


from test_locations import TestLocations

check_equivalent= [
                   ("1000V",    "1kV" ),
                   ("1000mV",   "1 V" ),
                   
                   
                   ("0.1",      "1e-1"),
                   ("400",      "4e2"),
                   ("10",       "1e1"),
                   ("1",        "1e0"),
                   ("1.54",     "1.54e0"),
                   ("0.324",    "3240.e-4"),
                   
                   ("0.324m",    "324mm"),
                   ("0.324m",    "32.4cm"),
                   ("0.324m",    "324e3um"),
                   
                   ]









data = []

for (a,b) in check_equivalent:
    A = NeuroUnitParser.QuantitySimple(a) 
    B = NeuroUnitParser.QuantitySimple(b)
    
    
    
    pcA =  ((A-B)/A).dimensionless()
    pcB =  ((A-B)/B).dimensionless()  
    
    
    data.append ( [a,b, str(A), str(B), str(pcA), str(pcB)] )
    

header = "A|B|Parsed(A)|Parsed(B)|PC(A)|PC(B)".split("|")

t = Table( header=header, data=data)

doc = Document( t )

import os
opdir = os.path.join( TestLocations.getTestOutputDir(), 'quantity_exprs_valid' )

HTMLWriter.BuildHTML(doc, os.path.join(opdir, 'html') )
LatexWriter.BuildPDF(doc, os.path.join(opdir, 'all.pdf') )

