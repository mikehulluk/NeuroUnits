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

from neurounits.misc import SeqUtils

from neurounits.ast_builder import EqnSetBuilder
from neurounits.ast_builder.eqnsetbuilder import LibraryBuilder
from neurounits.ast_builder.eqnsetbuilder import NineMLComponentBuilder

from itertools import chain
import glob
import os



class DuplicateNameError(RuntimeError):
    pass

class NoSuchObjectError(RuntimeError):
    pass

class ComponentNamespace(object):

    def __init__(self, name):
        self.name = name


class LibraryManager(object):

    _stdlib_cache = False
    _stdlib_cache_loading = False

    # Find the location of the standard library, relative to this directory
    _stdlibdir = os.path.join(os.path.dirname(__file__), '../stdlib/')

    def accept_visitor(self, v, **kwargs):
        return v.VisitLibraryManager(self, **kwargs)

    @property
    def currentblock(self):
        if len(self.block_stack) == 0:
            return None
        else:
            return self.block_stack[-1]

    def __init__(self,backend, working_dir=None, options=None, name=None, src_text=None, is_stdlib_cache=False):
        from neurounits.neurounitparser import NeuroUnitParserOptions
        self.options = options or NeuroUnitParserOptions()

        # This is only used to make summarising easier:

        self.name = name
        self.src_text = src_text

        self.block_stack = []

        self.backend = backend

        self.libraries = []
        self.components = []

        if is_stdlib_cache:
            # Load in the standard libraries:
            from neurounits.unit_expr_parsing.units_expr_yacc import parse_expr, ParseTypes
            LibraryManager._stdlib_cache_loading = True
            for f in glob.glob(self._stdlibdir + '/*.eqn'):
                with open(f) as l:
                    print 'Loading StdLib file:', f
                    parse_expr(l.read(), parse_type=ParseTypes.N6_9MLFile, library_manager=self)
                    #parse_expr(l.read(), parse_type=ParseTypes.L6_TextBlock, library_manager=self)

            LibraryManager._stdlib_cache_loading = False
            LibraryManager._stdlib_cache = self

        # Ensure the cache is setup:
        if not LibraryManager._stdlib_cache and not is_stdlib_cache:
            LibraryManager(backend=backend, is_stdlib_cache=True)



    def add_component(self, component):
        try:
            self.get(component.name)
            raise DuplicateNameError('Name already exists: %s' % component.name)
        except NoSuchObjectError:
            pass
        
        self.components.append(component)



    def get(self, name, include_stdlibs=True):

        if LibraryManager._stdlib_cache_loading:
            include_stdlibs = False

        if include_stdlibs:
            srcs = chain(self.libraries, self.components, self._stdlib_cache.libraries)
        else:
            srcs = chain(self.libraries, self.components)

        srcs = list(srcs)
        print srcs
        print [s.name for s in srcs]
        print '"%s"' % name
        ls = [l for l in srcs if l.name == name]

        if len(ls) != 1:
            print 'Did not find item in Library Manager!'
            print 'Looking for: %s' % name
            print 'Found:', [l.name for l in ls]
            print
            raise NoSuchObjectError()


        # Testing: make sure all nodes accounted for:
        from neurounits.visitors.common.ast_node_connections import ASTAllConnections
        from neurounits.visitors.common.ast_node_connections import ASTAllConnectionsCheck
        ASTAllConnectionsCheck().visit(ls[0])
        #assert False
        return ls[0]

    def get_library(self, libname):

        # print 'Searching for library: ' % libname

        lib = SeqUtils.expect_single([l for l in chain(self.libraries, self._stdlib_cache.libraries) if l.name == libname])
        return lib

    #def get_eqnset(self, libname):
    #    eqnset = SeqUtils.expect_single([l for l in self.eqnsets if l.name == libname])
    #    return eqnset

    #def get_eqnset_names(self):
    #    names = [l.name for l in self.eqnsets]
    #    return names

    def get_library_names(self, include_stdlibs=True):
        return [l.name for l in self.libraries]

    def open_block(self, block):
        self.block_stack.append(block)

    def pop_block(self):
        return self.block_stack.pop()

    #def start_eqnset_block(self, name):
    #    self.open_block(EqnSetBuilder(library_manager=self, name=name))

    #def end_eqnset_block(self):
    #    eqnset = self.pop_block()
    #    eqnset.finalise()
    #    self.eqnsets.append(eqnset._astobject)
    #    self.get_eqnset_names()

    def start_library_block(self, name):
        self.open_block(LibraryBuilder(library_manager=self, name=name))

    def end_library_block(self):
        lib = self.pop_block()
        lib.finalise()
        assert not lib._astobject.name in self.get_library_names()

        self.libraries.append(lib._astobject)

    def get_current_block_builder(self):
        return self.currentblock

    def start_namespace_block(self, name):
        self.open_block(ComponentNamespace(name=name))

    def end_namespace_block(self):
        self.pop_block()

    def start_component_block(self, name):
        self.open_block(NineMLComponentBuilder(library_manager=self, name=name))

    def end_component_block(self):
        component = self.pop_block()
        component.finalise()

        self.components.append(component._astobject)

    def summary(self, details=True):
        name = self.name if self.name else ''
        simple = '<LibraryManager: %s Components: %d Libraries:%d>' % (name, len(self.components), len(self.libraries))

        return simple


