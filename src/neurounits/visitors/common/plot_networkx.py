
import networkx as nx
import matplotlib.pyplot as plt

from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate
from neurounits.visitors import ASTVisitorBase
from neurounits.ast_builder.eqnsetbuilder_symbol_proxy import SymbolProxy
from neurounits.ast import OnEventStateAssignment
import neurounits.ast as ast
import itertools
import neurounits

import inspect
import collections


def inheritors(klass):
    subclasses = set()
    work = [klass]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return subclasses


pastels = [	
    "#F7977A",
    "#F9AD81",
    "#FDC68A",
    "#FFF79A",
    "#C4DF9B",
    "#A2D39C",
    "#82CA9D",
    "#7BCDC8",
    "#6ECFF6",
    "#7EA7D8",
    "#8493CA",
    "#8882BE",
    "#A187BE",
    "#BC8DBF",
    "#F49AC2",
    "#F6989D",
]





class TypeBasedLookupDict(object):
    def __init__(self, data):
        self._data = data


    def __getitem__(self, k):

        # Are we passed in type or object:
        if type(k) != type:
            k = type(k)


        parents = inspect.getmro(k)
        
        for p in parents:
            if p in self._data:
                return self._data[p]
        
        assert False, 'Unable to find suitable entry for: %s'%k






class DefaultNodeColors(ASTActionerDefault):
    def ActionNode(self, o, **kwargs):


        class_colors= TypeBasedLookupDict( {
            ast.IfThenElse: 'blue',
            ast.ASTBooleanExpression: 'blue',
            ast.InEquality: 'blue',
            ast.OnConditionCrossing: 'blue',
            ast.BoolAnd: pastels[3],
            ast.BoolOr: pastels[3],
            ast.BoolNot: pastels[3],

            ast.ASTSymbolNode: pastels[1],
            ast.ASTConstNode: pastels[2],
            ast.FunctionDefBuiltIn: 'blue',
            ast.FunctionDefUser: 'blue',
            ast.FunctionDefParameter: 'blue',
            ast.FunctionDefUserInstantiation: 'blue',
            ast.FunctionDefBuiltInInstantiation: 'blue',
            ast.FunctionDefParameterInstantiation: 'blue',

            ast.BinaryOp: pastels[0],

            ast.OnConditionTriggerTransition: 'blue',
            ast.OnEventTransition: pastels[8],
            ast.OnEventDefParameter: 'blue',
            ast.EmitEvent: 'blue',
            ast.EmitEventParameter: 'blue',
            ast.OnEventStateAssignment: pastels[7],
            ast.Regime: 'blue',
            ast.RTBlock: 'blue',
            ast.EqnTimeDerivativePerRegime: 'blue',
            ast.EqnAssignmentPerRegime: 'blue',
            ast.AnalogReducePort: 'blue',
            ast.InEventPort: pastels[6],
            ast.EqnAssignmentByRegime: pastels[4],
            ast.EqnTimeDerivativeByRegime: pastels[5],
            ast.EqnRegimeDispatchMap: 'blue',
            ast.Transition: 'blue',
            ast.InEventPortParameter: 'blue',
            ast.OutEventPort: 'blue',
            ast.OutEventPortParameter: 'blue',
            ast.EventPortConnection: 'blue',
            ast.Library: 'blue',
            ast.InterfaceWire: 'blue',
            ast.NineMLComponent: 'blue',
            ast.InterfaceWireContinuous: 'blue',
            ast.InterfaceWireEvent: 'blue',
            ast.Interface: 'blue',
            ast.CompoundPortConnectorWireMapping: 'blue',
            ast.CompoundPortConnector: 'blue',
            ast.RandomVariable: 'blue',
            ast.RandomVariableParameter: 'blue',
            ast.AutoRegressiveModel: 'blue',
            neurounits.LibraryManager: 'blue',
            })

        return class_colors[type(o)]
        



class DefaultNodeLabels(ASTActionerDefault):
    def ActionNode(self, n, **kwargs):
        return n.summarise_node_short()







class ActionerPlotNetworkX(object):
    def __init__(self, o, labels = None, colors=None, include_types=None, exclude_connections=None, figure=None):

        ast_types = inheritors(ast.ASTObject)
        if include_types is None:
            include_types = ast_types

        if not exclude_connections:
            exclude_connections=set()
        for ex in exclude_connections:
            assert isinstance(ex, set) 
            assert len(ex) == 2
            assert (list(ex)[0]) in ast_types
            assert (list(ex)[1]) in ast_types



        graph = nx.DiGraph()

        connections = ActionerGetConnections(o).get_connections()
        for node in connections.keys():
            if type(node) in include_types:
                graph.add_node(node, color='green', label='"%s"' % node.summarise_node_short(), penwidth=0.00001 )

        for (node, connections) in connections.items():
            for c in connections:
                if type(node) in include_types and \
                   type(c) in include_types and \
                   set([type(node),type(c)]) not in exclude_connections:
                    graph.add_edge(node, c, color='blue')


        # Colors:
        if isinstance(colors, dict):
            color_lut =  colors
            colors = [ color_lut.get(node,'white') for node in graph]

        if colors == None:
            nc = DefaultNodeColors()
            colors = [nc.visit(v) for v in graph]

        elif isinstance( colors, ASTVisitorBase):
            colors = [colors.visit(v) for v in graph]


        # Labelling:
        label_dict = {}
        default_labeller = DefaultNodeLabels()
        for node in graph.nodes_iter():
            node_label = None

            # Try to subscript the object:
            if isinstance(labels, dict):
                try:
                    node_label = labels[node]
                except KeyError:
                    pass

            # Try to call the object:
            if not node_label:
                try:
                    node_label = labels(node)
                except TypeError:
                    pass

            # Try to 'visit' the object:
            if not node_label and isinstance(labels, ASTVisitorBase):
                node_label = labels.visit(node)

            # OK, apply the default label:
            if node_label is None:
                node_label = default_labeller.visit(node)


            label_dict[node] = node_label





        print 'Plotting!'
        if not figure:
            plt.figure()
        nx.draw_graphviz(graph, font_size=8, iteration=200, node_color=colors, penwidth=0.001, scale=1, labels=label_dict )

        #ax = plt.gca()

        #plt.show()



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
        self.connections[o].append(o.lesser_than)
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
    def ActionTimeVariable(self, o, **kwargs):
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

    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        self.connections[o].append(o.rhs_ast)

    def ActionOnConditionTriggerTransition(self, o, **kwargs):
        self.connections[o].append(o.trigger)
        self.connections[o].extend(o.actions)

    def ActionOnConditionCrossing(self, o, **kwargs):
        self.connections[o].append(o.crosses_lhs)
        self.connections[o].append(o.crosses_rhs)


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

    def ActionRandomVariable(self, o, **kwargs):
        self.connections[o].extend( o.parameters)

    def ActionRandomVariableParameter(self, o, **kwargs):
        self.connections[o].append( o.rhs_ast)
