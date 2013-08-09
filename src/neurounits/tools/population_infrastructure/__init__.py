




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






#class EventSource(object):
    
    







class Network(object):
    def __init__(self, ):
        self.populations = []
        self.chemical_synapse_projections = []
        self.electrical_synapse_projections = []
        
        
    def add(self, obj):
        if isinstance( obj, Population):
            self.populations.append(obj)
        
        elif isinstance( obj, ElectricalSynapseProjection):
            self.electrical_synapse_projections.append(obj)
            
            
        else:
            assert False