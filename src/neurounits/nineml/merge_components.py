
import neurounits.ast as ast
#import neurounits.visitors.common as visitors
from neurounits.ast_builder.eqnsetbuilder import BuildData
from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree
from neurounits.visitors.common.ast_replace_node import ReplaceNode





def _is_node_output(n):
    if isinstance( n, (ast.AssignedVariable, ast.StateVariable, ast.OutEventPort)):
        return True
    if isinstance( n, (ast.AnalogReducePort, ast.SuppliedValue, ast.InEventPort)):
        return False
    assert False, "I don't know the direction of: %s" % n

def _is_node_analog(n):
    if isinstance( n, (ast.AssignedVariable, ast.StateVariable, ast.AnalogReducePort, ast.SuppliedValue)):
        return True
    if isinstance( n, (ast.OutEventPort, ast.InEventPort)):
        return False
    assert False, "I don't know the direction of: %s %s" % (n, type(n))


def build_compound_component(component_name, instantiate,  analog_connections=None, event_connections=None,  renames=None, connections=None, prefix='/', auto_remap_time=True, merge_nodes=None, compound_ports_in=None, multiconnections=None):



    lib_mgrs = list(set( [comp.library_manager for comp in instantiate.values()]) )
    #print lib_mgrs
    assert len( lib_mgrs ) == 1 and lib_mgrs[0] is not None
    lib_mgr = lib_mgrs[0]


    # 1. Lets cloning all the subcomponents:
    instantiate = dict([(name, component.clone()) for (name, component) in instantiate.items()])


    symbols_not_to_rename = []
    if auto_remap_time:
        time_node = ast.SuppliedValue(symbol='t')
        symbols_not_to_rename.append(time_node)

        for component in instantiate.values():
            ##print component.terminal_symbols
            if component.has_terminal_obj('t'):
                ReplaceNode.replace_and_check(srcObj=component.get_terminal_obj('t'), dstObj=time_node, root=component)


    # 2. Rename all the internal names of the objects:
    for (subcomponent_name, component) in instantiate.items():
        ns_prefix = subcomponent_name + prefix
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

        for connector in itertools.chain( component._compound_ports_connectors):
            connector.name = ns_prefix + connector.name







    # 3. Copy the relevant parts of the AST tree into a new build-data object:
    builddata = BuildData()
    #builddata.eqnset_name = component_name

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
    comp = ast.NineMLComponent(
                    library_manager = lib_mgr,
                    builder = None,
                    builddata = builddata,
                    name=component_name,
                    )
    # Copy across the existing event port connnections
    for subcomponent in instantiate.values():
        for conn in subcomponent._event_port_connections:
            comp.add_event_port_connection(conn)


    # Copy accross existing compound ports:
    for component in instantiate.values():
        for compoundport in component._compound_ports_connectors:
            comp.add_compound_port(compoundport)
        #assert len( component._compound_ports_connectors) == 0




    # 5.A Resolve more general syntax for connections:
    if analog_connections is None:
        analog_connections = []
    if event_connections is None:
        event_connections = []




    from neurounits.visitors.common.plot_networkx import ActionerPlotNetworkX
    #ActionerPlotNetworkX(comp)
    #ActionerPlotNetworkX(lib_mgr)


    # Resolve the multiconnections, which involves adding pairs to either the 
    # analog or event connection lists:
    if multiconnections:
        for m in multiconnections:
            io1_name, io2_name = m
            #print 'Multicnnecitons;', m
            #print comp._compound_ports_connectors
            conn1 = comp._compound_ports_connectors.get_single_obj_by(name=io1_name)
            conn2 = comp._compound_ports_connectors.get_single_obj_by(name=io2_name)
            #print 'Connecting connectors:,', conn1, conn2

            # sort out the direction:
            if  (conn1.get_direction()=='in' and conn2.get_direction()=='out'):
                conn1,conn2 = conn2, conn1
            assert (conn1.get_direction()=='out' and conn2.get_direction()=='in') 
            compound_ports = list(set([conn1.compound_port_def, conn2.compound_port_def] ) )
            #print compound_ports
            assert len(compound_ports) == 1
            compound_port = compound_ports[0]

            # Make the connections:
            #print 'Resolving connections:'
            for wire in compound_port.connections:
                #print "Connecting:", repr(wire)
                #print conn1.wire_mappings
                pre = conn1.wire_mappings.get_single_obj_by(compound_port=wire)
                post = conn2.wire_mappings.get_single_obj_by(compound_port=wire)

                # Resolve the direction again!:
                if wire.direction  =='DirRight':
                    pass
                elif wire.direction == 'DirLeft':
                    pre,post = post,pre
                else:
                    assert False

                #print 'Pre: in/Out?:', _is_node_output(pre.component_port)
                #print 'Pre: in/Out?:', _is_node_output(post.component_port)


                assert _is_node_output(pre.component_port)
                assert not _is_node_output(post.component_port)
                assert _is_node_analog(pre.component_port) == _is_node_analog(post.component_port)

                if _is_node_analog(pre.component_port):
                    analog_connections.append( (pre.component_port, post.component_port))
                else:
                    event_connections.append( (pre.component_port, post.component_port))

                



                #print wire.direction

                #print pre, post
                #print





        #assert False

    # Ok, and single connections ('helper parameter')
    if connections is not None:
        for c1,c2 in connections:
            #print c1,c2
            t1 = comp.get_terminal_obj_or_port(c1)
            t2 = comp.get_terminal_obj_or_port(c2)

            # Analog Ports:
            if _is_node_analog(t1):
                assert _is_node_analog(t2) == True
                if _is_node_output(t1):
                    assert not _is_node_output(t2)
                    analog_connections.append( (c1,c2))
                else:
                    assert _is_node_output(t2)
                    analog_connections.append( (c2,c1))

            # Event Ports:
            else:
                assert _is_node_analog(t2) == False
                if _is_node_output(t1):
                    assert not _is_node_output(t2)
                    event_connections.append( (c1,c2))
                else:
                    assert _is_node_output(t2)
                    event_connections.append( (c2,c1))


            #print t1,t2

    #assert False


    mergeable_node_types = (ast.SuppliedValue, ast.Parameter, ast.InEventPort, )
    #print merge_nodes
    if merge_nodes:
        for srcs, new_name in merge_nodes:
            if not srcs:
                assert False, 'No sources found'

            # Sanity check:
            src_objs = [comp.get_terminal_obj(s) for s in srcs]
            node_types = list( set( [ type(s) for s in src_objs ] ) )
            assert len(node_types) == 1, 'Different types of nodes found in merge'
            assert node_types[0] in mergeable_node_types

            # OK, so they are all off the same type, and the type is mergable:
            # So, lets remap everything to first obj
            dst_obj = src_objs[0]
            for s in src_objs[1:]:
                ReplaceNode.replace_and_check(srcObj=s, dstObj=dst_obj, root=comp)

            # And now, we can rename the first obj:
            dst_obj.symbol = new_name



    #assert False




    # 5. Connect the relevant ports internally:
    for (src, dst) in analog_connections:
        if isinstance(src, basestring):
            src_obj = comp.get_terminal_obj(src)
        else:
            assert src in comp.all_terminal_objs()
            src_obj = src
        if isinstance(dst, basestring):
            dst_obj = comp.get_terminal_obj(dst)
        else:
            assert dst in comp.all_terminal_objs(), 'Dest is not a terminal_symbols: %s' % dst
            dst_obj = dst
        
        #dst_obj = comp.get_terminal_obj(dst)
        del src, dst

        # Sanity Checking:
        assert _is_node_analog(src_obj)
        assert _is_node_analog(dst_obj)
        assert _is_node_output(src_obj)
        assert not _is_node_output(dst_obj)


        if isinstance(dst_obj, ast.AnalogReducePort):
            dst_obj.rhses.append(src_obj)
        elif isinstance(dst_obj, ast.SuppliedValue):
            ReplaceNode.replace_and_check(srcObj=dst_obj, dstObj=src_obj, root=comp)
        else:
            assert False, 'Unexpected node type: %s' % dst_obj


    for (src, dst) in event_connections:
        src_port = comp.output_event_port_lut.get_single_obj_by(name=src)
        dst_port = comp.input_event_port_lut.get_single_obj_by(name=dst)
        conn = ast.EventPortConnection( src_port = src_port, dst_port = dst_port)
        comp.add_event_port_connection(conn)




    # 6. Map relevant ports externally:
    if renames:
        for (src, dst) in renames:
            assert not dst in [s.symbol for s in comp.terminal_symbols]
            s_obj = comp.get_terminal_obj(src)
            s_obj.symbol = dst
            assert not src in [s.symbol for s in comp.terminal_symbols]



    # 7. Create any new compound ports:
    #print
    if compound_ports_in:
        for compound_port in compound_ports_in:
            #print 'Compound port:', compound_port
            local_name, porttype, direction, wire_mapping_txts = compound_port
            compound_port_def = lib_mgr.get(porttype)
            #print compound_port_def
            wire_mappings = []
            for wire_mapping_txt in wire_mapping_txts:
                wire_map = ast.CompoundPortConnectorWireMapping(
                                component_port = comp.get_terminal_obj(wire_mapping_txt[0]),
                                compound_port = compound_port_def.get_wire(wire_mapping_txt[1]),
                                )
                wire_mappings.append(wire_map)

            conn = ast.CompoundPortConnector(name=local_name, compound_port_def = compound_port_def, wire_mappings=wire_mappings, direction=direction)
            comp.add_compound_port(conn)




    # Ensure all the units are propogated ok, because we might have added new
    # nodes:
    PropogateDimensions.propogate_dimensions(comp)
    VerifyUnitsInTree(comp, unknown_ok=False)

    # Return the new component:
    return comp

