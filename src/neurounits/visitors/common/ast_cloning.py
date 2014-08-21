


import neurounits.ast as  ast

def copy_std(old, new):
    assert type(old) == type(new)
    if '_dimension' in old.__dict__:
        shallow_copy(old, new, what=['_dimension'])
    if '_metadata' in old.__dict__:
        shallow_copy(old, new, what=['_metadata'])

    assert set(old.__dict__.keys()) == set(old.__dict__.keys())
    return new

def shallow_copy(old, new, what):
    for var_name in what:
        assert var_name in old.__dict__
        assert not var_name in new.__dict__ or new.__dict__[var_name] is None or new.__dict__[var_name]==old.__dict__[var_name], 'Variable already set on: %s.%s as %s' %(new, var_name, getattr(new,var_name))
        new.__dict__[var_name] = old.__dict__[var_name]
    return new





class BuildDataDummy(object):
    pass

class ASTClone(object):



    def clone_root(self, obj):
        from ast_replace_node import ReplaceNode

        new_obj = None
        # Replace the nodes one at a time (set to prevent duplicates:
        for old_node in set(obj.all_ast_nodes()):
            new_node = ASTClone().visit(old_node)
            if old_node == obj:
                new_obj = new_node
            ReplaceNode.replace_and_check(srcObj=old_node, dstObj=new_node, root = obj)


        assert new_obj is not None
        return new_obj




    def visit(self, o, **kwargs):
        return o.accept_visitor(self, **kwargs)


    def VisitRTGraph(self, o, **kwargs):
        new = ast.RTBlock(name = o.name)
        new.regimes = o.regimes.copy()
        if o.default_regime:
            new.default_regime = new.get_regime(name=o.default_regime.name)
            assert new.default_regime in new.regimes
        return new

    def VisitRegime(self, o, **kwargs):
        new = ast.Regime(name=o.name, parent_rt_graph = o.parent_rt_graph)
        return new





    def VisitNineMLComponent(self, o, **kwargs):
        builddata = BuildDataDummy()


        builddata.transitions_conditiontriggers = o._transitions_conditiontriggers.copy()
        builddata.transitions_events =  o._transitions_events.copy()
        builddata.rt_graphs = o.rt_graphs.copy()

        # Top-level objects:
        builddata.assignments = o._eqn_assignment.copy()
        builddata.funcdefs = o._function_defs.copy()
        builddata.timederivatives = o._eqn_time_derivatives.copy()
        builddata.symbolicconstants = o._symbolicconstants.copy()
        builddata.component_name = o.name
        builddata.time_node = o._time_node

        new = ast.NineMLComponent(
                library_manager=o.library_manager,
                builder=None,
                builddata=builddata,
                name = o.name
                )

        new._event_port_connections = o._event_port_connections.copy()
        new._interface_connectors = o._interface_connectors.copy()
        return copy_std(o, new, )





    def VisitSymbolicConstant(self, o, **kwargs):
        new = ast.SymbolicConstant(
                symbol = o.symbol,
                value = o.value)
        return copy_std(o, new, )


    def VisitFunctionDefUser(self, o, **kwargs):
        new = ast.FunctionDefUser(
                funcname=o.funcname,
                parameters=o.parameters.copy(),
                rhs = o.rhs
                )
        return copy_std(o, new, )

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        new = ast.FunctionDefBuiltIn(
                funcname = o.funcname,
                parameters= o.parameters,
                )
        return copy_std(o, new, )

    def VisitFunctionDefParameter(self, o, **kwargs):
        new = ast.FunctionDefParameter(
                symbol=o.symbol
                )
        return copy_std(o, new, )

    def VisitStateVariable(self, o, **kwargs):
        new = ast.StateVariable(
                symbol=o.symbol
                )
        new.initial_value = o.initial_value
        return copy_std(o, new, )

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        new = ast.EqnTimeDerivativeByRegime(
                lhs = o.lhs,
                rhs_map = o.rhs_map,
                )
        return copy_std(o, new, )

    def VisitRegimeDispatchMap(self, o, **kwargs):
        new = ast.EqnRegimeDispatchMap(
                rhs_map = o.rhs_map.copy()
                )
        return copy_std(o, new, )

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        new = ast.EqnAssignmentByRegime(
                lhs = o.lhs,
                rhs_map = o.rhs_map,
                )
        return copy_std(o, new, )


    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        new =  ast.FunctionDefBuiltInInstantiation(
                function_def = o.function_def,
                parameters = o.parameters.copy()
                )
        return copy_std(o, new, )

    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        new =  ast.FunctionDefUserInstantiation(
                function_def = o.function_def,
                parameters = o.parameters.copy()
                )
        return copy_std(o, new, )


    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        new =  ast.FunctionDefParameterInstantiation(
                    symbol = o.symbol,
                    rhs_ast = o.rhs_ast,
                    function_def_parameter = o._function_def_parameter

                )
        return copy_std(o, new, )


    def VisitOnEvent(self, o, **kwargs):
        assert False
        raise NotImplementedError()

    def VisitOnEventStateAssignment(self, o, **kwargs):
        new = ast.OnEventStateAssignment(lhs = o.lhs, rhs=o.rhs)
        return copy_std(o, new, )

    def VisitIfThenElse(self, o, **kwargs):
        new = ast.IfThenElse(
                predicate=o.predicate,
                if_true_ast=o.if_true_ast,
                if_false_ast=o.if_false_ast,)
        return copy_std(o, new, )

    def VisitInEquality(self, o, **kwargs):
        new = ast.InEquality(
                lesser_than=o.lesser_than,
                greater_than=o.greater_than
                )
        return copy_std(o, new, )

    def VisitBoolAnd(self, o, **kwargs):
        new = ast.BoolAnd(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitBoolOr(self, o, **kwargs):
        new = ast.BoolOr(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitBoolNot(self, o, **kwargs):
        new = ast.BoolOr(lhs = o.lhs)
        return copy_std(o, new, )

    def VisitParameter(self, o, **kwargs):
        new = ast.Parameter(symbol = o.symbol)
        return copy_std(o, new, )

    def VisitConstant(self, o, **kwargs):
        new = ast.ConstValue(value = o.value)
        return copy_std(o, new, )

    def VisitConstantZero(self, o, **kwargs):
        new = ast.ConstValueZero()
        return copy_std(o, new, )

    def VisitAssignedVariable(self, o, **kwargs):
        new = ast.AssignedVariable(symbol = o.symbol)
        return copy_std(o, new, )

    def VisitSuppliedValue(self, o, **kwargs):
        new = ast.SuppliedValue(symbol = o.symbol)
        return copy_std(o, new, )

    def VisitTimeVariable(self, o, **kwargs):
        new = ast.TimeVariable(symbol = o.symbol)
        return copy_std(o, new, )


    def VisitAddOp(self, o, **kwargs):
        new = ast.AddOp(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitSubOp(self, o, **kwargs):
        new = ast.SubOp(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitMulOp(self, o, **kwargs):
        new = ast.MulOp(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitDivOp(self, o, **kwargs):
        new = ast.DivOp(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )

    def VisitExpOp(self, o, **kwargs):
        new = ast.ExpOp(
                lhs = o.lhs,
                rhs = o.rhs, )
        return copy_std(o, new, )



    def VisitOnConditionTriggerTransition(self, o, **kwargs):
        new = ast.OnConditionTriggerTransition(
                src_regime = o.src_regime,
                target_regime = o.target_regime,
                actions = o.actions[:],
                trigger = o.trigger
                )
        return copy_std(o, new, )
    def VisitOnTransitionEvent(self, o, **kwargs):
        new = ast.OnEventTransition(
                src_regime = o.src_regime,
                target_regime = o.target_regime,
                actions = o.actions[:],
                port = o.port,
                parameters = o.parameters.copy()
                )
        return copy_std(o, new, )


    def VisitAnalogReducePort(self, o, **kwagrs):
        return ast.AnalogReducePort(
                symbol = o.symbol,
                rhses = list(o.rhses)
                )

    def VisitEmitEventParameter(self, o, **kwargs):
        return ast.EmitEventParameter(
                _symbol='(from_clone)',
                rhs= o.rhs,
                port_parameter_obj=o.port_parameter_obj)

    def VisitOutEventPortParameter(self, o, **kwargs):
        return ast.OutEventPortParameter(symbol = o.symbol)

    def VisitOutEventPort(self, o, **kwargs):
        return ast.OutEventPort(
                symbol = o.symbol,
                parameters = o.parameters.copy()
                )
    def VisitEmitEvent(self, o, **kwargs):
        return ast.EmitEvent(
                port = o.port,
                parameters = o.parameters.copy()
                )

    def VisitInEventPort(self,o, **kwargs):
        return ast.InEventPort(
                symbol = o.symbol,
                parameters = o.parameters.copy()
                )

    def VisitInEventPortParameter(self, o, **kwargs):
        return ast.InEventPortParameter(
                symbol = o.symbol
                )

    def VisitOnEventDefParameter(self, o, **kwargs):
        return ast.OnEventDefParameter(
                symbol = o.symbol,
                dimension = o.get_dimension()
                )


    def VisitCompoundPortConnector(self, o, **kwaargs):
        return ast.CompoundPortConnector(
                symbol = o.symbol,
                interface_def = o.interface_def,
                wire_mappings = o.wire_mappings.copy(),
                direction = o.direction
                )

    def VisitCompoundPortConnectorWireMapping(self, o, **kwargs):
        return ast.CompoundPortConnectorWireMapping(
                component_port = o.component_port,
                interface_port =  o.interface_port,
                )

    def VisitEventPortConnection(self, o, **kwargs ):
        assert o.delay is None
        return ast.EventPortConnection(
            dst_port = o.dst_port,
            src_port = o.src_port,
        )






