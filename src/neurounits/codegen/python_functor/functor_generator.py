#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------




from neurounits.visitors import ASTVisitorBase
import numpy as np
from neurounits import ast
from neurounits.units_backends.mh import MHUnitBackend
from collections import defaultdict
from neurounits.misc import SeqUtils

from neurounits.units_backends.mh import MMQuantity, MMUnit







def with_number_check(func, src_obj):
    return func

    def my_func(*args, **kwargs):

        res = func(*args, **kwargs)
        print 'Value of node:', repr(src_obj), res
        return res
    return my_func



class FunctorGenerator(ASTVisitorBase):

    def __init__(self, component=None, as_float_in_si=False, fully_calculate_assignments=True):
        self.ast = None

        self.fully_calculate_assignments = fully_calculate_assignments

        self.assignment_evaluators = {}
        self.timederivative_evaluators = {}

        self.as_float_in_si = as_float_in_si

        if component is not None:
            assert isinstance(component, ast.NineMLComponent)
            self.visit(component)


    def VisitNineMLComponent(self, o, **kwargs):
        self.ast = o

        for ass in o.ordered_assignments_by_dependancies:
            self.visit(ass)

        for a in o.timederivatives:
            self.visit(a)

        # Build a dictionary of predicates which detect whether a
        # trigger is valid
        self.transition_triggers_evals = {}
        self.transitions_actions = {}
        self.transition_event_forwarding = defaultdict(list)
        self.transition_port_handlers = defaultdict(list)

        for conn in o._event_port_connections:
            self.visit(conn)

        for tr in o.transitions:
            self.visit(tr)




    def VisitOnEventStateAssignment(self, o, **kwargs):

        rhs = self.visit(o.rhs)

        def f1(state_data, **kw):
            sv_name = o.lhs.symbol
            new_value = rhs(state_data=state_data, **kw)
            state_data.states_out[sv_name] = new_value
        return f1



    def _visit_trans(self, o, **kwargs):
        callable_actions = [self.visit(a) for a in o.actions]

        def f2(state_data, **kw):
            # Do the effects:
            for c in callable_actions:
                c(state_data=state_data, **kw)
        return f2

    def VisitOnConditionTriggerTransition(self, o, **kwargs):
        # Trigger predicate functor:
        self.transition_triggers_evals[o] = self.visit(o.trigger, **kwargs)

        # Action functor:
        self.transitions_actions[o] = self._visit_trans(o, **kwargs)

    def VisitOnTransitionEvent(self, o, **kwargs):
        self.transition_port_handlers[o.port].append(o )
        self.transitions_actions[o] = self._visit_trans(o, **kwargs)

    def VisitOnEventDefParameter(self, o):
        def f(evt, **kw):
            # Single parameter:
            if len(evt.parameter_values)==1:
                return list(evt.parameter_values.values() )[0]
            # Resolve from among many parameters:
            else:
                return evt.parameter_values[o.port_parameter_obj.symbol]

        return f


    def VisitEventPortConnection(self, o):
        self.transition_event_forwarding[o.src_port].append(o.dst_port)





    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        self.assignment_evaluators[o.lhs.symbol] = self.visit(o.rhs_map)

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        self.timederivative_evaluators[o.lhs.symbol] = self.visit(o.rhs_map)



    def VisitRegimeDispatchMap(self,o,**kwargs):

        rt_graph = o.get_rt_graph()

        rhs_functors = dict([(regime, self.visit(rhs)) for (regime,rhs) in o.rhs_map.items()])

        try:
            default = SeqUtils.filter_expect_single(rhs_functors.keys(), lambda r:r.name == None)
            assert not None in rhs_functors
            rhs_functors[None] = rhs_functors[default]
        except ValueError:
            pass


        def f3(state_data, **kw):
            regime_states = state_data.rt_regimes

            curr_state = regime_states[rt_graph]
            if curr_state in rhs_functors:
                rhs_functor = rhs_functors[curr_state]
            else:
                rhs_functor = rhs_functors[None]

            return rhs_functor(state_data=state_data, **kw)

        return f3



    def VisitIfThenElse(self, o, **kwargs):
        fpred = self.visit(o.predicate)
        ftrue = self.visit(o.if_true_ast)
        ffalse = self.visit(o.if_false_ast)

        def f4(**kw):
            if fpred(**kw):
                return ftrue(**kw)
            else:
                return ffalse(**kw)
        return f4


    def VisitInEquality(self, o , **kwargs):
        lt = self.visit(o.lesser_than )
        gt = self.visit(o.greater_than )
        def f5(**kw):
            lhs = lt(**kw)
            rhs = gt(**kw)
            return lhs < rhs
        return f5

    def VisitBoolAnd(self, o, **kwargs):
        s1 = self.visit(o.lhs)
        s2 = self.visit(o.rhs)

        def f(**kw):
            return s1(**kw) and s2(**kw)

        return f

    def VisitBoolOr(self, o, **kwargs):
        s1 = self.visit(o.lhs)
        s2 = self.visit(o.rhs)

        def f(**kw):
            return s1(**kw) or s2(**kw)
        return f

    def VisitBoolNot(self, o, **kwargs):
        s1 = self.visit(o.lhs)

        def f(**kw):
            return not s1(**kw)
        return f

    def VisitFunctionDefBuiltIn(self, o, **kwargs):
        return o.accept_func_visitor(self, **kwargs)



    def VisitBIFSingleArg(self, o, functor):
        if not self.as_float_in_si:
            def eFunc(state_data, func_params, **kw):
                assert len(func_params) == 1
                ParsingBackend = MHUnitBackend
                return ParsingBackend.Quantity(float(functor((func_params.values()[0] ).dimensionless())), ParsingBackend.Unit() )
        else:
            def eFunc(state_data, func_params, **kw):
                assert len(kw) == 1
                return float(functor(kw.values()[0]))
        return eFunc

    # ============
    def VisitBIFsin(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.sin)
    def VisitBIFcos(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.cos)
    def VisitBIFtan(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.tan)

    def VisitBIFsinh(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.sinh)
    def VisitBIFcosh(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.cosh)
    def VisitBIFtanh(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.tanh)

    def VisitBIFasin(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.arcsin)
    def VisitBIFacos(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.arccos)
    def VisitBIFatan(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.arctan)

    def VisitBIFexp(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.exp)

    def VisitBIFceil(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.ceil)
    def VisitBIFfloor(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.ceil)
    def VisitBIFsqrt(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.sqrt)
    def VisitBIFfabs(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.fabs)

    def VisitBIFln(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.log)
    def VisitBIFlog2(self, o):
        return self.VisitBIFSingleArg(o=o,functor=np.log2)
    def VisitBIFlog10(self, o):
        return self.VisitBIFSingleArg(o=o, functor=np.log10)
    # ==================


    def _VisitBIF2arg(self, o, functor, arg_names):
        if not self.as_float_in_si:
            def eFunc(state_data, func_params, **kw):
                assert len(func_params) == 2
                ParsingBackend = MHUnitBackend
                return ParsingBackend.Quantity(float(functor(
                        (func_params[arg_names[0]] ).dimensionless() ,
                        (func_params[arg_names[1]] ).dimensionless()) ), ParsingBackend.Unit() )
        else:
            def eFunc(state_data, func_params, **kw):
                assert len(kw) == 2
                return float(functor(kw[arg_names[0]], kw[ arg_names[1] ]))

        return eFunc

    def VisitBIFpow(self, o, ):
        return self._VisitBIF2arg(o=o, arg_names=('base','exp'), functor=np.power )
    def VisitBIFmin(self, o, ):
        return self._VisitBIF2arg(o=o, arg_names=('x','y'), functor=np.min )
    def VisitBIFmax(self, o, ):
        return self._VisitBIF2arg(o=o, arg_names=('x','y'), functor=np.max )
    def VisitBIFatan2(self, o, ):
        return self._VisitBIF2arg(o=o, arg_names=('y', 'x'), functor=np.arctan2 )








    def VisitSymbolicConstant(self, o, **kwargs):
        if not self.as_float_in_si:

            def eFunc(**kw):
                return o.value

            return eFunc
        else:

            def eFunc(**kw):
                return o.value.float_in_si()

            return eFunc

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):

        if not self.as_float_in_si:
            def eFunc2(state_data, **kw):
                v = state_data.states_in[o.symbol]
                assert o.get_dimension().is_compatible(v.get_units())
                return v
        else:
            def eFunc2(state_data, **kw):
                v = state_data.states_in[o.symbol]
                return v


        return with_number_check(eFunc2, o )

    def VisitParameter(self, o, **kwargs):
        def eFunc(state_data, **kw):

            v= state_data.parameters[o.symbol]
            assert o.get_dimension().is_compatible(v.get_units()), 'Param Units Err: %s [Expected:%s Found:%s]'%(o.symbol, o.get_dimension(), v.get_units())
            return v

        return eFunc

    def VisitConstant(self, o, **kwargs):
        if not self.as_float_in_si:

            def eFunc(**kw):
                return o.value
            return eFunc
        else:
            def eFunc(**kw):
                return o.value.float_in_si()
            return eFunc

    def VisitConstantZero(self, o, **kwargs):
        if not self.as_float_in_si:
            def eFunc(**kw):
                return MMQuantity(0 , o.get_dimension() )
            return eFunc
        else:
            def eFunc(**kw):
                return 0
            return eFunc



    def VisitSuppliedValue(self, o, **kwargs):
        def eFunc(state_data, **kw):
            v = state_data.suppliedvalues[o.symbol]
            return v
        return eFunc

    def VisitTimeVariable(self, o, **kwargs):
        def eFunc(state_data, **kw):
            v = state_data.suppliedvalues[o.symbol]
            return v
        return eFunc


    def VisitAssignedVariable(self, o, **kwargs):
        # We are at an assignment. We resolve this by looking up the
        # Right hand side of the assigned variable:
        if self.fully_calculate_assignments:
            assignment_rhs = self.assignment_evaluators[o.symbol]
            def eFunc(**kw):
                res = assignment_rhs(**kw)
                return res
            return with_number_check(eFunc, o)

        else:
            def eFunc(state_data, **kw):
                v = state_data.assignedvalues[o.symbol]
                return v
            return eFunc

    def VisitAddOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            res = f_lhs(**kw) + f_rhs(**kw)
            return res
        return with_number_check(eFunc,o)

    def VisitSubOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            v_l = f_lhs(**kw)
            v_r = f_rhs(**kw)
            return v_l-v_r
        return with_number_check(eFunc, o)

    def VisitMulOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_lhs(**kw) * f_rhs(**kw)
        return with_number_check(eFunc, o)

    def VisitDivOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            v_l = f_lhs(**kw)
            v_r = f_rhs(**kw)
            res = v_l / v_r
            return res
        return with_number_check(eFunc, o)

    def VisitExpOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        def eFunc(**kw):
            return f_lhs(**kw) ** o.rhs
        return eFunc

    def _VisitFunctionDefInstantiation(self, o, **kwargs):

        # Param Functors:
        param_functors = {}
        for p in o.parameters:
            param_functors[p] = self.visit(o.parameters[p])
        func_call_functor = self.visit(o.function_def)
        def eFunc(**kw):
            func_params_new = dict([(p, func(**kw)) for (p, func) in param_functors.iteritems()])
            if 'func_params' in kw:
                del kw['func_params']
            res = func_call_functor(func_params=func_params_new,**kw)
            return res

        return eFunc

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return self._VisitFunctionDefInstantiation(o, **kwargs)
    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        return self._VisitFunctionDefInstantiation(o, **kwargs)




    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        f_rhs = self.visit(o.rhs_ast)
        def eFunc(**kw):
            return f_rhs(**kw)
        return eFunc

    def VisitFunctionDefUser(self, o, **kwargs):
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_rhs(**kw)
        return eFunc

    def VisitFunctionDefParameter(self, o, **kwargs):
        def eFunc(func_params, **kw):
            if not o.symbol in func_params:
                print "Couldn't find %s in %s" % (o.symbol, func_params.keys())
                assert False
            return func_params[o.symbol]
        return eFunc


    # Map to Numpy:
    def VisitRVUniform(self, o, **kwargs):
        return self._VisitRV(o, functor=np.random.uniform, arg_names=['min','max'] )

    def VisitRVNormal(self, o, **kwargs):
        return self._VisitRV(o, functor=np.random.normal, arg_names=['loc', 'scale'] )

    def _VisitRV(self, o, functor, arg_names, **kwargs):
        if not self.as_float_in_si:
            def func(**kwargs):
                args = [kwargs[a].float_in_si() for a in arg_names]
                return MMQuantity(functor(*args), MMUnit())
        else:
            def func(**kwargs):
                args = [kwargs[a] for a in arg_names]
                return float(functor(*args) )
        return func



    def VisitRandomVariable(self, o, **kwargs):
        # Param Functors:
        param_functors = {}
        for p in o.parameters:
            param_functors[p] = self.visit(p.rhs_ast)
        func_call_functor = o.accept_RVvisitor(self)
        def eFunc(**kw):
            func_params_new = dict([(p.name, func(**kw)) for (p, func) in param_functors.iteritems()])
            if 'func_params' in kw:
                del kw['func_params']
            res = func_call_functor(**func_params_new)
            return res

        return eFunc




    def VisitEmitEvent(self, o, **kwargs):
        param_evals = {}
        for param in o.parameters:
            param_evals[param] = self.visit(param.rhs)

        def f(state_data, **kw):
            parameter_values = {}
            for p in o.parameters:
                val = param_evals[p](state_data=state_data, **kw)
                parameter_values[p.port_parameter_obj.symbol] = val
            # Emit the event!:
            state_data.event_manager.emit_event(port=o.port, parameter_values=parameter_values )
        return f




