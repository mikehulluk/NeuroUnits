




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
        

class ChemicalSynapseProjection(Projection):
    pass

class ElectricalSynapseProjection(Projection):
    def __init__(self, connection_probability, strength_ohm, **kwargs):
        super(ElectricalSynapseProjection, self).__init(**kwargs)
        self, connection_prop
        self.connection_probability = connection_probability
        self.strength_ohm = strength_ohm
        





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