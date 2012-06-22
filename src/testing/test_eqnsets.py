#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are 
# met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------


import os
from util_test_locations import TestLocations
from neurounits.neurounitparser import NeuroUnitParser
from neurounits.writers.writer_ast_to_mredoc import MRedocWriterVisitor
from mredoc.writers import LatexWriter
from mredoc import Document, TableOfContents


from os.path import join as Join



def document_eqnsets(individual_reports=True):

    all_redocs = []

    for f in TestLocations.getEqnSetFiles():
        f_basename = os.path.splitext( os.path.basename(f))[0] 

        # Load the EqnSet:
        library_manager = NeuroUnitParser.File( open(f).read(), name=f_basename )

        # Create the documentation:
        local_redoc = MRedocWriterVisitor.build( library_manager) 

        # Create a local documentation file:
        if individual_reports:
            LatexWriter.BuildPDF(
                Document(TableOfContents(), local_redoc),
                Join(TestLocations.getTestOutputDir(), 'eqnsets_%s.pdf'%f_basename  ) )
        
        # Add it to single large file:
        all_redocs.append( local_redoc )

    return all_redocs







# Hook into automatic documentation:
from test_base import ReportGenerator
class EqnsetDoc(ReportGenerator):
    def __init__(self):
        ReportGenerator.__init__(self, "ExampleEqnSets")
    def __call__(self):
        return document_eqnsets(individual_reports=False)
EqnsetDoc()


# run individually:
def main():
    all_redocs = document_eqnsets(individual_reports = True)
    d = Document( TableOfContents(), all_redocs)
    op_dir = TestLocations.getTestOutputDir()
    op_loc = os.path.join( op_dir, 'eqnsets', "all.pdf" )
    LatexWriter.BuildPDF(d, op_loc)

if __name__=="__main__":
    main()
