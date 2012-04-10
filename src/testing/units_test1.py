#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
from neurounits import NeuroUnitParser, ParseTypes
import re

from neurounits.writers import DotVisitor, StringWriterVisitor, LatexWriterVisitor
from neurounits.writers import SimulateEquations
#from neurounits.visitors.writer_ast_to_nmodl import WriterASTToNMODL

from neurounits.tools import WriteToPDF, WriteToNMODL
from neurounits.units_misc import EnsureExisits
import shutil
import os

#from neurounits.visitors.common import DotVisitor, StringWriterVisitor, LatexWriterVisitor


# Clear out the output directory
outputdir = '/home/michael/hw/morphforge/src/mhlibs/NeuroUnits/src/_output/'
if os.path.exists(outputdir):
    for dirpath, dirname,files in os.walk(outputdir):
        for f in files:
            os.unlink(dirpath+'/'+f)
    #shutil.rmtree(outputdir)



def iterate_valid_lines(filename):
    with open(filename) as f:
        for line in f.readlines():
            line = re.sub('#.*','',line.strip())
            if line:
                yield line


def iterate_valid_blocks(filename):
    with open(filename) as f:
        for block in f.read().split("#--"):
            block = "\n".join( [l for l in block.split("\n") if l.strip() and  l.strip()[0] != '#'])
            yield block

            #line = re.sub('#.*','',line.strip())
            #if line:
            #    yield line


def test_valid_units():
    print 'Testing Valid Units'
    for line in iterate_valid_lines("../test_data/validunits.txt"):
        print ' ', line.ljust(30), '->', 
        result = NeuroUnitParser.Unit(line)
        print result
    print

def test_valid_exprs():
    print 'Testing Valid Expressions'
    for line in iterate_valid_lines("../test_data/validexpressions.txt"):
        print ' ',line.ljust(30), '->', 
        result = NeuroUnitParser.Expr(line)
        print result

def test_valid_lhss():
    print 'Testing Valid Expressions'
    for line in iterate_valid_lines("../test_data/validassignmentlhs.txt"):
        print ' ',line.ljust(30), '->', 
        result = NeuroUnitParser.LHS(line)
        print result


def test_valid_eqnsets():
    print 'Testing Valid EqnSets'
    for line in iterate_valid_blocks("../test_data/valid_eqnsets.txt"):
        print ' ',line.ljust(30), '->', 
        result = NeuroUnitParser.EqnSet(line, )
        #StringWriterVisitor().Visit(result)
        #DotVisitor().Visit(result)
        LatexWriterVisitor().Visit(result)
        SimulateEquations(result)
        print result
        break

def test_valid_libraries():
    print 'Testing Valid Librarys'
    for line in iterate_valid_blocks("../test_data/valid_libraries.txt"):
        print ' ',line.ljust(30), '->', 
        result = NeuroUnitParser.Library(line)
        #StringWriterVisitor().Visit(result)
        #DotVisitor().Visit(result)
        #LatexWriterVisitor().Visit(result)
        SimulateEquations(result)
        print result
        break


def test_valid_files():
    print 'Testing Valid Files'
    for line in iterate_valid_blocks("../test_data/valid_files.txt"):
        print ' ',line.ljust(30), '->', 
        results = NeuroUnitParser.File(line,working_dir=outputdir)
        
        pdf_files = []
        mod_files = []

        for result in results.eqnsets:
        #StringWriterVisitor().Visit(result)
        #DotVisitor().Visit(result)
            #LatexWriterVisitor().Visit(result)
            nmodl, nmodl_info = WriteToNMODL(result)
            moddir=outputdir+"/modfiles/"
            EnsureExisits(moddir)
            f = open(moddir+result.name+".mod",'w')
            mod_files.append(result.name +".mod")
            f.write(nmodl)
            f.close()

            pdf_file= outputdir + "/summary_"+result.name+".pdf"
            pdf_files.append(pdf_file)
            WriteToPDF(result, filename=pdf_file, additional_verbatim=nmodl )
            print result.name
            
            #SimulateEquations(result)
            print result

        os.system("pdftk %s cat output %s"%( " ".join(pdf_files), outputdir + "/All.pdf")        )

        with open(outputdir+"/modfiles/tests.sh","w") as f:
            for mf in mod_files:
                f.write("modlunit %s\n"%mf)
    
    import pylab
    #pylab.show()


# Make the default parser, otherwise ply has a whinge
#from neurounits import units_expr_yacc
#units_expr_yacc.parse_expr("mV", parse_type=ParseTypes.L1_Unit) 


#test_valid_units()
#test_valid_exprs()
#test_valid_lhss()

#test_valid_eqnsets()
#test_valid_libraries()
test_valid_files()
import pylab
pylab.show()
