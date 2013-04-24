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
from neurounits.units_misc import LookUpDict
import neurounits.ast as ast



class DuplicateNameError(RuntimeError):
    pass

class NoSuchObjectError(RuntimeError):
    pass

class ComponentNamespace(object):

    def is_root(self):
        return self.parent is None

    def __repr__(self):
        return '<Component namespace: %s>' % self.full_name

    def __init__(self, name, parent ):
        # name is local, not fully qualified:
        self.name = name
        self.parent = parent

        self.subnamespaces = LookUpDict(accepted_obj_types=ComponentNamespace)
        self.libraries = LookUpDict(accepted_obj_types=ast.Library)
        self.components = LookUpDict(accepted_obj_types=ast.NineMLComponent)
        self.interfaces = LookUpDict(accepted_obj_types=ast.Interface)

    def get_blocks(self,):
        return list( self.libraries) + list(self.components) + list(self.interfaces)

    @property
    def full_name(self,):
        if self.is_root():
            return ''
        elif self.parent.is_root():
            return self.name
        else:
            return self.parent.full_name + '.' + self.name

    def get_subnamespace(self, sub_namespace_name_tokens):
        if not self.subnamespaces.has_obj(name=sub_namespace_name_tokens[0]):
            sub_ns = ComponentNamespace(name=sub_namespace_name_tokens[0], parent=self)
            self.subnamespaces._add_item(sub_ns)
        ns = self.subnamespaces.get_single_obj_by(name=sub_namespace_name_tokens[0])
        if len(sub_namespace_name_tokens) == 1:
            return ns
        else:
            return ns.get_subnamespace(sub_namespace_name_tokens[1:])




        assert False

    def add(self, obj):
        obj_toks = obj.name.split('.')
        ns_toks = self.full_name.split('.')

        n_more_obj_tokens = len(obj_toks) - len(ns_toks)
        assert n_more_obj_tokens > 0 or self.is_root()
        assert len(obj_toks) >=0

        # Both '<root>' and 'std' will have a single token:

        if self.is_root():
            if len(obj_toks) == 1:
                self.add_here(obj)
            else:
                sub_ns = self.get_subnamespace(sub_namespace_name_tokens=obj_toks[:-1])
                sub_ns.add(obj)

        else:
            # Namespace A.B, object A.B.d  (insert locally)
            # Namespace A.B, object A.B.C.d (insert in subnamespace)
            if n_more_obj_tokens == 0:
                assert False
            elif n_more_obj_tokens == 1:
                self.add_here(obj)
            else:
                sub_ns = self.get_subnamespace(sub_namespace_name_tokens=obj_toks[len(ns_toks):-1])
                sub_ns.add(obj)

        return






    def add_here(self, obj):
        ns_toks = self.full_name.split('.')
        obj_toks = obj.name.split('.')
        assert len(obj_toks) == len(ns_toks) +1 or (self.is_root() and len(obj_toks) == 1)

        assert not obj.name in self.libraries.get_objects_attibutes(attr='name')
        assert not obj.name in self.components.get_objects_attibutes(attr='name')
        assert not obj.name in self.interfaces.get_objects_attibutes(attr='name')

        if isinstance(obj, ast.NineMLComponent):
            self.components._add_item(obj)
        if isinstance(obj, ast.Library):
            self.libraries._add_item(obj)
        if isinstance(obj, ast.Interface):
            self.interfaces._add_item(obj)


    def get_all(self, components=True, libraries=True, interfaces=True):

        objs =  []
        if components:
            objs.extend(self.components)
        if libraries:
            objs.extend(self.libraries)
        if interfaces:
            objs.extend(self.interfaces)

        for ns in self.subnamespaces:
            objs.extend( ns.get_all(components=components, libraries=libraries, interfaces=interfaces) )
        return objs






