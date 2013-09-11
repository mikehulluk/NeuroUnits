
from itertools import chain
from types import NoneType

from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault

from neurounits.units_misc import LookUpDict

def subnodes_on_obj(obj, recurse_builtins=True):
    if isinstance(obj, set):
        obj = list(obj)

    if isinstance(obj, LookUpDict):
        return list(obj._objs)

    if isinstance(obj, list):
        return list(chain(*[subnodes_on_obj(o) for o in obj]))
    if isinstance(obj, dict):
        ks = list(chain(*[subnodes_on_obj(k) for k in obj.keys()]))
        vs = list(chain(*[subnodes_on_obj(v) for v in obj.values()]))
        return ks + vs
    if isinstance(obj, (int, float, basestring, NoneType)):
        return []

    return [obj]

def nodes_on_obj(obj, recurse_builtins=True):
    vs = list(chain(*[subnodes_on_obj(v) for v in obj.__dict__.values()]))
    return vs




class ASTAllConnectionsCheck(ASTActionerDefault):
    def ActionNode(self,n):
        self.check_node(n)

    def check_node(self, obj, **kwargs):


        from neurounits.ast import Interface
        from neurounits.ast import EventPortConnection
        from neurounits.ast import RandomVariable
        if isinstance(obj, Interface):
            return
        if isinstance(obj, EventPortConnection):
            return
        if isinstance(obj, RandomVariable):
            # TODO - FIX this properly
            return


        connections = ASTAllConnections()

        nodes_told = obj.accept_visitor(connections)
        nodes_found = nodes_on_obj(obj)

        if nodes_told is None:
            print 'When visiting: %s' % obj
            assert False, 'None found (told) %s'% obj

        if nodes_found is None:
            print 'When visiting: %s' % obj
            assert False, 'None found (found) %s'% obj



        # Ignore LibraryBuilder and LibraryManager

        from neurounits.librarymanager import LibraryManager
        from neurounits.ast_builder.eqnsetbuilder import LibraryBuilder
        from neurounits.units_backends.mh import MMUnit, MMQuantity
        from neurounits.ast_builder.eqnsetbuilder import NineMLComponentBuilder
        from neurounits.ast_builder.eqnsetbuilder_io.io_str_parser import IODataDimensionSpec
        from neurounits.ast_builder.eqnsetbuilder_io.io_str_parser import IODataInitialCondition
        from neurounits.ast_annotations import ASTNodeAnnotationData, ASTTreeAnnotationManager
        clses = (LibraryBuilder, LibraryManager, MMUnit, MMQuantity, IODataDimensionSpec, IODataInitialCondition, NineMLComponentBuilder, ASTNodeAnnotationData, ASTTreeAnnotationManager)
        nodes_found = [n for n in nodes_found if not isinstance(n, clses)]

        nt = set(nodes_told)
        nf = set(nodes_found)

        if nf != nt:
            print 'ERROR!:'
            print '======='
            print 'Visiting:', obj
            print 'Found not told:'
            print nf-nt
            print 'Told not found:'
            print nt-nf
            assert False





