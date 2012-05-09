


import subprocess

from neurounits.neurounitparser import NeuroUnitParser
from mredoc.objects.core import Document, Table
from mredoc.writers.html import HTMLWriter
from mredoc.writers.latex import LatexWriter


from test_locations import TestLocations

#                   A           B               Test with GNU units
check_equivalent= [
                   ("1000V",    "1kV",         True  ),
                   ("1000mV",   "1 V",         True  ),
                   
                   
                   ("0.1",      "1e-1",        True  ),
                   ("400",      "4e2",         True  ),
                   ("10",       "1e1",         True  ),
                   ("1",        "1e0",         True  ),
                   ("1.54",     "1.54e0",      True  ),
                   ("0.324",    "3240.e-4",    True  ),
                   
                   ("0.324m",    "324mm",      True  ),
                   ("0.324m",    "32.4cm",     True  ),
                   ("0.324m",    "324e3um",    False  ),
                   
                   ]



def test_with_gnuunits(a,b):
    cmd = "units", "-1", "-s","--compact",a,b
    cmd_str = " ".join(cmd)
    print cmd_str

    op = subprocess.check_output( cmd )
    print op
    assert op.strip() == "1"



def test_simple_quantities():
    data = []

    for (a,b, check_with_gnu) in check_equivalent:
        A = NeuroUnitParser.QuantitySimple(a) 
        B = NeuroUnitParser.QuantitySimple(b)
        

        if check_with_gnu:
            test_with_gnuunits(a,b)
        
        
        pcA =  ((A-B)/A).dimensionless()
        pcB =  ((A-B)/B).dimensionless()  
        assert pcA==0 
        assert pcB==0 
        data.append ( [a,b, str(A), str(B), str(pcA), str(pcB)] )
        
    header = "A|B|Parsed(A)|Parsed(B)|PC(A)|PC(B)".split("|")
    return  Table( header=header, data=data)











valid_unit_exprs = [
                    ( '1.0',       "1.0",     True ),

                    ]



def test_unit_expr():
    data = []

    for (a,b, check_with_gnu) in valid_unit_exprs:
        A = NeuroUnitParser.QuantityExpr(a) 
        B = NeuroUnitParser.QuantityExpr(b)
        

        if check_with_gnu:
            test_with_gnuunits(a,b)
        
        
        pcA =  ((A-B)/A).dimensionless()
        pcB =  ((A-B)/B).dimensionless()  
        assert pcA==0 
        assert pcB==0 
        data.append ( [a,b, str(A), str(B), str(pcA), str(pcB)] )
        
    header = "A|B|Parsed(A)|Parsed(B)|PC(A)|PC(B)".split("|")
    return  Table( header=header, data=data)
























#t = test_simple_quantities()
t = test_unit_expr()

doc = Document( t )

import os
opdir = os.path.join( TestLocations.getTestOutputDir(), 'quantity_exprs_valid' )

HTMLWriter.BuildHTML(doc, os.path.join(opdir, 'html') )
LatexWriter.BuildPDF(doc, os.path.join(opdir, 'all.pdf') )

