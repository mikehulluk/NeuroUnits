




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
    pass





class Network(object):
    def __init__(self, ):
        self.populations = []
        self.chemical_synapse_projections = []
        self.electrical_synapse_projections = []
        
        
    def add(self, obj):
        if isinstance( obj, Population):
            self.populations.append(obj)
        
        else:
            assert False