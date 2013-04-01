
import neurounits
import inspect
import itertools
import numpy as np

from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree


txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ).read()
txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/more_components.9ml" ).read()
txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/complex_component.9ml" ).read()

src_files = [
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ,
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/more_components.9ml" ,
    "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/complex_component.9ml" ,
]



library_manager = None
for s in src_files:
    text = open(s).read()
    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( text, library_manager=library_manager)
    #print library_manager





#print library_manager.components



#def summarise_component(comp):
#    print comp
#    for k,v in comp.__dict__.items():
#        if k[0] == '_':
#            #continue
#            pass
#        print '  ', k,v
#    print comp.__dict__
#    
#    params = inspect.getmembers(comp)
#    for k in params:
#        if k[0][0] == '_':
#            continue
#        try:
#            print '  ', k
#        except:
#            pass
#            
#    for tr in comp.transitions:
#        print tr
#        for a in tr.actions:
#            
#            print ' ', a
#    
#for comp in library_manager.components:
#    print
#    summarise_component(comp)



#print 'Components Loaded:'
#for comp in library_manager.components:
#    print comp.name
        





test_text = """
module test {
    define_component step_current{
        p=2*t
        #f' = 3
        regime OFF{
            i=0A
            on (t>t_start) {
                
                transition_to ON;
            }
            }
            
        regime ON{
            i = i_amp
        }
        
        
        <=> OUTPUT i:(A)
        <=> PARAMETER i_amp:(A), t_start
        <=> INPUT t:(ms)
    }
    
    
    
      
    define_component i_squarewave{
        t_last'=0
        i=0nA
        regime init{
            i=0A
            on(0<1){
                t_last = 0s
                transition_to OFF 
                }
        }

        regime OFF{
            i=0A
            on (t>t_last + t_off) {
                t_last = t
                transition_to ON;
                }
            }
        
        regime ON{
            i = i_amp
            on (t>t_last + t_on) {
                t_last = t
                transition_to OFF;
                }
        }
        
        <=> PARAMETER t_on, t_off 
        <=> OUTPUT i:(A)
        <=> PARAMETER i_amp:(A)        
        <=> INPUT t:(ms)    
        
        }
    




	define_component std_neuron {

	    
        V' = i_sum / C

	    <=> ANALOG_REDUCE_PORT i_sum 
	    <=> PARAMETER C:(uF)
	    <=> OUTPUT     V: mV            
        
	}
    
    define_component chlstd_leak {
        
        
	    i = g * (erev-V) *a 
        a = 1000 um2
	    <=> PARAMETER g:(S/m2), erev
	    <=> OUTPUT    i:(mA)            
	    <=> INPUT     V: mV             
        
	}
    
    
}
"""


library_manager = neurounits.NeuroUnitParser.Parse9MLFile( test_text )

#for component in library_manager.components:
#    print component
 
    







    
    
        
from neurounits.ast_builder.eqnsetbuilder import BuildData  
from neurounits.ast_builder.eqnsetbuilder import SingleSetDict
from neurounits.ast import NineMLComponent
from neurounits.ast import SuppliedValue
from neurounits.ast.astobjects_nineml import AnalogReducePort
    