class ASTAllConnections(ASTActionerDepthFirst):



    def VisitEventPortConnection(self, o, **kwargs):
        return [o.src_port, o.dst_port]


    def VisitLibrary(self,o, **kwargs):
        return list(chain(
            iter(o._eqn_assignment),
            iter(o._function_defs),
            iter(o._symbolicconstants),
        ))
    def VisitNineMLComponent(self, o, **kwargs):
        return list(chain(
            iter(o._eqn_assignment),
            iter(o._function_defs),
            iter(o._eqn_time_derivatives),
            iter(o._symbolicconstants),
            iter(o._transitions_triggers),
            iter(o._transitions_events),
            iter(o.rt_graphs),
            iter(o._interface_connectors),
            iter(o._event_port_connections),
            iter([o._time_node]),
        ))

    def VisitRegime(self, o, **kwargs):
        return [o.parent_rt_graph]
    def VisitRTGraph(self, o, **kwargs):
        return list(o.regimes)



    
    def VisitRandomVariable(self, o, **kwargs):
        return list(o.parameters)
    
    def VisitRandomVariableParameter(self, o, **kwargs):
        return [o.rhs_ast]




    def VisitIfThenElse(self, o, **kwargs):
        return [o.predicate, o.if_true_ast, o.if_false_ast]

    def VisitInEquality(self, o, **kwargs):
        return [o.lesser_than, o.greater_than]

    def VisitBoolAnd(self, o, **kwargs):
        return [o.lhs, o.rhs]

    def VisitBoolOr(self, o, **kwargs):
        return [o.lhs, o.rhs]

    def VisitBoolNot(self, o, **kwargs):
        return [o.lhs]

    def VisitFunctionDefUser(self, o, **kwargs):
        return list(chain(
            o.parameters.values(),
            [o.rhs]
            ))


    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        return o.parameters.values()

    def VisitFunctionDefParameter(self, o, **kwargs):
        return []

    def VisitStateVariable(self, o, **kwargs):
        if o.initial_value:
            return [o.initial_value]
        return []

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    def VisitParameter(self, o, **kwargs):
        return []

    def VisitConstant(self, o, **kwargs):
        return []
    def VisitConstantZero(self, o, **kwargs):
        return []

    def VisitAssignedVariable(self, o, **kwargs):
        return []

    def VisitSuppliedValue(self, o, **kwargs):
        return []
    def VisitTimeVariable(self, o, **kwargs):
        return []

    def VisitAnalogReducePort(self, o, **kwargs):
        return o.rhses

    def VisitRegimeDispatchMap(self, o, **kwargs):
        return list(o.rhs_map.keys()) + list( o.rhs_map.values() )

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        return [o.lhs, o.rhs_map]

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return [o.lhs, o.rhs_map]

    def VisitAddOp(self, o, **kwargs):
        return [o.lhs, o.rhs]

    def VisitSubOp(self, o, **kwargs):
        return [o.lhs, o.rhs]


    def VisitMulOp(self, o, **kwargs):
        return [o.lhs, o.rhs]


    def VisitDivOp(self, o, **kwargs):
        return [o.lhs, o.rhs]


    def VisitExpOp(self, o, **kwargs):
        assert isinstance( o.rhs, (float,int) )
        return [o.lhs]


    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        return list(chain([o.function_def], o.parameters.values() ))
    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return list(chain([o.function_def], o.parameters.values() ))

    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        return [o.rhs_ast, o._function_def_parameter]

    def VisitOnTransitionTrigger(self, o, **kwargs):
        return [o.trigger, o.src_regime, o.target_regime ] + list(o.actions)

    def VisitOnTransitionEvent(self, o, **kwargs):
        return [ o.src_regime, o.target_regime, o.port] + list(o.actions) + list(o.parameters)



    def VisitOnEventStateAssignment(self, o, **kwargs):
        return [o.lhs, o.rhs]


    def VisitInEventPort(self, o, **kwargs):
        return list(o.parameters)
    def VisitInEventPortParameter(self, o, **kwargs):
        return []

    def VisitOutEventPort(self, o, **kwargs):
        return list(o.parameters)
    def VisitOutEventPortParameter(self, o, **kwargs):
        return []


    def VisitEmitEventParameter(self, o, **kwargs):
        return [o.rhs, o.port_parameter_obj]
    def VisitEmitEvent(self, o, **kwargs):
        return [o.port] + list(o.parameters)

    def VisitOnEventDefParameter(self, o, **kwargs):
        return []


    def VisitCompoundPortConnectorWireMapping(self, o, **kwargs):
        return [o.interface_port, o.component_port]

    def VisitInterface(self, o, **kwargs):
        return list(o.connections)

    def VisitCompoundPortConnector(self, o, **kwargs):
        return list(o.wire_mappings) + [o.interface_def]





