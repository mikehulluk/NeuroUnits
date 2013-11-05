
from neurounits import NeuroUnitParser
import numpy as np




class Population(object):
    def __init__(self, name, component, size, autotag=None):
        self.name = name
        self.component = component
        self._size = size
        self.autotag = autotag if autotag is not None else []

    def get_subpopulation(self, start_index, end_index, subname, autotag):
        return SubPopulation(population=self,
                             start_index=start_index,
                             end_index=end_index,
                             subname=subname,
                             autotag=autotag )
    @property
    def population(self):
        return self
    @property
    def indices(self):
        return (0, self._size)
    def get_size(self,):
        return self.indices[1] - self.indices[0]
    @property
    def start_index(self):
        return 0
    @property
    def end_index(self):
        return self._size
    @property
    def tags(self):
        return self.autotag + ['wholepop']

class SubPopulation(object):
    def __init__(self, population, start_index, end_index, subname, autotag):
        self._population = population
        self.start_index = start_index
        self.end_index = end_index
        self.subname = subname
        self.autotag = autotag

    @property
    def population(self):
        return self._population
    @property
    def indices(self):
        return (self.start_index, self.end_index)
    @property
    def component(self):
        return self.population.component

    def get_size(self,):
        return self.indices[1] - self.indices[0]

    @property
    def name(self):
        return "%s__%s" % (self._population.name, self.subname)


    @property
    def tags(self):
        return self.autotag + self._population.autotag + ['subpop']


    def __str__(self):
        return "<SubPopulation: %s>" % self.name



    def get_subpopulation(self, start_index, end_index, subname, autotag):
        assert 0<=start_index<=self.end_index
        assert 0<=end_index<=self.end_index
        return SubPopulation(
                start_index = self.start_index + start_index,
                end_index = self.start_index + end_index,
                subname = self.subname + "_" + subname,
                autotag = self.autotag + autotag,
                population = self._population
                )

class Projection(object):
    def __init__(self, name, src_population, dst_population):
        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population



class ElectricalSynapseProjection(Projection):
    def __init__(self,  strength_S, injected_port_name, connector, **kwargs):
        super(ElectricalSynapseProjection, self).__init__(**kwargs)
        self.connector = connector
        self.injected_port_name = injected_port_name
        
        self.strength_S = strength_S
        self.strength_S_upscale = -21
        assert strength_S / (2**self.strength_S_upscale) < 1

        from neurounits.ast_annotations import NodeFixedPointFormatAnnotator
        self.strength_S_int = NodeFixedPointFormatAnnotator.encode_value_cls(self.strength_S, self.strength_S_upscale, 24)




class FixedValue(object):
    def __init__(self, value):
        if isinstance(value, basestring):
            value = NeuroUnitParser.QuantitySimple(value)
        self.value=value




class EventPortConnector(object):
    def __init__(self, src_population, dst_population, src_port_name, dst_port_name, name, connector, delay, parameter_map):


        self.name = name
        self.src_population = src_population
        self.dst_population = dst_population
        self.src_port = src_population.component.output_event_port_lut.get_single_obj_by(symbol=src_port_name)
        self.dst_port = dst_population.component.input_event_port_lut.get_single_obj_by(symbol=dst_port_name)
        self.connector = connector
        self.delay = NeuroUnitParser.QuantitySimple(delay).float_in_si()

        self.delay_upscale = -8
        assert self.delay * np.power(2,self.delay_upscale) < 1

        from neurounits.ast_annotations.node_fixedpointannotator import NodeFixedPointFormatAnnotator
        self.delay_int = NodeFixedPointFormatAnnotator.encode_value_cls(self.delay, self.delay_upscale, nbits=24)

        self.parameter_map = parameter_map
        # Some error checking









