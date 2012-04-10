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
from units_misc import ExpectSingle
#from units_data_functions import StdLibrary
import units_data_functions 

from neurounits.units_misc import EnsureExisits
from neurounits.ast_builder import EqnSetBuilder

from itertools import chain

class LibraryManager(object):
    
    def __init__(self,backend, working_dir=None):
        self.currentblock = None
        self.backend=backend
    
        self.libraries = []
        self.eqnsets = []

        available_libraries = None
        self.available_libraries = available_libraries or units_data_functions.StdLibrary.getDefault(backend=backend)
        self.working_dir = working_dir or "/tmp/mf_neurounits/"
        EnsureExisits(self.working_dir)
        
        
    def get(self,name):
        return ExpectSingle( [ l for l in chain(self.available_libraries,self.eqnsets) if l.name==name ] )
        
        
    def get_library(self,libname):
        lib = ExpectSingle( [ l for l in self.available_libraries if l.name==libname ] )
        return lib
    
    
    def get_eqnset(self,libname):
        eqnset = ExpectSingle( [ l for l in self.eqnsets if l.name==libname ] )
        return eqnset
    
    def get_eqnset_names(self):
        return [ l.name for l in self.eqnsets]
    
    def get_library_names(self):
        return [ l.name for l in self.libraries]

    
    def start_eqnset_block(self,):
        assert self.currentblock is None
        
        self.currentblock = EqnSetBuilder(library_manager=self)
        
    
    def end_eqnset_block(self,):
        #builder = self.currentblock
        #builder._astobject._builder = builder

        self.currentblock.finalise()
        self.eqnsets.append( self.currentblock._astobject )
        #builder.astobject = self.working_dir + builder.astobject.name
        self.currentblock = None
    
        

    def start_library_block(self,):
        assert False
        assert self.currentblock is None
        #from neurounits.ast_builder import EqnSetBuilder
        self.currentblock = EqnSetBuilder(library_manager=self)
        
    
    def end_library_block(self,):
        assert False
        self.currentblock.finalise()
        self.currentblock = None
    
        
    def get_current_block_builder(self):
        return self.currentblock 
