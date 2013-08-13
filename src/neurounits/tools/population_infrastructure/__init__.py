




class Population(object):
    def __init__(self, name, component, size):
        self.name = name
        self.component = component
        self.size = size
        
        
        
class Projection(object):
    def __init__(self, name, src_population, dst_population):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population



class ElectricalSynapseProjection(Projection):
    def __init__(self, connection_probability, strength_ohm, injected_port_name, **kwargs):
        super(ElectricalSynapseProjection, self).__init__(**kwargs)
        self.connection_probability = connection_probability
        self.strength_ohm = strength_ohm
        self.injected_port_name = injected_port_name


        

class ChemicalSynapseProjection(Projection):
    pass




class EventPortConnector(object):
    def __init__(self, src_population, dst_population, src_port_name, dst_port_name, connection_probability, name):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population
        self.src_port = src_population.component.output_event_port_lut.get_single_obj_by(symbol=src_port_name)
        self.dst_port = src_population.component.input_event_port_lut.get_single_obj_by(symbol=dst_port_name)
        self.connection_probability = connection_probability





class Network(object):
    def __init__(self, ):
        self.populations = []
        self.event_port_connectors = []
        self.electrical_synapse_projections = []
        
        
    def add(self, obj):
        if isinstance( obj, Population):
            self.populations.append(obj)
        
        elif isinstance( obj, ElectricalSynapseProjection):
            self.electrical_synapse_projections.append(obj)
        
        elif isinstance( obj, EventPortConnector):
            self.event_port_connectors.append(obj)
            
        else:
            assert False