class LibraryManager(object):

    _stdlib_cache = None
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

        ## We are moving away from using these:
        #self.libraries = []
        #self.components = []
        #self.compound_port_defs = []


        self._parsing_namespace_stack = []

        # And into these:
        self.namespace = ComponentNamespace(name=None, parent=None)

        if is_stdlib_cache and not LibraryManager._stdlib_cache:
            # Load in the standard libraries:
            from neurounits.unit_expr_parsing.units_expr_yacc import parse_expr, ParseTypes
            LibraryManager._stdlib_cache_loading = True
            for f in glob.glob(self._stdlibdir + '/*.eqn'):
                with open(f) as l:
                    print 'Loading StdLib file:', f
                    parse_expr(l.read(), parse_type=ParseTypes.N6_9MLFile, library_manager=self)

            LibraryManager._stdlib_cache_loading = False
            # Copy the old namespace object accross
            LibraryManager._stdlib_cache = self.namespace
            self.namespace = ComponentNamespace(name=None, parent=None)


        # Ensure the cache is setup:
        if not LibraryManager._stdlib_cache and not is_stdlib_cache:
            LibraryManager(backend=backend, is_stdlib_cache=True)


    def get_root_namespace(self, ):
        return self.namespace


    # Syntactic sugar:
    @property
    def interfaces(self):
        return self.get_root_namespace().get_all(components=False, libraries=False)
    @property
    def components(self):
        return self.get_root_namespace().get_all(interfaces=False, libraries=False)
    @property
    def libraries(self):
        return self.get_root_namespace().get_all(interfaces=False, components=False)

    @property
    def objects(self):
        return self.get_root_namespace().get_all()


    def add_component(self, component):
        self.namespace.add(component)

    def add_compoundportdef(self, compoundportdef):
        self.namespace.add(compoundportdef)

    def add_library(self, library):
        self.namespace.add(library)


    def get(self, name, include_stdlibs=True):

        if LibraryManager._stdlib_cache_loading:
            include_stdlibs = False

        if include_stdlibs:
            srcs_1 = self.namespace.get_all()
            srcs_2 = LibraryManager._stdlib_cache.get_all()
            srcs =  srcs_1 + srcs_2 
        else:
            
            srcs = self.namespace.get_all()

        srcs = list(srcs)
        ls = [l for l in srcs if l.name == name]

        if len(ls) != 1:
            possibles = [ l.name for l in srcs if l.name.endswith(name) ]
            raise NoSuchObjectError('Cant find: %s in [%s]\nDid you mean: %s' % (name, ','.join([l.name for l in srcs] ), str(possibles) ) )


        # Testing: make sure all nodes accounted for:
        from neurounits.visitors.common.ast_node_connections import ASTAllConnections
        from neurounits.visitors.common.ast_node_connections import ASTAllConnectionsCheck
        ASTAllConnectionsCheck().visit(ls[0])
        return ls[0]

    def get_library(self, libname):

        

        lib = SeqUtils.expect_single([l for l in chain(self.libraries, self._stdlib_cache.libraries) if l.name == libname])
        return lib

    def get_library_names(self, include_stdlibs=True):
        return [l.name for l in self.libraries]

    def open_block(self, block):
        self.block_stack.append(block)

    def pop_block(self):
        return self.block_stack.pop()

    def start_library_block(self, name):
        self.open_block(LibraryBuilder(library_manager=self, name=name))

    def end_library_block(self):
        lib = self.pop_block()
        lib.finalise()

        self.add_library(lib._astobject)


    def get_current_block_builder(self):
        return self.currentblock

    def start_namespace_block(self, name):
        self._parsing_namespace_stack.append(name)

    def end_namespace_block(self):
        self._parsing_namespace_stack.pop()

    def start_component_block(self, name):
        self.open_block(NineMLComponentBuilder(library_manager=self, name=name))

    def end_component_block(self):
        component = self.pop_block()
        component.finalise()
        self.add_component( component._astobject)


    def summary(self, details=True):
        name = self.name if self.name else ''
        simple = '<LibraryManager: %s Components: %d Libraries:%d>' % (name, len(self.components), len(self.libraries))

        return simple