def build_compound_component(name, instantiate,  analog_connections, event_connections,  remap_ports, prefix='/'):
    
    

        
        
    lib_mgrs = list(set( [comp.library_manager for comp in instantiate.values()]) )
    assert len( lib_mgrs ) == 1 and lib_mgrs[0] is not None
    lib_mgr = lib_mgrs[0]
    #print lib_mgr
    
    
    #First step, lets build a new component, by cloning all the components:
    # Cloned Components:
    #for (name, component) in instantiate.items():
    #    c = CloneObject().visit(
    
    
    # 2. Rename all the internal names of the objects:
    new_name_dict ={}
    for component_name, component in instantiate.items():
        for obj in component.terminal_symbols:  
            obj.symbol = component_name + prefix + obj.symbol
            
        # Warning - the keys in this dictionary are now going to be incorrect:
        for rtname, obj in component.rt_graphs.items():  
            obj.name = component_name + prefix + (obj.name if obj.name else '')
            
            
    # 3. Copy the relevant parts of the AST tree into a new build-data object:
    builddata = BuildData()
    builddata.eqnset_name = name
    
    builddata.timederivatives = SingleSetDict()
    builddata.assignments = SingleSetDict()
    builddata.rt_graphs = SingleSetDict()
    
    for c in instantiate.values():
        for td in c.timederivatives:
            builddata.timederivatives[td.lhs] = td
        for ass in c.assignments:
            builddata.assignments[ass.lhs] = ass
    
        for symconst in c.symbolicconstants:
            builddata.symbolicconstants[symconst.symbol] = symconst
    
        for rt_graph in c.rt_graphs.values():  
            builddata.rt_graphs[rt_graph.name] = rt_graph
            
        
        builddata.transitions_triggers.extend( c._transitions_triggers)
        builddata.transitions_events.extend( c._transitions_events)
    
    
    
    
    
    # 4. Build the object:
    comp = NineMLComponent(library_manager = lib_mgr,
                    builder = None,
                    builddata = builddata,
                    io_data = [],
                    )

    from neurounits.visitors.common.ast_replace_node import ReplaceNode
    
    
    # 5. Connect the relevant ports internally:
    for (src,dst) in analog_connections:
        
        src_obj = comp.get_terminal_obj(src)
        dst_obj = comp.get_terminal_obj(dst)
        
        #print 'Connecting:', src_obj, 'to', dst_obj
        if isinstance(dst_obj, AnalogReducePort):
            dst_obj.rhses.append(src_obj)
        elif isinstance(dst_obj, SuppliedValue):
            r = ReplaceNode(srcObj=dst_obj, dstObj = src_obj).visit(comp)
        else:
            assert False, 'Unexpected node type: %s' % dst_obj
    comp._cache_nodes()
        
        
    # 6. Map relevant ports externally:
    for (src,dst) in remap_ports:
        assert not dst in [ s.symbol for s in comp.terminal_symbols]
    
        
        comp._cache_nodes()

    comp._cache_nodes()
    #comp.summarise()
    
    print 'Propagating Units:'
    PropogateDimensions.propogate_dimensions(component)
    print 'OK!'
    # 7. Close Reduce ports:
    # TODO:
    
    
    
    # Return the new component:
    return comp
    
    
    
    
    
from neurounits.units_misc import safe_dict_merge
import neurounits.ast as ast

    
class EventHandler(object):
    def emit_event(self, ):
        pass
    
    
    
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator
#def simulation_step( state, 
    
    
def close_analog_port(ap, comp):
    from neurounits.visitors.common.ast_replace_node import ReplaceNode
    if len(ap.rhses) == 2:
        new_node = ast.AddOp( ap.rhses[0], ap.rhses[1] )
        r = ReplaceNode(srcObj=ap, dstObj = new_node).visit(comp)
        comp._cache_nodes()
        PropogateDimensions.propogate_dimensions(comp)
        return
        
    if len(ap.rhses) == 3:
        new_node = ast.AddOp( ap.rhses[0], ast.AddOp(ap.rhses[1],ap.rhses[2] ) )
        r = ReplaceNode(srcObj=ap, dstObj = new_node).visit(comp)
        comp._cache_nodes()
        PropogateDimensions.propogate_dimensions(comp)
        return
        
    assert False   
    
    
    
    
def do_transition_change(tr, rt_graph, state_vars, current_regimes):
    print 'Transition Triggered!', 
    
    
    for action in tr.actions:
        print action
        assert False
    
    current_regimes[rt_graph] = tr.target_regime
    
    #assert False
    
    
