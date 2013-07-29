
import networkx as nx
import matplotlib.pyplot as plt

from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate
from neurounits.visitors import ASTVisitorBase
from neurounits.ast_builder.eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.ast import OnEventStateAssignment
import neurounits.ast as ast
import itertools

import collections



class DefaultNodeColors(ASTVisitorBase):

    def VisitLibrary(self, o, **kwargs):
        return 'green'

    def visit(self, o):

        if isinstance(o, SymbolProxy):
            return 'red'
        if isinstance(o, OnEventStateAssignment):
            return 'orange'
        if isinstance(o, ast.NineMLComponent):
            return 'yellow'
        if isinstance(o, ast.OnEventTransition):
            return 'pink'
        if isinstance(o, ast.OnTriggerTransition):
            return 'cyan'
        if isinstance(o, ast.CompoundPortConnector):
            return 'red'

        return 'blue'

        try:
            return ASTVisitorBase.visit(self, o)
        except NotImplementedError:
            return 'red'






class ActionerPlotNetworkX(object):
    def __init__(self, o, labels = None, colors=None):


        graph = nx.DiGraph()

        connections = ActionerGetConnections(o).get_connections()
        for node in connections.keys():
            graph.add_node(node, color='green', label='"%s"' % repr(node) )

        for (node, connections) in connections.items():
            for c in connections:
                graph.add_edge(node, c, color='blue')


        if isinstance(colors, dict):
            color_lut =  colors 
            colors = [ color_lut.get(node,'white') for node in graph]

        if colors == None:
            nc = DefaultNodeColors()
            colors = [nc.visit(v) for v in graph]
        
        elif isinstance( colors, ASTVisitorBase):
            colors = [colors.visit(v) for v in graph]


        if isinstance(labels, dict):
            for node in  graph.nodes_iter():
                if not node in labels:
                    labels[node] = repr(node)

        if labels == None:
            labels=dict( (s, repr(s)) for s in graph.nodes_iter( ) )

        graph_nodes = set(  graph.nodes_iter() )
        labels = dict([(k,v) for (k,v) in labels.items() if k in graph_nodes])


        f = plt.figure()
        nx.draw_graphviz(graph, font_size=10, iteration=200, node_color=colors,scale=1, labels=labels )

        ax = plt.gca()
        ax.text(0.5, 0.5, 'Hello')
        
        plt.show()



class ActionerGetConnections(ASTActionerDefault):

    def __init__(self, o):
        ASTActionerDefault.__init__(self, action_predicates=[SingleVisitPredicate()])
        self.connections = collections.defaultdict(list)
        self.visit(o)

    def get_connections(self):
        return self.connections

    def ActionAnalogReducePort(self, o, **kwargs):
        self.connections[o].extend(o.rhses)


    def ActionLibraryManager(self, o, **kwargs):
        self.connections[o].extend(o.libraries)
        self.connections[o].extend(o.components)
        self.connections[o].extend(o.interfaces)


    def ActionLibrary(self, o, **kwargs):
        self.connections[o].extend(o.functiondefs)
        self.connections[o].extend(o.symbolicconstants)


    def ActionNineMLComponent(self, o, **kwargs):
        self.connections[o].extend(o.assignments)
        self.connections[o].extend(o.timederivatives)
        self.connections[o].extend(o.functiondefs)
        self.connections[o].extend(o.symbolicconstants)
        self.connections[o].extend(o.transitions)
        self.connections[o].extend(list(o._event_port_connections) )
        self.connections[o].extend(list(o._interface_connectors) )


    def ActionRegime(self, o, **kwargs):
        pass
    def ActionRTGraph(self, o, **kwargs):
        pass
    def ActionOutEventPortParameter(self, o, **kwargs):
        pass
    def ActionEmitEventParameter(self, o, **kwargs):
        self.connections[o].extend([o.rhs, o.port_parameter_obj])
        
    def ActionOutEventPort(self, o, **kwargs):
        self.connections[o].extend( list(o.parameters))
        




    def ActionOnEvent(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].extend(o.actions)

    def ActionOnEventStateAssignment(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionIfThenElse(self, o, **kwargs):
        self.connections[o].append(o.predicate)
        self.connections[o].append(o.if_true_ast)
        self.connections[o].append(o.if_false_ast)

    def ActionInEquality(self, o, **kwargs):
        self.connections[o].append(o.less_than)
        self.connections[o].append(o.greater_than)

    def ActionBoolAnd(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionBoolOr(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionBoolNot(self, o, **kwargs):
        self.connections[o].append(o.lhs)

    def ActionFunctionDefUser(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].append(o.rhs)

    def ActionFunctionDefBuiltIn(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())

    def ActionFunctionDefParameter(self, o, **kwargs):
        pass

    def ActionStateVariable(self, o, **kwargs):
        pass

    def ActionSymbolicConstant(self, o, **kwargs):
        pass

    def ActionParameter(self, o, **kwargs):
        pass

    def ActionConstant(self, o, **kwargs):
        pass
    def ActionConstantZero(self, o, **kwargs):
        pass

    def ActionAssignedVariable(self, o, **kwargs):
        pass

    def ActionSuppliedValue(self, o, **kwargs):
        pass

    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs_map)

    def ActionRegimeDispatchMap(self, o, **kwargs):
        self.connections[o].extend(o.rhs_map.values())

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs_map)

    def ActionAddOp(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionSubOp(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionMulOp(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionDivOp(self, o, **kwargs):
        self.connections[o].append(o.lhs)
        self.connections[o].append(o.rhs)

    def ActionExpOp(self, o, **kwargs):
        self.connections[o].append(o.lhs)

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].append(o.function_def)
    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].append(o.function_def)

    def ActionFunctionDefInstantiationParater(self, o, **kwargs):
        self.connections[o].append(o.rhs_ast)

    def ActionOnTransitionTrigger(self, o, **kwargs):
        self.connections[o].append(o.trigger)
        self.connections[o].extend(o.actions)

    def ActionOnTransitionEvent(self, o, **kwargs):
        self.connections[o].extend(list(o.parameters))
        self.connections[o].extend(o.actions)

    def ActionOnEventDefParameter(self, o, **kwargs):
        pass

    def ActionEmitEvent(self, o, **kwargs):
        self.connections[o].extend(list(o.parameters))

    def ActionInEventPortParameter(self, o, **kwargs):
        pass
    def ActionInEventPort (self, o, **kwargs):
        self.connections[o].extend(list(o.parameters))

    def ActionEventPortConnection(self, o, **kwargs):
        self.connections[o].extend([o.src_port, o.dst_port])


    def ActionInterface(self, o, **kwargs):
        self.connections[o].extend(list(o.connections))

    def ActionCompoundPortConnectorWireMapping(self, o, **kwargs):
        self.connections[o].extend([o.interface_port, o.component_port])


    def ActionCompoundPortConnector(self, o, **kwargs):
        self.connections[o].extend([o.interface_def] + list(o.wire_mappings))

