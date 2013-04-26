

import base
from neurounits.units_misc import LookUpDict



class PortDirection(object):
    In = 'In'
    Out = 'Out'


class InterfaceWire(base.ASTObject):
    DirRight = 'DirRight'
    DirLeft = 'DirLeft'

    DirCute = {DirRight:'==>>', DirLeft:'<<=='}

    def __init__(self, symbol, direction, optional=False):
        assert direction in [InterfaceWire.DirRight, InterfaceWire.DirLeft]
        self.symbol = symbol
        self.direction = direction
        self.optional = optional

class InterfaceWireContinuous(InterfaceWire):
    def __init__(self, symbol, direction, unit, optional=False):
        super(InterfaceWireContinuous, self).__init__( symbol=symbol, direction=direction, optional=optional)
        self.unit = unit

    def _summarise(self):
        print '  ', self.DirCute[self.direction],self.symbol.ljust(5),  'Analog', self.unit, 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitInterfaceWireContinuous(self, **kwargs)

class InterfaceWireEvent(InterfaceWire):
    def __init__(self, symbol, direction, parameters, optional=False):
        super(InterfaceWireEvent, self).__init__( symbol=symbol, direction=direction, optional=optional)
        self.parameters = parameters
    def _summarise(self):
        print '  ', self.DirCute[self.direction],self.symbol.ljust(5),  'Event', ['%s:%s'%p for p in self.parameters ], 'Optional:', self.optional

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitInterfaceWireEvent(self, **kwargs)

    def __repr__(self,):
        return '<InterfaceWireEvent: %s (Optional:%s, Direction:%s)>' %( self.symbol, self.optional, self.direction)



class Interface(base.ASTObject):

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitInterface(self, **kwargs)


    def __init__(self, symbol, connections):
        super(Interface, self).__init__()

        self.symbol = symbol
        self.connections = LookUpDict(connections, accepted_obj_types=(InterfaceWire,))

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

    def __repr__(self, ):
        return '<Interface: %s (%s)>' % (self.symbol, id(self))


    def to_redoc(self):
        from neurounits.writers import MRedocWriterVisitor
        return MRedocWriterVisitor.build(self)


class CompoundPortConnectorWireMapping(base.ASTObject):
    def __init__(self, component_port, interface_port):
        super(CompoundPortConnectorWireMapping,self).__init__()
        self.component_port = component_port
        self.interface_port = interface_port

        import neurounits.ast as ast



        assert isinstance(component_port, (ast.SuppliedValue, ast.AssignedVariable, ast.StateVariable, ast.AnalogReducePort, ast.SymbolicConstant) )
        assert isinstance(interface_port, (InterfaceWireContinuous, InterfaceWireEvent) )

    def accept_visitor(self, visitor, **kwargs):
        return visitor.VisitCompoundPortConnectorWireMapping(self, **kwargs)


    def __repr__(self,):
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
        self.wire_mappings = LookUpDict(wire_mappings, accepted_obj_types=(CompoundPortConnectorWireMapping,) )
        self.direction = direction

    def __repr__(self):
        return '<CompoundPortConnctor: %s (%s) [%s] (%s)>' % ( self.symbol,self.direction, '??', id(self))

    def get_direction(self):
        return self.direction



