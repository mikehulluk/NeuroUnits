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


from neurounits.units_misc import Chainmap
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from .base import ASTObject
from neurounits.ast.astobjects import Parameter, SuppliedValue, AssignedVariable
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
from neurounits.io_types import IOType











class Block(object):

    def __init__(self, name, library_manager, builder):
        # General info, and connected objects:
        self.name = name
        self.library_manager = library_manager
        self._builder = builder

    @property
    def src_text(self):
        assert False
        return self.library_manager.src_text


    @property
    def terminal_symbols(self):
        raise NotImplementedError()
    def get_terminal_obj(self, symbol):
        raise NotImplementedError()
    def has_terminal_obj(self, symbol):
        raise NotImplementedError()


    def to_redoc(self):
        from neurounits.writers import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)



class Library(Block):
    def accept_visitor(self, v, **kwargs):
        return v.VisitLibrary(self, **kwargs)

    def __init__(self,  library_manager, builder, builddata, io_data):
        Block.__init__(self, library_manager=library_manager, builder=builder, name=builddata.eqnset_name)
        # We have to read the _eqn_assignment, although they should be
        # reduced during the conversion to symbolic constants.
        self._eqn_assignment = builddata.assignments
        self._function_defs = builddata.funcdefs
        self._symbolicconstants = builddata.symbolicconstants


    def get_terminal_obj(self, sym):
        if sym in self._symbolicconstants:
            return self._symbolicconstants[sym]
        if sym in self._function_defs:
            return self._function_defs[sym]
        assert False, "Can't find Symbol: %s in: %s" % (sym, self.name)



    @property
    def functiondefs(self):
        return self._function_defs.values()

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants.values(), key=lambda a:a.symbol )






class EqnSet(Block):

    def accept_visitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)




    def __init__(self,  library_manager, builder, builddata, io_data):
        Block.__init__(self, library_manager=library_manager, builder=builder, name=builddata.eqnset_name)

        # Metadata about the inputs and outputs:
        self.io_data = io_data
        self.initial_conditions = [p for p in io_data if p.iotype
                                   == IOType.InitialCondition]

        # Top-level objects:
        self._eqn_assignment = builddata.assignments
        self._function_defs = builddata.funcdefs
        self._eqn_time_derivatives = builddata.timederivatives
        self._symbolicconstants = builddata.symbolicconstants
        self._on_events = builddata.onevents

        # Symbols in equations, these values are
        # cached and regenerated by a call to '_cache_nodes'
        self._parameters = None
        self._supplied_values = None

        # Initialise _parameters and _supplied_values cache.
        self._cache_nodes()


    def _cache_nodes(self):
        t = EqnsetVisitorNodeCollector()
        t.visit(self)
        self._parameters = t.nodes[Parameter]
        self._supplied_values = t.nodes[SuppliedValue]









    @property
    def onevents(self):
        return self._on_events.values()

    @property
    def assignments(self):
        return self._eqn_assignment.values()

    @property
    def timederivatives(self):
        return self._eqn_time_derivatives.values()

    @property
    def assignedvalues(self):
        return sorted( self._eqn_assignment.keys(), key=lambda a:a.symbol )

    @property
    def states(self):
        return sorted( self._eqn_time_derivatives.keys(), key=lambda a:a.symbol )

    @property
    def functiondefs(self):
        return self._function_defs.values()

    @property
    def symbolicconstants(self):
        return sorted(self._symbolicconstants.values(), key=lambda a:a.symbol )

    @property
    def parameters(self):
        return self._parameters
    @property
    def suppliedvalues(self,):
        return self._supplied_values

    @property
    def terminal_symbols(self):
        ts = list(self.states) + list(self.assignedvalues) \
            + list(self.parameters) + list(self.suppliedvalues) \
            + list(self.symbolicconstants)
        for t in ts:
            assert isinstance(t, ASTObject)
        return ts


    def get_terminal_obj(self, symbol):
        m = Chainmap( self._getParametersDict(),
                      self._getSuppliedValuesDict(),
                      self._getAssignedVariablesDict(),
                      self._getStateVariablesDict(),
                      self._symbolicconstants  )
        return m[symbol]

    def has_terminal_obj(self, symbol):
        try:
            self.get_terminal_obj(symbol=symbol)
            return True
        except KeyError:
            return False
        except:
            raise

    def _getSuppliedValuesDict(self):
        return dict( [(s.symbol, s)  for s in self._supplied_values ])
    def _getParametersDict(self):
        return dict( [(s.symbol, s)  for s in self._parameters ])
    def _getAssignedVariablesDict(self):
        return  dict( [(ass.lhs.symbol, ass.lhs)  for ass in self._eqn_assignment.values() ])
    def _getStateVariablesDict(self):
        return dict([ (td.lhs.symbol, td.lhs)  for td in self._eqn_time_derivatives.values() ])






    # These should be tidied up:
    def getSymbolDependancicesDirect(self, sym, include_constants=False):

        assert sym in self.terminal_symbols

        if isinstance(sym, AssignedVariable):
            assert False
            sym = sym.assignment_rhs

        d = VisitorFindDirectSymbolDependance()

        return list(set(d.visit(sym)))

    def getSymbolDependancicesIndirect(self, sym,include_constants=False, include_ass_in_output=False):
        res_deps = []
        un_res_deps =  self.getSymbolDependancicesDirect(sym, include_constants=include_constants)

        while un_res_deps:
            p = un_res_deps.pop()

            if p is sym:
                continue
            if p in res_deps:
                continue

            p_deps = self.getSymbolDependancicesIndirect(p, include_constants=include_constants)
            un_res_deps.extend(p_deps)
            res_deps.append(p)

        if not include_ass_in_output:
            res_deps = [d for d in res_deps if not isinstance(d,AssignedVariable) ]
        return res_deps



    def getSymbolMetadata(self, sym):
        assert sym in self.terminal_symbols
        for io in self.io_data:
            if io.symbol == sym.symbol:
                return io.metadata
        return None




class NineMLComponent(EqnSet):
    pass


class NineMLModule(object):
    
    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitNineMLModule(self, **kwargs)

    def __init__(self, **kwargs):
        print 'building NineMLModule'
        print kwargs
    pass

