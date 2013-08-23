




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




#class ChemicalSynapseProjection(Projection):
#    pass




class EventPortConnector(object):
    def __init__(self, src_population, dst_population, src_port_name, dst_port_name, name, connector):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population
        self.src_port = src_population.component.output_event_port_lut.get_single_obj_by(symbol=src_port_name)
        self.dst_port = src_population.component.input_event_port_lut.get_single_obj_by(symbol=dst_port_name)
        self.connector = connector





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





class PopulationConnector(object):
    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):
        raise NotImplementedError()

class AllToAllConnector(PopulationConnector):
    def __init__(self, connection_probability):
        self.connection_probability = connection_probability

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):

        from mako.template import Template
        tmpl = Template("""
        for(IntType i=IntType(0);i< IntType(${src_pop_size_expr});i++)
        {
            for(IntType j=IntType(0);j<IntType(${dst_pop_size_expr});j++)
            {
                if(i==j) continue;
                if(rnd::rand_in_range(0,1) < ${connection_probability})
                {
                    ${add_connection_functor("i","j")}; 
                }
            }
        }

        """)

        return tmpl.render( 
                src_pop_size_expr = src_pop_size_expr,
                dst_pop_size_expr = dst_pop_size_expr,
                add_connection_functor = add_connection_functor,
                connection_probability = self.connection_probability, 
                )

