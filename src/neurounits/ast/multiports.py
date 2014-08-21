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

import base
from neurounits.units_misc import LookUpDict


class PortDirection(object):

    In = 'In'
    Out = 'Out'


class MultiportInterfaceDefWire(base.ASTObject):

    DirRight = 'DirRight'
    DirLeft = 'DirLeft'

    DirCute = {DirRight: '==>>', DirLeft: '<<=='}

    def __init__(self, symbol, direction, optional=False):
        assert direction in [MultiportInterfaceDefWire.DirRight,
                             MultiportInterfaceDefWire.DirLeft]
        self.symbol = symbol
        self.direction = direction
        self.optional = optional


class MultiportInterfaceDefWireContinuous(MultiportInterfaceDefWire):
    def __init__(self, symbol, direction, unit, optional=False):
        super(MultiportInterfaceDefWireContinuous, self).__init__(symbol=symbol, direction=direction, optional=optional)
        self.unit = unit

    def _summarise(self):
        print '  ', self.DirCute[self.direction], self.symbol.ljust(5),  'Analog', self.unit, 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitMultiportInterfaceDefWireContinuous(self, **kwargs)

class MultiportInterfaceDefWireEvent(MultiportInterfaceDefWire):
    def __init__(self, symbol, direction, parameters, optional=False):
        super(MultiportInterfaceDefWireEvent, self).__init__(symbol=symbol, direction=direction, optional=optional)
        self.parameters = parameters

    def _summarise(self):
        print '  ', self.DirCute[self.direction], self.symbol.ljust(5),  'Event', ['%s:%s'%p for p in self.parameters ], 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitMultiportInterfaceDefWireEvent(self, **kwargs)

    def __repr__(self):
        return '<MultiportInterfaceDefWireEvent: %s (Optional:%s, Direction:%s)>' %( self.symbol, self.optional, self.direction)



class MultiportInterfaceDef(base.ASTObject):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitMultiportInterfaceDef(self, **kwargs)

    def __init__(self, symbol, connections):
        super(MultiportInterfaceDef, self).__init__()

        self.symbol = symbol
        self.connections = LookUpDict(connections, accepted_obj_types=(MultiportInterfaceDefWire,))

    @property
    def name(self):
        return self.symbol

    def summarise(self):
        print
        print 'Compound Port: %s' % self.symbol
        for conn in self.connections:
            conn._summarise()
        print

    def get_wire(self, wire_name):
        return self.connections.get_single_obj_by(symbol=wire_name)

    def __repr__(self):
        return '<MultiportInterfaceDef: %s (%s)>' % (self.symbol, id(self))


    def to_redoc(self):
        from neurounits.visualisation.mredoc import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)


class CompoundPortConnectorWireMapping(base.ASTObject):

    def __init__(self, component_port, interface_port):
        super(CompoundPortConnectorWireMapping, self).__init__()
        self.component_port = component_port
        self.interface_port = interface_port

        import neurounits.ast as ast



        assert isinstance(component_port, (ast.SuppliedValue, ast.AssignedVariable, ast.StateVariable, ast.AnalogReducePort, ast.SymbolicConstant))
        assert isinstance(interface_port, (MultiportInterfaceDefWireContinuous, MultiportInterfaceDefWireEvent))

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortConnectorWireMapping(self, **kwargs)

    def __repr__(self):
        try:
            # This might fail when we close reduce ports with AddOps
            return "<CompoundPortConnectorWireMapping: Component: %s to Compound: %s>" % (self.component_port.symbol, self.interface_port.symbol)
        except AttributeError:
            return "<CompoundPortConnectorWireMapping: Component: %s to Compound: %s>" % (self.component_port, self.interface_port)



class CompoundPortConnector(base.ASTObject):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortConnector(self, **kwargs)

    def __init__(self, symbol, interface_def, wire_mappings, direction):
        super(CompoundPortConnector, self).__init__()

        self.symbol = symbol
        self.interface_def =  interface_def
        self.wire_mappings = LookUpDict(wire_mappings, accepted_obj_types=(CompoundPortConnectorWireMapping,))
        self.direction = direction

    def __repr__(self):
        return '<CompoundPortConnctor: %s (%s) [%s] (%s)>' % (self.symbol, self.direction, '??', id(self))

    def get_direction(self):
        return self.direction



