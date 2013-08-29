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

from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector
from neurounits.units_misc import LookUpDict

class ReplaceNode(ASTVisitorBase):

    @classmethod
    def replace_and_check(cls, srcObj, dstObj, root):
        root = ReplaceNode(srcObj, dstObj).visit(root)




        if srcObj in EqnsetVisitorNodeCollector(root).all():

            from .ast_node_connections import ASTAllConnections
            print 'A node has not been completely removed: %s' % srcObj
            print 'The following are still connected:'
            for node in EqnsetVisitorNodeCollector(root).all():
                conns = ASTAllConnections().visit(node)
                if srcObj in conns:
                    print '    node:', node

            print 'OK'



        # Lets make sure its completely gone:
        assert not srcObj in EqnsetVisitorNodeCollector(root).all()





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
                assert not o.symbol == self.srcObj.symbol, 'Symbol: %s' % o.symbol

            return self.visit(o)


    def replace(self, o, ):
        if o == self.srcObj:
            return self.dstObj
        return o


    def visit(self, o, **kwargs):
        return o.accept_visitor(self, **kwargs)








    def _replace_within_new_lut(self, lut):
        from neurounits.units_misc import LookUpDict

        new_lut = LookUpDict()
        new_lut.unique_attrs =  lut.unique_attrs
        new_lut.accepted_obj_types =  lut.accepted_obj_types
        for o in lut:
            new_lut._add_item( self.replace_or_visit(o)  )
        return new_lut


    def VisitEventPortConnection(self, o, **kwargs):
        o.dst_port = self.replace_or_visit(o.dst_port)
        o.src_port = self.replace_or_visit(o.src_port)

        return o




    def VisitCompoundPortConnectorWireMapping(self, o, **kwargs):
        o.interface_port = self.replace_or_visit(o.interface_port)
        o.component_port = self.replace_or_visit(o.component_port)
        return o


    def VisitInterfaceWireContinuous(self, o, **kwargs):
        return o
    def VisitInterfaceWireEvent(self, o, **kwargs):
        return o

    def VisitInterface(self, o, **kwarg):
        o.connections = self._replace_within_new_lut(o.connections)
        return o



    def VisitCompoundPortConnector(self, o, **kwargs):
        o.wire_mappings = self._replace_within_new_lut(o.wire_mappings)
        o.interface_def = self.replace_or_visit(o.interface_def)
        return o


    def VisitLibrary(self, o, **kwargs):
        o._eqn_assignment = self._replace_within_new_lut(o._eqn_assignment)
        o._function_defs = self._replace_within_new_lut(o._function_defs)
        o._symbolicconstants = self._replace_within_new_lut(o._symbolicconstants)
        return o


    def VisitNineMLComponent(self, o, **kwargs):
        o._transitions_events = self._replace_within_new_lut(o._transitions_events)
        o._transitions_triggers = self._replace_within_new_lut(o._transitions_triggers)
        o._rt_graphs = self._replace_within_new_lut(o.rt_graphs)
        o._eqn_assignment = self._replace_within_new_lut(o._eqn_assignment)
        o._eqn_time_derivatives = self._replace_within_new_lut(o._eqn_time_derivatives)
        o._function_defs = self._replace_within_new_lut(o._function_defs)
        o._symbolicconstants = self._replace_within_new_lut(o._symbolicconstants)
        o._interface_connectors = self._replace_within_new_lut(o._interface_connectors)

        o._event_port_connections = self._replace_within_new_lut(o._event_port_connections)

        return o

    def VisitRTGraph(self, o, **kwargs):
        if o.default_regime:
            assert o.default_regime in o.regimes
        o.regimes = self._replace_within_new_lut(o.regimes)
        if o.default_regime:
            o.default_regime = self.replace_or_visit(o.default_regime)
            assert o.default_regime in o.regimes
        return o


    def VisitRegime(self, o, **kwargs):
        # This is not a parent, so lets prevenmt recursion:
       o.parent_rt_graph  = self.replace(o.parent_rt_graph) 
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
        o.lesser_than = self.replace_or_visit(o.lesser_than)
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
    def VisitFunctionDefUser(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p))
                            for (pName, p) in o.parameters.iteritems()])
        o.rhs = self.replace_or_visit(o.rhs)
        return o

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        return o

    def VisitFunctionDefParameter(self, o, **kwargs):
        return o



    # Random Variables:
    def VisitRandomVariable(self, o, **kwargs):
        o.parameters = LookUpDict([ self.replace_or_visit(p) for p in o.parameters])
        return o

    def VisitRandomVariableParameter(self, p, **kwargs):
        p.rhs_ast = self.replace_or_visit(p.rhs_ast)
        return p

        







    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        if o.initial_value:
            o.initial_value = self.replace_or_visit(o.initial_value)
        return o

    def VisitParameter(self, o, **kwargs):
        return o

    def VisitConstant(self, o, **kwargs):
        return o
    def VisitConstantZero(self, o, **kwargs):
        return o

    def VisitAssignedVariable(self, o, **kwargs):
        return o

    def VisitSuppliedValue(self, o, **kwargs):
        return o

    def VisitAnalogReducePort(self, o, **kwargs):
        o.rhses = [self.replace_or_visit(rhs) for rhs in o.rhses]
        return o

    # AST Objects:
    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs_map = self.replace_or_visit(o.rhs_map)
        return o

    def VisitRegimeDispatchMap(self, o, **kwargs):
        o.rhs_map = dict([(self.replace_or_visit(reg), self.replace_or_visit(rhs)) for (reg,rhs) in o.rhs_map.items()])
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

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p)) for (pName, p) in o.parameters.iteritems()])
        o.function_def = self.replace_or_visit(o.function_def)
        return o
    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        o.parameters = dict([(pName, self.replace_or_visit(p)) for (pName, p) in o.parameters.iteritems()])
        o.function_def = self.replace_or_visit(o.function_def)
        return o


    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        o.rhs_ast = self.replace_or_visit(o.rhs_ast)
        return o

    def VisitOnTransitionTrigger(self, o, **kwargs):
        o.trigger = self.replace_or_visit(o.trigger)
        o.actions = [self.replace_or_visit(a) for a in o.actions]
        o.src_regime = self.replace_or_visit(o.src_regime)
        o.target_regime = self.replace_or_visit(o.target_regime)
        return o
    def VisitOnTransitionEvent(self, o, **kwargs):
        o.port = self.replace_or_visit(o.port)
        o.parameters = self._replace_within_new_lut(o.parameters)
        o.actions = [self.replace_or_visit(a) for a in o.actions]
        o.src_regime = self.replace_or_visit(o.src_regime)
        o.target_regime = self.replace_or_visit(o.target_regime)
        return o

    def VisitOnEventDefParameter(self, o, **kwargs):
        return o
    def VisitEmitEvent(self, o, **kwargs):
        o.parameters = self._replace_within_new_lut(o.parameters)
        o.port = self.replace_or_visit(o.port)
        return o


    def VisitEmitEventParameter(self, o, **kwargs):
        o.port_parameter_obj = self.replace_or_visit(o.port_parameter_obj)
        o.rhs = self.replace_or_visit(o.rhs)
        return o



    def VisitInEventPort(self, o, **kwargs):
        o.parameters = self._replace_within_new_lut(o.parameters)
        return o
    def VisitInEventPortParameter(self, o, **kwargs):
        return o
    def VisitOutEventPort(self, o, **kwargs):
        o.parameters = self._replace_within_new_lut(o.parameters)
        return o
    def VisitOutEventPortParameter(self, o, **kwargs):
        return o
