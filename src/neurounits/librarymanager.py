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
from neurounits.misc import SeqUtils
from . import units_data_functions

#from neurounits.units_misc import EnsureExisits
from neurounits.ast_builder import EqnSetBuilder
from neurounits.ast_builder.eqnsetbuilder import LibraryBuilder

from itertools import chain
import glob, os

class LibraryManager(object):


    _stdlib_cache = False
    _stdlib_cache_loading = False

    # Find the location of the standard library, relative to this directory
    _stdlibdir = os.path.join( os.path.dirname(__file__), '../stdlib/' )



    def accept_visitor(self, v, **kwargs):
        return v.VisitLibraryManager(self,**kwargs)


    def __init__(self,backend, working_dir=None, options=None, name=None, src_text=None, is_stdlib_cache=False):
        #assert src_text is None
        from neurounits.neurounitparser import NeuroUnitParserOptions
        self.options = options or NeuroUnitParserOptions()

        # This is only used to make summarising easier:
        self.name = name
        self.src_text = src_text


        self.currentblock = None
        self.backend=backend

        self.libraries = []
        self.eqnsets = []

        #self.working_dir = working_dir or "/tmp/mf_neurounits/"
        #EnsureExisits(self.working_dir)





        if is_stdlib_cache:
            # Load in the standard libraries:
            from neurounits.unit_expr_parsing.units_expr_yacc import parse_expr, ParseTypes
            LibraryManager._stdlib_cache_loading=True
            for f in glob.glob(self._stdlibdir+"/*.eqn"):
                with open( f ) as l:
                    parse_expr( l.read(), parse_type=ParseTypes.L6_TextBlock, library_manager=self)

            LibraryManager._stdlib_cache_loading=False
            LibraryManager._stdlib_cache = self


        # Ensure the cache is setup:
        if not LibraryManager._stdlib_cache and not is_stdlib_cache:
            LibraryManager( backend=backend, is_stdlib_cache=True)




    def get(self,name, include_stdlibs=True):
        print 'Searching for library: ' , name
        if LibraryManager._stdlib_cache_loading:
            include_stdlibs = False

        if include_stdlibs:
            srcs = chain(self.eqnsets, self.libraries, self._stdlib_cache.libraries)
        else:
            srcs = chain(self.eqnsets, self.libraries)
        return SeqUtils.expect_single( [ l for l in srcs if l.name==name ] )


    def get_library(self,libname):
        print 'Searching for library: ' % libname
        lib = SeqUtils.expect_single( [ l for l in chain(self.libraries,self._stdlib_cache.libraries) if l.name==libname ] )
        return lib


    def get_eqnset(self,libname):
        eqnset = SeqUtils.expect_single( [ l for l in self.eqnsets if l.name==libname ] )
        return eqnset

    def get_eqnset_names(self):
        names = [ l.name for l in self.eqnsets]
        return names

    def get_library_names(self, include_stdlibs=True):
        return [ l.name for l in self.libraries]


    def start_eqnset_block(self,):
        assert self.currentblock is None
        self.currentblock = EqnSetBuilder(library_manager=self)


    def end_eqnset_block(self,):
        self.currentblock.finalise()
        self.eqnsets.append( self.currentblock._astobject )
        self.currentblock = None
        self.get_eqnset_names()



    def start_library_block(self,):
        assert self.currentblock is None
        self.currentblock = LibraryBuilder(library_manager=self)


    def end_library_block(self,):
        self.currentblock.finalise()
        print 'Name',self.currentblock._astobject.name
        assert not self.currentblock._astobject.name in self.get_library_names()
        #if self.load_into_stdlibs:
        #    self.stdlibraries.append( self.currentblock._astobject )
        #else:
        self.libraries.append( self.currentblock._astobject )
        self.currentblock = None


    def get_current_block_builder(self):
        return self.currentblock
