#!/usr/bin/python
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
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
# -------------------------------------------------------------------------------

import os
from mhlibs.test_data.neuroml import NeuroMLDataLibrary

from neurounits.importers.neuroml.errors import NeuroUnitsImportNeuroMLNotImplementedException
from neurounits.importers.neuroml import ChannelMLReader

from mredoc.objects.core import Document, TableOfContents, SectionNewPage, Section, VerbatimBlock, Paragraph

from neurounits.writers.writer_ast_to_mredoc import MRedocWriterVisitor
from neurounits.tools import nmodl

from util_test_locations import TestLocations

from os.path import join as Join


def load_neuroml():

    redocs = []

    for (i, xmlfile) in enumerate(NeuroMLDataLibrary.get_channelMLV1FilesWithSingleChannel()):

        try:
            print 'XMLFILE:', xmlfile
            (eqnset, chl_info, default_filename) = ChannelMLReader.BuildEqnset(xmlfile)

            # Build the pdf for the channel:
            eqnset_redoc = MRedocWriterVisitor.build(eqnset)

            # Build the NModl for the channel:
            (txt, buildparameters) = nmodl.WriteToNMODL(eqnset)

            section = SectionNewPage("Import from: %s"% "/".join(xmlfile.split('/')[-3:]),
                        Section("Original XML:", VerbatimBlock(open(xmlfile).read() ) ),
                        eqnset_redoc,
                        Section("Generated Modfile",VerbatimBlock(txt) ) )

            redocs.append(section)
        except NeuroUnitsImportNeuroMLNotImplementedException, e:

            pass

        if i > 1:
            break

    return redocs


# Hook into automatic documentation:
from test_base import ReportGenerator


class NeuroMLDocGen(ReportGenerator):

    def __init__(self):
        ReportGenerator.__init__(self, 'Importing from NeuroML')

    def __call__(self):
        return load_neuroml()


NeuroMLDocGen()


def main():
    redocs = load_neuroml()
    doc = Document(TableOfContents(), *redocs)

    opdir = os.path.join(TestLocations.getTestOutputDir(), 'neuroml')
    doc.to_html(Join(opdir, 'html'))
    doc.to_pdf(Join(opdir, 'all.pdf'))


main()
