

import neurounits.ast as ast
from collections import defaultdict


def close_unconnected_input_event_ports(component):
    assert False

def remove_unused_rt_graphs(component):

    # Remove any RegimeDispatchMaps that only have a single regime:
    for ass in list(component._eqn_assignment) + list(component._eqn_time_derivatives) :
        if isinstance(ass.rhs_map, ast.EqnRegimeDispatchMap):
            if len(ass.rhs_map.rhs_map) == 1:
                #print 'Candidate for removal:', repr(ass)
                regime = list(ass.rhs_map.rhs_map.keys())[0]
                # Sanity check:
                assert len(regime.parent_rt_graph.regimes) == 1 or regime.name == None

                ass.rhs_map = ass.rhs_map.rhs_map.values()[0]
            else:
                pass
                #print 'Not removing', repr(ass)


    # Lets remove unused rt_graph, whi is any aren't used in a RegimeDispatchMap,
    # or any that don't have any transitions:
    graph_transitions = defaultdict(list) # {rt_graph -> [tr1, tr2]}
    for tr in component.transitions:
        graph_transitions[tr.rt_graph].append(tr)
    used_rt_graphs = set()
    for ass in list(component._eqn_assignment) + list(component._eqn_time_derivatives) :
        if isinstance(ass.rhs_map, ast.EqnRegimeDispatchMap):
            used_rt_graphs.add(ass.rhs_map.get_rt_graph() )
    new_rt_graphs = [ rt_graph for rt_graph in component._rt_graphs if (rt_graph in used_rt_graphs) or (len(graph_transitions[rt_graph]) > 0) ]
    n_prev, n_new = len(component.rt_graphs), len(new_rt_graphs)
    #print 'Removed %d/%d RT_Graphs' % (n_prev-n_new, n_prev)
    component._rt_graphs = new_rt_graphs

    #print used_rt_graphs



