
import neurounits.ast as ast
#import neurounits.visitors.common as visitors
from neurounits.ast_builder.eqnsetbuilder import BuildData
from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree
from neurounits.visitors.common.ast_replace_node import ReplaceNode

def build_compound_component(name, instantiate,  analog_connections, event_connections=None,  remap_ports=None, prefix='/', auto_remap_time=True):


    lib_mgrs = list(set( [comp.library_manager for comp in instantiate.values()]) )
    assert len( lib_mgrs ) == 1 and lib_mgrs[0] is not None
    lib_mgr = lib_mgrs[0]


    # 1. Lets cloning all the subcomponents:
    instantiate = dict([(name, component.clone()) for (name, component) in instantiate.items()])


    symbols_not_to_rename = []
    if auto_remap_time:
        time_node = ast.SuppliedValue(symbol='t')
        symbols_not_to_rename.append(time_node)

        for (component_name, component) in instantiate.items():
            #print component.terminal_symbols
            if component.has_terminal_obj('t'):
                ReplaceNode.replace_and_check(srcObj=component.get_terminal_obj('t'), dstObj=time_node, root=component)


    # 2. Rename all the internal names of the objects:
    for (component_name, component) in instantiate.items():
        ns_prefix = component_name + prefix
        # Symbols:
        for obj in component.terminal_symbols:
            if obj in symbols_not_to_rename:
                continue
            obj.symbol = ns_prefix + obj.symbol


        # RT Graphs names (not the names of the regimes!):
        for rt_graph in component.rt_graphs:
            rt_graph.name = ns_prefix + (rt_graph.name if rt_graph.name else '')

        #Event Ports:
        import itertools
        for port in itertools.chain( component.output_event_port_lut,  component.input_event_port_lut):
            port.name = ns_prefix + port.name







    # 3. Copy the relevant parts of the AST tree into a new build-data object:
    builddata = BuildData()
    builddata.eqnset_name = name

    builddata.timederivatives = []
    builddata.assignments = []
    builddata.rt_graphs = []
    builddata.symbolicconstants = []

    for c in instantiate.values():
        for td in c.timederivatives:
            builddata.timederivatives.append( td )
        for ass in c.assignments:
            builddata.assignments.append(ass)

        for symconst in c.symbolicconstants:
            builddata.symbolicconstants.append(symconst)

        for rt_graph in c.rt_graphs:
            builddata.rt_graphs.append(rt_graph)

        builddata.transitions_triggers.extend(c._transitions_triggers)
        builddata.transitions_events.extend(c._transitions_events)

    # 4. Build the object:
    comp = ast.NineMLComponent(library_manager = lib_mgr,
                    builder = None,
                    builddata = builddata,
                    name=name,
                    )
    # Copy across the existing event port connnections
    for subcomponent in instantiate.values():
        for conn in subcomponent._event_port_connections:
            comp.add_event_port_connection(conn)


    # 5. Connect the relevant ports internally:
    for (src, dst) in analog_connections:

        src_obj = comp.get_terminal_obj(src)
        dst_obj = comp.get_terminal_obj(dst)

        if isinstance(dst_obj, ast.AnalogReducePort):
            dst_obj.rhses.append(src_obj)
        elif isinstance(dst_obj, ast.SuppliedValue):
            ReplaceNode.replace_and_check(srcObj=dst_obj, dstObj=src_obj, root=comp)
            
        else:
            assert False, 'Unexpected node type: %s' % dst_obj

    #print comp.name
    #print 'Outports:', comp.output_event_port_lut
    #print 'Inports:', comp.input_event_port_lut
    for (src, dst) in event_connections:
        #print src, dst
        src_port = comp.output_event_port_lut.get_single_obj_by(name=src) 
        dst_port = comp.input_event_port_lut.get_single_obj_by(name=dst) 
        conn = ast.EventPortConnection( src_port = src_port, dst_port = dst_port)
        comp.add_event_port_connection(conn)
        

        

    # 6. Map relevant ports externally:
    if remap_ports:
        for (src, dst) in remap_ports:
            assert False
            assert not dst in [s.symbol for s in comp.terminal_symbols]
            


    # Ensure all the units are propogated ok, because we might have added new
    # nodes:
    PropogateDimensions.propogate_dimensions(comp)
    VerifyUnitsInTree(comp, unknown_ok=False)

    # Return the new component:
    return comp