class PopRec(object):
    def __init__(self, global_offset, size, src_population, src_pop_start_index, node, tags):
        self.global_offset = global_offset
        self.size = size
        self.src_population = src_population
        self.src_pop_start_index = src_pop_start_index
        self.node = node
        self.tags = tags

        self.src_pop_end_index = src_pop_start_index + size


    def __str__(self):
        return "<PopRec [global_offset: %s , size: %s] from [src_pop: %s recording: %s local_offset: %s ] {Tags:%s}>" % (
                        self.global_offset, self.size, self.src_population.name, self.src_pop_start_index, self.node.symbol, self.tags )




class Network(object):
    def __init__(self, ):
        self.is_frozen=False
        self.populations = []
        self.event_port_connectors = []
        self.electrical_synapse_projections = []
        self.additional_events = []


        self._record_traces = defaultdict( list )
        self._record_output_events = defaultdict( list )
        self._record_input_events = defaultdict( list )

        # Setup properly by finalise:
        self.all_trace_recordings = None
        self.n_trace_recording_buffers = None
        self.all_output_event_recordings = None
        self.n_output_event_recording_buffers = None
        self.all_input_event_recordings = None
        self.n_input_event_recording_buffers = None




    # Syntactic sugar
    # ================
    def create_population(self, **kwargs):
        assert not self.is_frozen
        pop = Population(**kwargs)
        self.add(pop)
        return pop
    def create_eventportconnector(self, **kwargs):
        assert not self.is_frozen
        pop = EventPortConnector(**kwargs)
        self.add(pop)
        return pop
    def create_electricalsynapseprojection(self, **kwargs):
        assert not self.is_frozen
        pop = ElectricalSynapseProjection(**kwargs)
        self.add(pop)
        return pop



    def record_traces(self, subpopulations, terminal_node_names):
        assert not self.is_frozen
        if isinstance(terminal_node_names, basestring):
            terminal_node_names = terminal_node_names.split()


        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]

        for terminal_node_name in terminal_node_names:
            for subpop in subpopulations:
                self._record_trace_for_population(subpop, terminal_node_name)

    def record_output_events(self, subpopulations, port_name):
        assert not self.is_frozen
        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]
        for subpop in subpopulations:
            self._record_output_events_for_population(subpop, port_name)

    def record_input_events(self, subpopulations, port_name):
        assert not self.is_frozen
        if isinstance(subpopulations, (Population,SubPopulation)):
            subpopulations = [subpopulations]
        for subpop in subpopulations:
            #print 'Recordings', subpop
            self._record_input_events_for_population(subpop, port_name)



    def _record_trace_for_population(self, subpop, _terminal_node_name):
        from neurounits import ast
        terminal_node_names = None
        if _terminal_node_name == '*':
            terminal_node_names = [ t.symbol for t in subpop.component.terminal_symbols if not isinstance(t, (ast.SymbolicConstant, ast.TimeVariable)) ]
        else:
            terminal_node_names = [_terminal_node_name]

        population = subpop.population

        for terminal_node_name in terminal_node_names:
            terminal_node = population.component.get_terminal_obj(terminal_node_name)
            self._record_traces[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )

    def _record_output_events_for_population(self, subpop, terminal_node_name):
        population = subpop.population
        terminal_node = population.component.output_event_port_lut.get_single_obj_by(symbol=terminal_node_name)
        self._record_output_events[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )

    def _record_input_events_for_population(self, subpop, terminal_node_name):
        population = subpop.population
        terminal_node = population.component.input_event_port_lut.get_single_obj_by(symbol=terminal_node_name)
        self._record_input_events[(population, terminal_node)].append( (subpop.indices, subpop.autotag) )



    def finalise(self):
        if self.is_frozen:
            return 
        self.is_frozen=True
        # Work out which traces to record:
        def curr_rec_offset(lst):
            return 0 if lst == [] else ( lst[-1].global_offset + lst[-1].size )

        # Traces:
        assert self.all_trace_recordings is None
        self.all_trace_recordings = []
        for (population, terminal_node), values in sorted(self._record_traces.items()):
            for indices, autotag in sorted(values):
                global_offset = curr_rec_offset(self.all_trace_recordings)
                size = indices[1] - indices[0]
                self.all_trace_recordings.append( PopRec( global_offset=global_offset, size=size, src_population=population, src_pop_start_index=indices[0], node=terminal_node, tags=autotag ) )
        self.n_trace_recording_buffers =  curr_rec_offset(self.all_trace_recordings)




         # Output events:
        assert self.all_output_event_recordings is None
        self.all_output_event_recordings = []
        for (population, terminal_node), values in sorted(self._record_output_events.items()):
            for indices, autotag in sorted(values):
                global_offset = curr_rec_offset(self.all_output_event_recordings)
                size = indices[1] - indices[0]
                self.all_output_event_recordings.append( PopRec( global_offset=global_offset, size=size, src_population=population, src_pop_start_index=indices[0], node=terminal_node, tags=autotag ) )
        self.n_output_event_recording_buffers =  curr_rec_offset(self.all_output_event_recordings)


         # input events:
        assert self.all_input_event_recordings is None
        self.all_input_event_recordings = []
        for (population, terminal_node), values in sorted(self._record_input_events.items()):
            for indices, autotag in sorted(values):
                global_offset = curr_rec_offset(self.all_input_event_recordings)
                size = indices[1] - indices[0]
                self.all_input_event_recordings.append( PopRec( global_offset=global_offset, size=size, src_population=population, src_pop_start_index=indices[0], node=terminal_node, tags=autotag ) )
        self.n_input_event_recording_buffers =  curr_rec_offset(self.all_input_event_recordings)


        # Resolve all the connections:
        # Event Ports:
        for p in self.event_port_connectors:
            for dst_param_name, src in p.parameter_map.items():

                dst_param = p.dst_port.parameters.get_single_obj_by(symbol=dst_param_name)
                assert isinstance(src, FixedValue)
                # Lets encode it:
                anntr = p.dst_population.component.annotation_mgr._annotators['fixed-point-format-ann']
                from neurounits.ast_annotations import NodeFixedPointFormatAnnotator
                assert isinstance(anntr, NodeFixedPointFormatAnnotator )


                src.value_scaled_for_target = anntr.encode_value(value=src.value.float_in_si(), upscaling_pow=dst_param.annotations['fixed-point-format'].upscale )





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

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor, add_connection_set_functor):

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