def simulate_component(component, times, parameters,initial_state_values, initial_regimes, close_reduce_ports):
    
    #from neurounits.visitors.common.plot_networkx import ActionerPlotNetworkX
    #ActionerPlotNetworkX(component)

    print '------------------------'
    print '------------------------'
    component.summarise()
    print '------------------------'
    print '------------------------'
    
    
    if close_reduce_ports:
        for ap in component.analog_reduce_ports:
            print 'Closing', ap
            close_analog_port(ap, component)
            
    #assert False
    
    neurounits.Q1 = neurounits.NeuroUnitParser.QuantitySimple
    
    parameters = dict( (k, neurounits.Q1(v)) for (k,v) in parameters.items() )
    initial_state_values = dict( (k, neurounits.Q1(v)) for (k,v) in initial_state_values.items() )
    
    
    VerifyUnitsInTree(component, unknown_ok=False)

    component.summarise()
    
    print
    print 'Simulating Component:', component.name
    print


    current_regimes = dict( [ (rt, rt.regimes.values()[0]) for rt in component.rt_graphs.values()] )
    
    for (rt,regime) in current_regimes.items():
        if rt.name=='i_inj/':
            current_regimes[rt] = rt.get_regime('OFF')
        if rt.name=='i_square/':
            current_regimes[rt] = rt.get_regime('OFF')        
        
        
        
        
    print 'Initial_regimes', current_regimes
     
    state = safe_dict_merge( parameters, initial_state_values, current_regimes)
    event_handler = EventHandler()
    
    f = FunctorGenerator(component)
    
    reses = []
    state_values = initial_state_values.copy()
    for i in range(len(times)-1):
        
        t = times[i]
        print 'Time:', t
        print '---------'
        
        reses.append( (t,state_values.copy()))
        
        t_unit = t * neurounits.NeuroUnitParser.QuantitySimple('1s')
        state_values['i_inj/t'] = t_unit
        state_values['i_square/t'] = t_unit
        
        
        deltas = {}
        for td in component.timederivatives:
            td_eval = f.timederivative_evaluators[td.lhs.symbol]
            
            s = safe_dict_merge(parameters, state_values)            
            res = td_eval(regime_states=current_regimes, **s)
            
            
            deltas[td.lhs.symbol] = res

        # Update the states:
        for d, dS in deltas.items():
            print d
            print state_values
            assert d in state_values
            state_values[d] += dS * (times[i+1] - times[i] ) * neurounits.NeuroUnitParser.QuantitySimple('1s')

        # Check for transitions:
        print 'Checking for transitions:'
        for rt_graph in component.rt_graphs.values():
            current_regime = current_regimes[rt_graph]
            print '  ', rt_graph, '(in %s)' % current_regime
            for transition in component.transitions_from_regime(current_regime):
                print '       Checking',  transition
                res = f.transition_triggers_evals[transition](regime_states=current_regimes, **s)
                #print res
                if res:
                    do_transition_change(tr=transition, rt_graph=rt_graph, state_vars=s, current_regimes=current_regimes)
                
            print '    '
            
        print
        
        #if i>5:
        #    break
    
    
    
    import pylab 
    import numpy as np
    data = [ (t,states['nrn/V'].float_in_si()) for (t,states) in reses]
    data = np.array(data)
    pylab.ylim((-70e-3,50e-3))
    pylab.plot( data[:,0], data[:,1] )
    print state_values
    pylab.show()




def test1():
    #def merge_components( components
    library_manager =  neurounits.NeuroUnitParser.Parse9MLFile( test_text )
    chlstd_leak = library_manager.get('chlstd_leak')
    std_neuron = library_manager.get('std_neuron')
    step_current = library_manager.get('step_current')
    square_current = library_manager.get('i_squarewave')


    c = build_compound_component( 
          name = 'Mikes new Neuron',
          instantiate = { 'lk': chlstd_leak, 'nrn': std_neuron, 'i_inj':step_current, 'i_square':square_current },
          event_connections = [],
          analog_connections = [
            ('i_inj/i', 'nrn/i_sum'), 
            ('lk/i', 'nrn/i_sum'), 
            ('i_square/i', 'nrn/i_sum'),
            ('nrn/V', 'lk/V'),
          ],
          remap_ports = [
            ('i_inj/t','t')
            ] ,
          

          )
            

    simulate_component(component=c, 
                        times = np.linspace(0,1,num=1000), 
                        close_reduce_ports=True,
                        parameters={
                            'i_inj/i_amp':'5pA', 
                            'lk/g': '0.1pS/um2', 
                            'nrn/C': '0.5pF', 
                            'lk/erev': '-60mV', 
                            'i_inj/t_start': '500ms',
                            'i_square/t_on': '100ms',
                            'i_square/t_off': '50ms',
                            
                            
                            },
                        initial_state_values={
                            'nrn/V': '-50mV',
                            'i_square/t_last': '0ms'
                        },
                        initial_regimes={
                            'inj/':'OFF'
                        }
            )





#test2()
test1()

