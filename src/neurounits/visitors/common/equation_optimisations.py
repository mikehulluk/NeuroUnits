




from neurounits import ast
from neurounits.visitors.common.ast_replace_node import ReplaceNode
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits.visitors.common.terminal_node_collector import EqnsetVisitorNodeCollector

from neurounits.visitors.bases.base_actioner  import ASTActionerDepthFirst
import operator

class OptimiseEquations(ASTVisitorBase):

    def __init__(self, component):
        self.component = component

        consts = ASTIsNodeConstant()
        consts.visit(component)

        rpl = ReplaceWithOptimisedNodes(component=component, constants=consts.const_value)



class ASTIsNodeConstant(ASTActionerDepthFirst):
    '''
    None - not constant
    Value? - some constant

    '''

    def __init__(self, component=None):
        self.const_value= {}
        super(ASTIsNodeConstant, self).__init__(component=component)

    def ActionNineMLComponent(self, component):
        pass


    def ActionRandomVariable(self,o,**kwargs):
        self.const_value[o] = None
    def ActionRandomVariableParameter(self, o, **kwargs):
        self.const_value[o] = self.const_value[o.rhs_ast]

    def ActionAutoRegressiveModel(self,o,**kwargs):
        self.const_value[o] = None

    def ActionFunctionDefUser(self, o, **kwargs):
        pass

    def ActionFunctionDefBuiltIn(self, o, **kwargs):
        pass

    def ActionFunctionDefParameter(self, o, **kwargs):
        pass

    def ActionStateVariable(self, o, **kwargs):
        self.const_value[o] = None

    def ActionSymbolicConstant(self, o, **kwargs):
        self.const_value[o] = o.value

    def ActionParameter(self, o, **kwargs):
        # Parameters are not 'constants' becase they can be different for 
        # each neuron in a population
        self.const_value[o] = None

    def ActionConstant(self, o, **kwargs):
        self.const_value[o] = o.value

    def ActionConstantZero(self, o, **kwargs):
        self.const_value[o] = 0

    def ActionAssignedVariable(self, o, **kwargs):
        # We should have already convert constant-assignments into Symbolic Constants
        self.const_value[o] = None

    def ActionSuppliedValue(self, o, **kwargs):
        self.const_value[o] = None

    def ActionTimeVariable(self, o, **kwargs):
        self.const_value[o] = None



    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        pass


    def ActionRegimeDispatchMap(self, o, **kwargs):
        assert len(o.rhs_map) == 1
        self.const_value[o] = self.const_value[ o.rhs_map.values()[0] ]


    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        # We shouldne't get const-value here, otherwise, we have a not properly reduced constants earlier!
        assert self.const_value[o.rhs_map] is None


    def _ActionBinOp(self, o, op):
        if self.const_value[o.lhs] is None or self.const_value[o.rhs] is None:
            self.const_value[o] = None
        else:
            self.const_value[o] = op( self.const_value[o.lhs] , self.const_value[o.rhs] )

    def ActionAddOp(self, o, **kwargs):
        self._ActionBinOp(o, operator.add)

    def ActionSubOp(self, o, **kwargs):
        self._ActionBinOp(o, operator.sub)

    def ActionMulOp(self, o, **kwargs):
        self._ActionBinOp(o, operator.mul)

    def ActionDivOp(self, o, **kwargs):
        self._ActionBinOp(o, operator.div)

    def ActionExpOp(self, o, **kwargs):
        assert False

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        assert o.function_def.funcname in ['__exp__','__ln__']

        # Are all of the parameters constants:
        for p in o.parameters.values():
            pres = self.visit(p.rhs_ast)
            if pres is None:
                self.const_value[o] = None
                return
        assert False, 'Optimisiation available if we reach here'


    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        assert False

    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        self.const_value[o] = self.const_value[o.rhs_ast]

    def ActionOnConditionTriggerTransition(self, o, **kwargs):
        pass # TODO: Optimisiations possible
        #assert False
    


    def ActionOnTransitionEvent(self, o, **kwargs):
        pass # TODO: Optimisiations possible

    def ActionOnEventDefParameter(self, o, **kwargs):
        self.const_value[o] = None
        

    def ActionEmitEvent(self, o, **kwargs):
        pass 


    def ActionOnEvent(self, o, **kwargs):
        pass # TODO: Optimisiations possible

    def ActionOnEventStateAssignment(self, o, **kwargs):
        pass # TODO: Optimisiations possible




    def ActionIfThenElse(self, o, **kwargs):
        self.const_value[o] = None
        pass # TODO: Optimisation here?


    def ActionRegime(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionAnalogVisitor(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionEmitEventParameter(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionMultiportInterfaceDef(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionOutEventPort(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionInEventPort(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionOutEventPortParameter(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionInEventPortParameter(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionRTGraph(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionEventPortConnection(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionMultiportInterfaceDefWireContinuous(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionMultiportInterfaceDefWireEvent(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionCompoundPortConnector(self, o,**kwargs):
        pass # TODO: Optimisation here?

    def ActionCompoundPortConnectorWireMapping(self, o,**kwargs):
        pass # TODO: Optimisation here?

    def ActionLibraryManager(self, o,**kwargs):
        pass # TODO: Optimisation here?

    def ActionLibrary(self, o, **kwargs):
        pass # TODO: Optimisation here?


    def ActionInEquality(self, o, **kwargs):
        pass # TODO: Optimisation here?
    def ActionOnConditionCrossing(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionBoolAnd(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionBoolOr(self, o, **kwargs):
        pass # TODO: Optimisation here?

    def ActionBoolNot(self, o, **kwargs):
        pass # TODO: Optimisation here?







class ReplaceWithOptimisedNodes(ASTVisitorBase):



    ## Division to multiplication if the RHS is a constant:
    #  ========================================================
    def should_replace_div_by_mul(self, o):
        if isinstance(o, ast.DivOp) and self.constants[o.rhs] is not None:
            return True
        return False

    def do_replace_div_by_mul(self, o):
        from neurounits.units_backends.mh import MMQuantity, MMUnit
        val = self.constants[o.rhs]
        new_node = ast.MulOp(
                lhs = o.lhs,
                rhs = ast.ConstValue( value = MMQuantity(1, MMUnit())/val )
                )
        new_node.set_dimension( o.get_dimension() )
        return new_node


    # Addition/Subtraction by zero can be dropped, (careful with lhs of sub!):
    def should_replace_addsub_zero(self, o):
        if not isinstance(o, (ast.AddOp, ast.SubOp)):
            return False

        br_lhs = self.constants[o.lhs]
        br_rhs = self.constants[o.rhs]
        if br_rhs is not None and br_rhs.magnitude == 0:
            return True

        if not isinstance(o, (ast.AddOp) ):
            return

        if br_lhs is not None and br_lhs.magnitude == 0:
            return True

        return False

    def do_replace_addsub_zero(self, o):
        br_lhs = self.constants[o.lhs]
        br_rhs = self.constants[o.rhs]

        if isinstance(o, ast.AddOp) and br_lhs is not None and br_lhs.magnitude == 0:
            return o.rhs
        if br_rhs is not None and br_rhs.magnitude == 0:
            return o.lhs
        assert False












    def __init__(self, component, constants):
        super(ReplaceWithOptimisedNodes,self).__init__()
        self.component = component
        self.constants = constants
        self.visit(component)


    def replace_or_visit(self, node):
        if self.should_replace_div_by_mul(node):
            return self.replace_or_visit( self.do_replace_div_by_mul(node) )
        if self.should_replace_addsub_zero(node):
            return self.replace_or_visit( self.do_replace_addsub_zero(node) )

        # No change?
        self.visit(node)
        return node


    def VisitNineMLComponent(self, o):
        for td in o.timederivatives:
            td.rhs_map = self.replace_or_visit(td.rhs_map)
        for ass in o.assignments:
            ass.rhs_map = self.replace_or_visit(ass.rhs_map)

        o._time_node = self.replace_or_visit(o._time_node)


    def VisitRegimeDispatchMap(self, o):
        o.rhs_map = { p: self.replace_or_visit(v) for (p,v) in o.rhs_map.items() }


    def _VisitBinOp(self, o):
        o.lhs = self.replace_or_visit(o.lhs)
        o.rhs = self.replace_or_visit(o.rhs)

    def VisitAddOp(self, o):
        self._VisitBinOp(o)
    def VisitSubOp(self, o):
        self._VisitBinOp(o)
    def VisitMulOp(self, o):
        self._VisitBinOp(o)
    def VisitDivOp(self, o):
        self._VisitBinOp(o)


    def VisitAssignedVariable(self, o):
        pass
    def VisitStateVariable(self,o ):
        pass
    def VisitConstant(self,o):
        pass
    def VisitConstantZero(self, o):
        pass
    def VisitSymbolicConstant(self, o ):
        pass
    def VisitSuppliedValue(self, o ):
        pass
    def VisitTimeVariable(self, o ):
        pass
    def VisitRandomVariable(self, o):
        pass
    def VisitAutoRegressiveModel(self, o):
        pass

    def VisitFunctionDefBuiltInInstantiation(self, o):
        for p in o.parameters.values():
            self.visit(p)

    def VisitFunctionDefInstantiationParameter(self, o):
        o.rhs_ast = self.replace_or_visit(o.rhs_ast)


    def VisitIfThenElse(self, o):
        pass

    def VisitParameter(self, o):
        pass

