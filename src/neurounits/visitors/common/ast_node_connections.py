
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
        connections = ASTAllConnections()

        #print 
        #print
        #print 'Visiting:', obj
        nodes_told = obj.accept_visitor(connections)
        nodes_found = nodes_on_obj(obj)

        if nodes_told is None:
            assert False, 'None found (told) %s'% obj

        if nodes_found is None:
            assert False, 'None found (found) %s'% obj

        #print 'Nodes told', nodes_told
        #print 'Nodes found', nodes_found



        # Ignore LibraryBuilder and LibraryManager

        from neurounits.librarymanager import LibraryManager
        from neurounits.ast_builder.eqnsetbuilder import LibraryBuilder
        from neurounits.units_backends.mh import MMUnit, MMQuantity
        from neurounits.ast_builder.eqnsetbuilder import NineMLComponentBuilder
        from neurounits.ast_builder.eqnsetbuilder_io.io_str_parser import IODataDimensionSpec
        clses = (LibraryBuilder, LibraryManager, MMUnit, MMQuantity, IODataDimensionSpec, NineMLComponentBuilder)
        nodes_found = [n for n in nodes_found if not isinstance(n, clses)]

        nt = set(nodes_told)
        nf = set(nodes_found)

        if nf != nt:
            print 'Visiting:', obj
            print 'Found not told:'
            print nf-nt
            print 'Told not found:'
            print nt-nf
            assert False


    


class ASTAllConnections(ASTActionerDepthFirst):


    def VisitEqnSet(self, o, **kwargs):
        assert False
        return [
            o._eqn_assignment.values(),
            o._function_defs.values(),
            o._eqn_time_derivatives.values(),
            o._symbolicconstants.values(),
        ]

    def VisitLibrary(self,o, **kwargs):
        #assert False
        return list(chain(
            iter(o._eqn_assignment),
            iter(o._function_defs),
            #iter(o._eqn_time_derivatives),
            iter(o._symbolicconstants),
            #o._eqn_assignment.values(),
            #o._function_defs.values() ,
            #o._symbolicconstants.values(),
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
        ))

    def VisitRegime(self, o, **kwargs):
        return [o.parent_rt_graph]
    def VisitRTGraph(self, o, **kwargs):
        return list(o.regimes)



    def VisitIfThenElse(self, o, **kwargs):
        return [o.predicate, o.if_true_ast, o.if_false_ast]

    def VisitInEquality(self, o, **kwargs):
        return [o.less_than, o.greater_than]

    def VisitBoolAnd(self, o, **kwargs):
        return [o.lhs, o.rhs]

    def VisitBoolOr(self, o, **kwargs):
        return [o.lhs, o.rhs]

    def VisitBoolNot(self, o, **kwargs):
        return [o.lhs]

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        return list(chain(
            o.parameters.values(),
            [o.rhs]
            ))


    def VisitBuiltInFunction(self, o, **kwargs):
        return o.parameters.values()

    def VisitFunctionDefParameter(self, o, **kwargs):
        return []

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return []

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    def VisitParameter(self, o, **kwargs):
        return []

    def VisitConstant(self, o, **kwargs):
        return []

    def VisitAssignedVariable(self, o, **kwargs):
        return []

    def VisitSuppliedValue(self, o, **kwargs):
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


    def VisitFunctionDefInstantiation(self, o, **kwargs):
        return list(chain([o.function_def], o.parameters.values() ))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
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

