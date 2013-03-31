
import networkx as nx
import matplotlib.pyplot as plt

from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate
from neurounits.visitors import ASTVisitorBase
from neurounits.ast_builder.eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.ast import OnEventStateAssignment
import itertools

import collections



class NodeColor(ASTVisitorBase):
    def VisitLibrary(self, o, **kwargs):
        return 'green'


    def visit(self, o):

        if isinstance(o, SymbolProxy):
            return 'red'
        if isinstance(o, OnEventStateAssignment):
            return 'orange'

        return 'blue'

        try:
            return ASTVisitorBase.visit(self, o)
        except NotImplementedError:
            return 'red'



class ActionerPlotNetworkX():
    def __init__(self, o):


        graph = nx.DiGraph()

        connections = ActionerGetConnections(o).get_connections()
        for node in connections.keys():
            graph.add_node(node, color='green')

        for node, connections in connections.items():
            for c in connections:
                graph.add_edge(node,c, color='blue')


        nc = NodeColor()
        node_color=[nc.visit(v) for v in graph]
        nx.draw_spring(graph, font_size=8, iteration=200, node_color=node_color,scale=2)
        #nx.draw_spectral(graph, font_size=8, iteration=200, node_color=node_color)

        plt.show()



class ActionerGetConnections(ASTActionerDefault):
    def __init__(self, o):
        ASTActionerDefault.__init__(self, action_predicates=[SingleVisitPredicate()])
        self.connections = collections.defaultdict(list)
        self.visit(o)

    def get_connections(self):
        return self.connections




    def ActionLibrary(self, o, **kwargs):
        self.connections[o].extend(o.functiondefs)
        self.connections[o].extend(o.symbolicconstants)

    def ActionEqnSet(self, o, **kwargs):
        self.connections[o].extend(o.assignments)
        self.connections[o].extend(o.timederivatives)
        self.connections[o].extend(o.functiondefs)
        self.connections[o].extend(o.symbolicconstants)
        self.connections[o].extend(o.onevents)

    def ActionNineMLComponent(self, o, **kwargs):
        self.connections[o].extend(o.assignments)
        self.connections[o].extend(o.timederivatives)
        self.connections[o].extend(o.functiondefs)
        self.connections[o].extend(o.symbolicconstants)
        self.connections[o].extend(o.onevents)
        self.connections[o].extend(o.transitions)

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

    # Function Definitions:
    def ActionFunctionDef(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].append(o.rhs)

    def ActionBuiltInFunction(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())

    def ActionFunctionDefParameter(self, o, **kwargs):
        pass

    # Terminals:
    def ActionStateVariable(self, o, **kwargs):
        pass
    def ActionSymbolicConstant(self, o, **kwargs):
        pass
    def ActionParameter(self, o, **kwargs):
        pass
    def ActionConstant(self, o, **kwargs):
        pass
    def ActionAssignedVariable(self, o, **kwargs):
        pass
    def ActionSuppliedValue(self, o, **kwargs):
        pass

    # AST Objects:
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

    def ActionFunctionDefInstantiation(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].append(o.function_def)

    def ActionFunctionDefInstantiationParater(self, o, **kwargs):
        self.connections[o].append(o.rhs_ast)



    def ActionOnTransitionTrigger(self, o, **kwargs):
        self.connections[o].append(o.trigger)
        self.connections[o].extend(o.actions)

    def ActionOnTransitionEvent(self, o, **kwargs):
        self.connections[o].extend(o.parameters.values())
        self.connections[o].extend(o.actions)

    def ActionOnEventDefParameter(self, o, **kwargs):
        pass

    def ActionEmitEvent(self, o, **kwargs):
        self.connections[o].extend(o.parameter_map.values())





