
import neurounits.ast as ast

from neurounits.ast_builder.eqnsetbuilder import BuildData
from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
from neurounits.ast_builder.builder_visitor_propogate_dimensions import VerifyUnitsInTree
from neurounits.visitors.common.ast_replace_node import ReplaceNode





def _is_node_output(n):
    if isinstance( n, (ast.AssignedVariable, ast.StateVariable, ast.OutEventPort, ast.SymbolicConstant)):
        return True
    if isinstance( n, (ast.AnalogReducePort, ast.SuppliedValue, ast.InEventPort)):
        return False
    assert False, "I don't know the direction of: %s" % n

def _is_node_analog(n):
    if isinstance( n, (ast.AssignedVariable, ast.StateVariable, ast.AnalogReducePort, ast.SuppliedValue, ast.SymbolicConstant)):
        return True
    if isinstance( n, (ast.OutEventPort, ast.InEventPort)):
        return False
    assert False, "I don't know the direction of: %s %s" % (n, type(n))


def build_compound_component(component_name, instantiate,  analog_connections=None, event_connections=None,  renames=None, connections=None, prefix='/', auto_remap_time=True, merge_nodes=None, interfaces_in=None, multiconnections=None, set_parameters=None):
    #print 'Building Compund Componet:', component_name



    lib_mgrs = list(set( [comp.library_manager for comp in instantiate.values()]) )

    assert len( lib_mgrs ) == 1 and lib_mgrs[0] is not None
    lib_mgr = lib_mgrs[0]


    # 1. Lets cloning all the subcomponents:
    instantiate = dict([(name, component.clone()) for (name, component) in instantiate.items()])


    symbols_not_to_rename = []
    if auto_remap_time:
        time_node = ast.SuppliedValue(symbol='t')
        symbols_not_to_rename.append(time_node)

        for component in instantiate.values():

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
            port.symbol = ns_prefix + port.symbol

        for connector in itertools.chain( component._interface_connectors):
            connector.symbol = ns_prefix + connector.symbol







    # 3. Copy the relevant parts of the AST tree into a new build-data object:
    builddata = BuildData()


    builddata.timederivatives = []
    builddata.assignments = []
    builddata.rt_graphs = []
    builddata.symbolicconstants = []

    for c in instantiate.values():
        #print 'merging component:', repr(c)
        for td in c.timederivatives:
            #print 'Merging in ', repr(td)
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
        for interface in component._interface_connectors:
            comp.add_interface_connector(interface)




    # 5.A Resolve more general syntax for connections:
    if analog_connections is None:
        analog_connections = []
    if event_connections is None:
        event_connections = []


    # Resolve the multiconnections, which involves adding pairs to either the 
    # analog or event connection lists:
    if multiconnections:
        for m in multiconnections:
            io1_name, io2_name = m
            conn1 = comp._interface_connectors.get_single_obj_by(symbol=io1_name)
            conn2 = comp._interface_connectors.get_single_obj_by(symbol=io2_name)
            #print 'Connecting connectors:,', conn1, conn2

            # sort out the direction:
            if  (conn1.get_direction()=='in' and conn2.get_direction()=='out'):
                conn1,conn2 = conn2, conn1
            assert (conn1.get_direction()=='out' and conn2.get_direction()=='in') 
            interfaces = list(set([conn1.interface_def, conn2.interface_def] ) )
            
            assert len(interfaces) == 1
            interface = interfaces[0]

            # Make the connections:
            for wire in interface.connections:


                pre = conn1.wire_mappings.get_single_obj_by(interface_port=wire)
                post = conn2.wire_mappings.get_single_obj_by(interface_port=wire)

                # Resolve the direction again!:
                if wire.direction  =='DirRight':
                    pass
                elif wire.direction == 'DirLeft':
                    pre,post = post,pre
                else:
                    assert False


                assert _is_node_output(pre.component_port)
                assert not _is_node_output(post.component_port)
                assert _is_node_analog(pre.component_port) == _is_node_analog(post.component_port)

                if _is_node_analog(pre.component_port):
                    analog_connections.append( (pre.component_port, post.component_port))
                else:
                    event_connections.append( (pre.component_port, post.component_port))


    # Ok, and single connections ('helper parameter')
    if connections is not None:
        for c1,c2 in connections:
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




    mergeable_node_types = (ast.SuppliedValue, ast.Parameter, ast.InEventPort, )
    if merge_nodes:
        for srcs, new_name in merge_nodes:
            if not srcs:
                assert False, 'No sources found'

            # Sanity check:
            src_objs = [comp.get_terminal_obj_or_port(s) for s in srcs]
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
        src_port = comp.output_event_port_lut.get_single_obj_by(symbol=src)
        dst_port = comp.input_event_port_lut.get_single_obj_by(symbol=dst)
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
    # TODO: shouldn't this go higher up? before connections??
    if interfaces_in:
        for interface in interfaces_in:
            local_name, porttype, direction, wire_mapping_txts = interface
            comp.build_interface_connector(local_name=local_name, porttype=porttype, direction=direction, wire_mapping_txts=wire_mapping_txts)

    #8. Set parameters:
    if set_parameters:
        for lhs, rhs in set_parameters:
            #print 'Set', lhs, rhs
            old_node = comp._parameters_lut.get_single_obj_by(symbol=lhs)
            assert isinstance(rhs, ast.ASTExpressionObject)

            new_node = rhs #ast.ConstValue(value=rhs)

            ReplaceNode.replace_and_check( srcObj=old_node, dstObj=new_node, root=comp)



    # Ensure all the units are propogated ok, because we might have added new
    # nodes:
    PropogateDimensions.propogate_dimensions(comp)
    VerifyUnitsInTree(comp, unknown_ok=False)

    # Return the new component:
    return comp

