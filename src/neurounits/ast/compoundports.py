

import base
from neurounits.units_misc import LookUpDict



class PortDirection(object):
    In = 'In'
    Out = 'Out'


class CompoundPortDefWire(base.ASTObject):
    DirRight = 'DirRight'
    DirLeft = 'DirLeft'

    DirCute = {DirRight:'==>>', DirLeft:'<<=='}

    def __init__(self, symbol, direction, optional=False):
        assert direction in [CompoundPortDefWire.DirRight, CompoundPortDefWire.DirLeft]
        self.symbol = symbol
        self.direction = direction
        self.optional = optional

class CompoundPortDefWireContinuous(CompoundPortDefWire):
    def __init__(self, symbol, direction, unit, optional=False):
        super(CompoundPortDefWireContinuous, self).__init__( symbol=symbol, direction=direction, optional=optional)
        self.unit = unit

    def _summarise(self):
        print '  ', self.DirCute[self.direction],self.symbol.ljust(5),  'Analog', self.unit, 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortDefWireContinuous(self, **kwargs)

class CompoundPortDefWireEvent(CompoundPortDefWire):
    def __init__(self, symbol, direction, parameters, optional=False):
        super(CompoundPortDefWireEvent, self).__init__( symbol=symbol, direction=direction, optional=optional)
        self.parameters = parameters
    def _summarise(self):
        print '  ', self.DirCute[self.direction],self.symbol.ljust(5),  'Event', ['%s:%s'%p for p in self.parameters ], 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortDefWireEvent(self, **kwargs)

    def __repr__(self,):
        return '<CompoundPortDefWireEvent: %s (Optional:%s, Direction:%s)>' %( self.symbol, self.optional, self.direction)



class CompoundPortDef(base.ASTObject):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortDef(self, **kwargs)


    def __init__(self, name, connections):
        super(CompoundPortDef, self).__init__()
        print 'Creating CompoundPortDef:', id(self)
        self.name = name
        self.connections = LookUpDict(connections, accepted_obj_types=(CompoundPortDefWire,))

    def summarise(self):
        print
        print 'Compound Port: %s' % self.name
        for conn in self.connections:
            conn._summarise()
        print

    def get_wire(self, wire_name):
        return self.connections.get_single_obj_by(symbol=wire_name)

    def __repr__(self, ):
        return '<CompoundPortDef: %s (%s)>' % (self.name, id(self))


class CompoundPortConnectorWireMapping(base.ASTObject):
    def __init__(self, component_port, compound_port):
        super(CompoundPortConnectorWireMapping,self).__init__()
        self.component_port = component_port
        self.compound_port = compound_port

        import neurounits.ast as ast
        print 'component_port', type(component_port)
        print 'compound_port', type(compound_port)

        assert isinstance(component_port, (ast.SuppliedValue, ast.AssignedVariable, ast.StateVariable, ast.AnalogReducePort) )
        assert isinstance(compound_port, (CompoundPortDefWireContinuous, CompoundPortDefWireEvent) )

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortConnectorWireMapping(self, **kwargs)


    def __repr__(self,):
        return "<CompoundPortConnectorWireMapping: Component: %s to Compound: %s>" % (self.component_port.symbol, self.compound_port.symbol)



class CompoundPortConnector(base.ASTObject):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortConnector(self, **kwargs)

    def __init__(self, name, compound_port_def, wire_mappings, direction):
        super(CompoundPortConnector, self).__init__()

        self.name = name
        self.compound_port_def =  compound_port_def
        self.wire_mappings = LookUpDict(wire_mappings, accepted_obj_types=(CompoundPortConnectorWireMapping,) )
        self.direction = direction

    def __repr__(self):
        return '<CompoundPortConnctor: %s (%s) [%s] (%s)>' % ( self.name,self.direction, '??', id(self))

    def get_direction(self):
        return self.direction