class ExplicitIndicesSet(PopulationConnector):
    def __init__(self, indices):
        self.indices = indices

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor, add_connection_set_functor):

        src_tgt_map = defaultdict( set)
        for i,j in self.indices:
            src_tgt_map[i].add(j);



        from mako.template import Template
        tmpl = Template('''

        %for src, tgts in src_tgt_map.items():
            <%tgt_str = ','.join( ['IntType(%s)'%t for t in tgts ] ) %>
            IntType tgts_from_${src}[] = { ${tgt_str} };
            IntType tgts_from_${src}_len = IntType(${len(tgts)} ) ;

            // # TODO: refactor this out properly:
            projections[${src}].assign(tgts_from_${src}, tgts_from_${src} + get_value32(tgts_from_${src}_len) );
        %endfor

        ''')
        return tmpl.render(
                indices=self.indices,
                add_connection_functor = add_connection_functor,
                src_tgt_map=src_tgt_map
                )


class ExplicitIndicesLoop(PopulationConnector):
    def __init__(self, indices):
        self.indices = indices

    def build_c(self, src_pop_size_expr, dst_pop_size_expr, add_connection_functor, add_connection_set_functor):

        src_tgt_map = defaultdict( set)
        for i,j in self.indices:
            src_tgt_map[i].add(j);



        from mako.template import Template
        tmpl = Template('''
        %for i,j in indices:
        ${ add_connection_functor(i, j) }
        %endfor


        ''')
        return tmpl.render(
                indices=self.indices,
                add_connection_functor = add_connection_functor,
                src_tgt_map=src_tgt_map
                )
