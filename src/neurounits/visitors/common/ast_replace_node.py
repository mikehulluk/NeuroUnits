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

from neurounits.visitors.bases.base_visitor import ASTVisitorBase

import itertools
from neurounits.ast.astobjects import ASTObject
from neurounits.ast.eqnset import Block


class ReplaceNode(ASTVisitorBase):

    def __init__(self, srcObj, dstObj):
        self.srcObj = srcObj
        self.dstObj = dstObj

    def replace_or_visit(self, o):
        assert isinstance(o, (ASTObject,Block)), 'Not replacing with an ASTObject!: [%s] %s' % (o, type(o) )
        assert isinstance(self.srcObj, (ASTObject, Block)), 'Not replacing with an existing ASTObject!: [%s] %s' % (self.srcObj, type(self.srcObj) )

        if o == self.srcObj:
            return self.dstObj
        else:
            if 'symbol' in o.__dict__ and hasattr(self.srcObj,'symbol'):
                assert not o.symbol == self.srcObj.symbol

            return self.visit(o)

    def visit(self, o, **kwargs):
        return o.accept_visitor(self, **kwargs)




    def VisitEqnSet(self, o, **kwargs):
        assert False
        subnodes = itertools.chain(o.assignments, o.timederivatives,
                                   o.functiondefs, o.symbolicconstants,
                                   o.onevents)
        for f in subnodes:
            self.visit(f, **kwargs)

        return o


    def _replace_name_to_obj_map(self, old_dict):
        new_objs =  [self.replace_or_visit(v) for v in old_dict.values() ]
        print new_objs
        new_dict = dict( [(o.name, o) for o in new_objs] )
        assert set(old_dict.keys()) == set(new_dict.keys() )
        return new_dict

    def VisitLibrary(self, o, **kwargs):
        _function_defs_new = {}
        for (k,v) in o._function_defs.items():
            k = k #self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _function_defs_new[k] =v
        o._function_defs = _function_defs_new


        _symbolicconstants_new = {}
        for (k,v) in o._symbolicconstants.items():
            k = k #self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _symbolicconstants_new[k] =v
        o._symbolicconstants = _symbolicconstants_new

        o._cache_nodes()

        return o


    def VisitNineMLComponent(self, o, **kwargs):
        o._transitions_triggers = [self.replace_or_visit(so) for so in o._transitions_triggers]
        o._transitions_events = [self.replace_or_visit(so) for so in o._transitions_events]
        o.rt_graphs = self._replace_name_to_obj_map(o.rt_graphs) 


        #print 'Before'
        #print o._eqn_assignment
        #print o._function_defs
        #print o._eqn_time_derivatives
        #print o._symbolicconstants



        _eqn_assignment_new = {}
        for (k,v) in o._eqn_assignment.items():
            k = self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _eqn_assignment_new[k] =v
        o._eqn_assignment = _eqn_assignment_new 

        _eqn_time_derivatives_new = {}
        for (k,v) in o._eqn_time_derivatives.items():
            k = self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _eqn_time_derivatives_new[k] =v
        o._eqn_time_derivatives = _eqn_time_derivatives_new


        #o._function_defs  = [ self.replace_or_visit(so) for so in o._function_defs  ]
        _function_defs_new = {}
        for (k,v) in o._function_defs.items():
            k = k #self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _function_defs_new[k] =v
        o._function_defs = _function_defs_new


        _symbolicconstants_new = {}
        for (k,v) in o._symbolicconstants.items():
            k = k #self.replace_or_visit(k)
            v = self.replace_or_visit(v)
            _symbolicconstants_new[k] =v
        o._symbolicconstants = _symbolicconstants_new


        #print 'Afeter'
        #print o._eqn_assignment
        #print o._function_defs
        #print o._eqn_time_derivatives
        #print o._symbolicconstants

        #o._eqn_assignment = [self.replace_or_visit(so) for so in o._eqn_assignment]
        #o._eqn_assignment = self._replace_name_to_obj_map(o._eqn_assignment) #[self.replace_or_visit(so) for so in o._eqn_assignment]
        #o._function_defs  = [ self.replace_or_visit(so) for so in o._function_defs  ]
        #o._function_defs  = self._replace_name_to_obj_map(o._function_defs)
        #o._eqn_time_derivatives  = [self.replace_or_visit(so) for so in o._eqn_time_derivatives ]
        #o._symbolicconstants  = [self.replace_or_visit(so) for so in o._symbolicconstants ]


        #o._on_events  = self._replace_name_to_obj_map(o._on_events) #[self.replace_or_visit(so) for so in o._on_events ]

        o._cache_nodes()


        return o

    def VisitRTGraph(self, o, **kwargs):
        print o.regimes
        o.regimes = self._replace_name_to_obj_map(o.regimes)
        return o


    def VisitRegime(self, o, **kwargs):
        # This is not a parent, so lets prevenmt recursion:
        if o.parent_rt_graph == self.srcObj:
            o.parent_rt_graph = self.dstObj
        return o



    def VisitOnEvent(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p))
                            for (pName, p) in o.parameters.iteritems()])
        o.actions = [self.replace_or_visit(a, **kwargs) for a in
                     o.actions]
        return o

    def VisitOnEventStateAssignment(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitSymbolicConstant(self, o, **kwargs):
        return o

    def VisitIfThenElse(self, o, **kwargs):
        o.predicate = self.replace_or_visit(o.predicate, **kwargs)
        o.if_true_ast = self.replace_or_visit(o.if_true_ast, **kwargs)
        o.if_false_ast = self.replace_or_visit(o.if_false_ast, **kwargs)
        return o

    def VisitInEquality(self, o, **kwargs):
        o.less_than = self.replace_or_visit(o.less_than)
        o.greater_than = self.replace_or_visit(o.greater_than)
        return o

    def VisitBoolAnd(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs, **kwargs)
        o.rhs = self.replace_or_visit(o.rhs, **kwargs)
        return o

    def VisitBoolOr(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs, **kwargs)
        o.rhs = self.replace_or_visit(o.rhs, **kwargs)
        return o

    def VisitBoolNot(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs, **kwargs)
        return o

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p))
                            for (pName, p) in o.parameters.iteritems()])
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitBuiltInFunction(self, o, **kwargs):
        return o

    def VisitFunctionDefParameter(self, o, **kwargs):
        return o

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return o

    def VisitParameter(self, o, **kwargs):
        return o

    def VisitConstant(self, o, **kwargs):
        return o

    def VisitAssignedVariable(self, o, **kwargs):
        return o

    def VisitSuppliedValue(self, o, **kwargs):
        return o

    def VisitAnalogReducePort(self, o, **kwargs):
        o.rhses = [self.visit(rhs) for rhs in o.rhses]
        return o

    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs_map = self.replace_or_visit(o.rhs_map)
        return o

    def VisitRegimeDispatchMap(self, o, **kwargs):
        o.rhs_map = dict([(reg, self.replace_or_visit(rhs)) for (reg,rhs) in o.rhs_map.items()])
        return o

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs_map = self.replace_or_visit(o.rhs_map)
        return o

    def VisitAddOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitSubOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitMulOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitDivOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitExpOp(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        return o

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p))
                            for (pName, p) in o.parameters.iteritems()])
        assert not self.srcObj in o.parameters.values()
        o.function_def = self.replace_or_visit(o.function_def)

        return o

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        o.rhs_ast = self.replace_or_visit(o.rhs_ast)
        return o

    def VisitOnTransitionTrigger(self, o, **kwargs):
        o.trigger = self.replace_or_visit(o.trigger)
        o.actions = [self.replace_or_visit(a) for a in o.actions]
        return o
    def VisitOnTransitionEvent(self, o, **kwargs):
        o.parameters= dict([(name, self.replace_or_visit(p)) for (name,p) in o.parameters.items()])
        o.actions = [self.replace_or_visit(a) for a in o.actions]
        return o

    def VisitOnEventDefParameter(self, o, **kwargs):
        return o
    def VisitEmitEvent(self, o, **kwargs):
        o.parameter_map= dict([(name, self.replace_or_visit(p)) for (name,p) in o.parameter_map.items()])
        return o


