




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

        self.additional_events = []


    def add(self, obj):
        if isinstance( obj, Population):
            self.populations.append(obj)

        elif isinstance( obj, ElectricalSynapseProjection):
            self.electrical_synapse_projections.append(obj)

        elif isinstance( obj, EventPortConnector):
            self.event_port_connectors.append(obj)

        else:
            assert False


    def provide_events(self, population, event_port, evt_details ):
        event_port = population.component.input_event_port_lut.get_single_obj_by(symbol=event_port)

        self.additional_events.append( 
            (population, event_port, evt_details )
                )




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


from collections import defaultdict

class ExplicitIndices(PopulationConnector):
    def __init__(self, indices):
        self.indices = indices

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor):

        src_tgt_map = defaultdict( set)
        for i,j in self.indices:
            src_tgt_map[i].add(j);
        

        
        from mako.template import Template
        tmpl = Template('''

        ##//struct TargetList
        ##//{
        ##//    IntType num; ## = { ${tgt_str} };
        ##//    IntType tgts[]; ## = { ${tgt_str} };
        ##//};


        %for src, tgts in src_tgt_map.items():
            <%tgt_str = ','.join( [str(t) for t in tgts ] ) %>
            IntType tgts_from_${src}[] = { ${tgt_str} };
            IntType tgts_from_${src}_len = ${len(tgts)} ;

            // # TODO: refactor this out properly:
            projections[${src}].assign(tgts_from_${src}, tgts_from_${src} + tgts_from_${src}_len);
        %endfor

        ##%for i,j in indices:
        ##    ${add_connection_functor(i,j)}; 
        ##%endfor
        ''')
        return tmpl.render(
                indices=self.indices,
                add_connection_functor = add_connection_functor,
                src_tgt_map=src_tgt_map
                )
