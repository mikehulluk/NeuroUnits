
from itertools import chain
from types import NoneType

from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault


def subnodes_on_obj(obj, recurse_builtins=True):
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
        ASTAllConnections().visit(n)



class ASTAllConnections(ASTActionerDepthFirst):

    def visit(self, obj):

        print 'Visiting:', obj
        nodes_told = obj.accept_visitor(self)
        nodes_found = nodes_on_obj(obj)

        if nodes_told is None:
            assert False, 'None found (told) %s'% obj
            
        if nodes_found is None:
            assert False, 'None found (found) %s'% obj

        print 'Nodes told', nodes_told
        print 'Nodes found', nodes_found

        

        # Ignore LibraryBuilder and LibraryManager

        from neurounits.librarymanager import LibraryManager
        from neurounits.ast_builder.eqnsetbuilder import LibraryBuilder
        from neurounits.units_backends.mh import MMUnit
        clses = (LibraryBuilder, LibraryManager, MMUnit)
        nodes_found = [n for n in nodes_found if not isinstance(n, clses)]

        nt = set(nodes_told) 
        nf = set(nodes_found)

        if nf != nt:
            print 'Found not told:'
            print nf-nt
            print 'Told not found:'
            print nt-nf
            assert False
        

    def VisitEqnSet(self, o, **kwargs):
        return [
            self._eqn_assignment.values(),
            self._function_defs.values(),
            self._eqn_time_derivatives.values(),
            self._symbolicconstants.values(),
            self._on_events.values() 
        ]

    def VisitIfThenElse(self, o, **kwargs):
        pass

    def VisitInEquality(self, o, **kwargs):
        pass

    def VisitBoolAnd(self, o, **kwargs):
        pass

    def VisitBoolOr(self, o, **kwargs):
        pass

    def VisitBoolNot(self, o, **kwargs):
        pass

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
        pass

    def VisitSymbolicConstant(self, o, **kwargs):
        pass

    def VisitParameter(self, o, **kwargs):
        pass

    def VisitConstant(self, o, **kwargs):
        pass

    def VisitAssignedVariable(self, o, **kwargs):
        pass

    def VisitSuppliedValue(self, o, **kwargs):
        pass

    def VisitAnalogReducePort(self, o, **kwargs):
        print 'self', self
        pass

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        pass

    def VisitRegimeDispatchMap(self, o, **kwargs):
        pass

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        pass

    def VisitAddOp(self, o, **kwargs):
        pass

    def VisitSubOp(self, o, **kwargs):
        pass

    def VisitMulOp(self, o, **kwargs):
        pass

    def VisitDivOp(self, o, **kwargs):
        pass

    def VisitExpOp(self, o, **kwargs):
        pass

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        return list(chain([o.function_def], o.parameters.values() ))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        return [o.rhs_ast, o._function_def_parameter]
        
    def VisitLibrary(self,o, **kwargs):
        return list(chain(
            o._eqn_assignment.values(),
            o._function_defs.values() ,
            o._symbolicconstants.values(),
        ))
        
    def VisitNineMLComponent(self, o, **kwargs):
        pass
    def VisitOnTransitionTrigger(self, o, **kwargs):
        pass
    def VisitOnTransitionEvent(self, o, **kwargs):
        pass



    def VisitOnEventStateAssignment(self, o, **kwargs):
        pass
