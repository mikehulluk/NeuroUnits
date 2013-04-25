


import pylab as plt



import networkx as nx
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance


class IntegrationBlock(object):
    def __init__(self, objs):
        self.state_variables = objs
        self.assignments = []#assignments

    def __repr__(self):
        return '<IntegrationBlock: %s>' % (','.join([ sv.symbol for sv in self.state_variables ] ) ) 




def separate_integration_blocks(component):
    print 'Separating Integration blocks'

    component.close_all_analog_reduce_ports()


    # Build the original dependance graph:
    graph = VisitorFindDirectSymbolDependance.build_direct_dependancy_graph(component)

    # Plot:
    do_plot = False
    if do_plot:
        objs, labels, colors = zip( * [ (d[0], d[1]['label'], d[1]['color'] ) for d in graph.nodes_iter(data=True) ] )
        nx.draw_graphviz(graph, font_size=10, iteration=200, node_color=colors,scale=1, labels=dict(zip(objs,labels)) )
        plt.show()


    res = nx.components.strongly_connected_component_subgraphs(graph)
    for subgraph in res:
        print subgraph, len(subgraph)
        print list(subgraph.nodes_iter() )


    # Get the strongly connected components, and the dependancies between the 
    # nodes:
    scc = nx.strongly_connected_components(graph)
    cond = nx.condensation(graph, scc=scc)

    #print 'SCC', scc
    #print 'Cond', cond
    #print cond, type(cond)

    for node, node_data in cond.nodes_iter(data=True):
        print node, node_data


    ordering = reversed( nx.topological_sort(cond) )
    print ordering

    blks = []
    for o in ordering:
        blk = IntegrationBlock( objs = scc[o] )
        blks.append(blk)


    return blks

    #for blk in blks:
    #    print blk



    #print 'Done'
    #assert False




    #from dependancy_new import get_dependancy_graph

    #get_dependancy_graph(component)


