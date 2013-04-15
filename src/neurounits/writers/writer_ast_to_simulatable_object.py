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

import scipy
import scipy.integrate
from neurounits.units_misc import safe_dict_merge

import numpy as np
from neurounits.visitors.common import VisitorFindDirectSymbolDependance

from neurounits import ast
from neurounits.units_backends.mh import MHUnitBackend
import neurounits

import mredoc
from functools import partial
import traceback
from collections import defaultdict
import sys



class DebugScope(object):

    nesting_depth = 0

    def __init__(self, s ):
        self.s = s
    def __enter__(self):
        #print 'Entering Scope: %s' % self.s
        DebugScope.nesting_depth = DebugScope.nesting_depth + 1

    def __exit__(self, *args):
        DebugScope.nesting_depth = DebugScope.nesting_depth - 1
        #print 'Exiti Scope: %s' % self.s, args


std_out_orig = sys.stdout

class MyWriter(object):
    def write(self, s):
        s1 = '  '  * DebugScope.nesting_depth
        std_out_orig.write(s1)
        return std_out_orig.write(s)

    def flush(self, *args, **kwargs):
        return std_out_orig.flush(*args, **kwargs)

sys.stdout = MyWriter()






def get_as_si(o):
    if isinstance(o, (float, int)):
        return o
    return o.float_in_si()




def rebuild_kw_dict(raw_state_data, params, t0, timederivatives):
    kw_states = dict([(td.lhs.symbol, y) for (td, y) in zip(timederivatives, raw_state_data)])
    #print t0, 'kw_states', kw_states
    kw = safe_dict_merge(kw_states, params)
    kw['t'] = t0
    return kw

def evaluate_gradient(y, t0, params, timederivatives_evaluators, timederivatives):
    # Create a dictionary containing the current states and
    # the parameters:
    kw = rebuild_kw_dict(raw_state_data=y, params=params,t0=t0, timederivatives=timederivatives)
    return [ev(**kw) for ev in timederivatives_evaluators]




class EqnSimulator(object):

    """A class to allow the evaluation of eqnsets.
    A simulator object is created using
    """

    def __init__(self, ast):

        self.ast = ast
        self.fObj = FunctorGenerator(ast, as_float_in_si=True)

        # Set the variable order:
        self.timederivatives = list(ast.timederivatives)
        self.timederivatives_evaluators = [self.fObj.timederivative_evaluators[td.lhs.symbol] for td in self.timederivatives]




    def build_redoc( self, time_data, traces=None, phase_plots=None, params={}, state0In={}, default_state0=None):
        res = self.__call__(time_data=time_data, params=params, default_state0=default_state0)

        # What traces do we plot:

        if traces is False:
            traces = []
        if traces is None:
            traces = res.keys()

        # What phase plots shall we draw:

        if phase_plots is False:
            phase_plots = []
        if phase_plots is None:
            phase_plots = []
            for r in res.keys():
                for s in res.keys():
                    if r != s:
                        phase_plots.append((r, s))

        def build_trace_plot(sym):
            import pylab
            f = pylab.figure()
            pylab.plot(res['t'], res[sym])
            pylab.xlabel('Time (s)')
            pylab.ylabel('Symbol: %s')
            return mredoc.Figure(f)

        def build_phase_plot(sym1, sym2):
            import pylab
            f = pylab.figure()
            pylab.plot(res[sym1], res[sym2])
            pylab.xlabel('Symbol: %s' % sym1)
            pylab.ylabel('Symbol: %s' % sym2)
            return mredoc.Figure(f)


        return mredoc.Section( "Simulation Results for: %s" % self.ast.name,
                 [ build_trace_plot(tr) for tr in traces ] + [ build_phase_plot(*tr) for tr in phase_plots ]
                )



    def __call__(self, time_data, params={}, state0In={}, default_state0=None ):
        if len(self.ast.timederivatives) == 0:
            return

        assert isinstance(time_data, np.ndarray)

        initial_condition_map = {}
        for s in self.ast.initial_conditions:
            assert isinstance(s.value, basestring)
            v = neurounits.NeuroUnitParser.QuantitySimple(s.value)
            initial_condition_map[s.symbol] = v







        ## Sanity Check:
        #for a,ev in self.fObj.assignment_evaluators.iteritems():
        #    x = state0In
        #    x.update(params)
        #    x['t'] = self.ast.library_manager.backend.Quantity(0.0,self.ast.library_manager.backend.Unit(second=1) )
        #    ev(**state0In)

        # ACTION!
        #evaluate_gradient(state0, 0.0)

        # Resolve the starting values:
        #state0 = [ get_as_si(get_initial_condition(td.lhs.symbol) ) for td in self.timederivatives ]




        # A.Calculate the initial values of
        # each state-variable (in SI)
        # ----------------------------------
        state0=[]
        for td in self.timederivatives:
            symbol = td.lhs.symbol

            if symbol in state0In:
                init = state0In[symbol]
            elif symbol in initial_condition_map:
                init = initial_condition_map[symbol]
            elif default_state0:
                init = default_state0
            else:
                raise ValueError('No Starting Value for StateVariable: %s found' % symbol)
            # Convert the value to SI:
            state0.append( get_as_si(init) )



        # B. Evaluate, do the integration to
        # find values for all the state variables:
        # -----------------------------------------
        y = scipy.integrate.odeint(
                partial(evaluate_gradient,
                    timederivatives_evaluators=self.timederivatives_evaluators,
                    timederivatives=self.timederivatives,
                    params=params),
                state0,
                t=time_data,
                )




        # Re-evaluate the assignments:
        print 'Re-evaluating assignments'
        nAssignments = len(self.fObj.assignment_evaluators)
        ass_data = [list() for i in range(nAssignments)]

        ass_units = [None for i in range(nAssignments)]
        ass_names = [None for i in range(nAssignments)]
        for (time_index, t) in enumerate(time_data):
            state_data = y[time_index, :]
            kw = rebuild_kw_dict(raw_state_data=state_data, params=params, t0=t, timederivatives=self.timederivatives)

            for (i, (a, afunctor)) in enumerate(self.fObj.assignment_evaluators.iteritems()):

                aVal = afunctor(**kw)

                if ass_names[i] is None:
                    ass_names[i] = a

                aValRaw = aVal # .rescale(ass_units[i])

                #print a, aValRaw

                ass_data[i].append(aValRaw)


        # Add the units back to the states:
        res = {}
        res['t'] = time_data  # , self.ast.library_manager.backend.Unit(second=1)
        for (i, td) in enumerate(self.timederivatives):
            res[td.lhs.symbol] = y[:, i]



        for (i, (name, unit)) in enumerate(zip(ass_names, ass_units)):
            d = np.array(ass_data[i])
            res[name] = d
            #print 'Ass;', name

        return res






class SimulationStateData(object):
    def __init__(self,
            parameters,
            suppliedvalues,
            states_in,
            states_out,
            rt_regimes,
            event_manager,
            ):
        self.parameters = parameters
        self.suppliedvalues = suppliedvalues
        self.states_in = states_in
        self.states_out = states_out
        self.rt_regimes = rt_regimes
        self.event_manager = event_manager

    def copy(self):
        return SimulationStateData(parameters=self.parameters.copy(),
                                   suppliedvalues=self.suppliedvalues.copy(),
                                   states_in=self.states_in.copy(),
                                   states_out=self.states_out.copy(),
                                   rt_regimes=self.rt_regimes.copy(),
                                   event_manager = None

                                   )





def with_number_check(func, src_obj):
    return func


    def my_func(*args, **kwargs):
        #print 'Evaluating Node', src_obj
        with DebugScope(''):
            res = func(*args, **kwargs)
        print 'Value of node:', repr(src_obj), res
        return res
    return my_func

class FunctorGenerator(ASTVisitorBase):

    def __init__(self, eqnset=None, as_float_in_si=False):
        self.ast = None

        self.assignment_evaluators = {}
        self.timederivative_evaluators = {}

        self.as_float_in_si = as_float_in_si

        if eqnset is not None:
            assert isinstance(eqnset, ast.EqnSet)
            self.visit(eqnset)

    #def VisitEqnSet(self, o, **kwargs):
    #    self.ast = o

    #    deps = VisitorFindDirectSymbolDependance()
    #    deps.visit(o)
    #    self.assignee_to_assigment = {}
    #    for a in o.assignments:
    #        self.assignee_to_assigment[a.lhs] = a

    #    assignment_deps = deps.dependancies
    #    resolved = set()

    #    def resolve(assignment):
    #        if assignment in resolved:
    #            return

    #        if type(assignment) != ast.AssignedVariable:
    #            return
    #        for dep in assignment_deps[assignment]:
    #            resolve(dep)
    #        self.visit(self.assignee_to_assigment[assignment])
    #        resolved.add(assignment)

    #    for a in o.assignments:
    #        resolve(a.lhs)

    #    for a in o.assignments:
    #        self.visit(a)

    #    for a in o.timederivatives:
    #        self.visit(a)

    def VisitNineMLComponent(self, o, **kwargs):
        self.ast = o

        deps = VisitorFindDirectSymbolDependance()
        deps.visit(o)
        self.assignee_to_assigment = {}
        for a in o.assignments:
            self.assignee_to_assigment[a.lhs] = a

        assignment_deps = deps.dependancies
        resolved = set()



        #print
        #print 'Assignments:'
        #for ass in o.assignments:
            #print ass.lhs.symbol, ass.lhs



        def resolve(assignment):
            if assignment in resolved:
                return

            if type(assignment) != ast.AssignedVariable:
                return
            for dep in assignment_deps[assignment]:
                resolve(dep)
            self.visit(self.assignee_to_assigment[assignment])
            resolved.add(assignment)

        for a in o.assignments:
            resolve(a.lhs)

        for a in o.assignments:
            self.visit(a)

        for a in o.timederivatives:
            #print 'Time Derivative:', a, a.lhs.symbol
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
            # print 'Making State assingment!'
            sv_name = o.lhs.symbol
            # print kw.keys()
            new_value = rhs(state_data=state_data, **kw)
            # print 'Old Value',state_data.states_in[sv_name]
            # print 'New Value',new_value
            state_data.states_out[sv_name] = new_value

            # assert False
            # return None

        return f1

#    def VisitEqnAssignment(self, o, **kwargs):
#        self.assignment_evaluators[o.lhs.symbol] = self.visit(o.rhs)

    def _visit_trans(self, o, **kwargs):
        callable_actions = [self.visit(a) for a in o.actions]

        def f2(state_data, **kw):
            # Do the effects:
            for c in callable_actions:
                c(state_data=state_data, **kw)

            # Switch the state:
            #current_regimes[rt_graph] = tr.target_regime


        return f2

    def VisitOnTransitionTrigger(self, o, **kwargs):
        # Trigger predicate functor:
        self.transition_triggers_evals[o] = self.visit(o.trigger, **kwargs)

        # Action functor:
        self.transitions_actions[o] = self._visit_trans(o, **kwargs)

    def VisitOnTransitionEvent(self, o, **kwargs):
        self.transition_port_handlers[o.port].append( o )
        self.transitions_actions[o] = self._visit_trans(o, **kwargs)

    def VisitOnEventDefParameter(self, o):
        def f(evt,**kw):
            #print 'Getting value of:', o.symbol

            # Single parameter:
            if len(evt.parameter_values)==1:
                return list( evt.parameter_values.values() )[0]
            # Resolve from among many parameters:
            else:
                return evt.parameter_values[o.port_parameter_obj.symbol]

            #print 'Getting value of:', o.symbol
            #print evt
            #print
            #assert False
        return f


    def VisitEventPortConnection(self, o):
        self.transition_event_forwarding[o.src_port].append(o.dst_port)





    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        self.assignment_evaluators[o.lhs.symbol] = self.visit(o.rhs_map)

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        with DebugScope('VisitTimeDerivativeByRegime (%s)' % o.lhs.symbol):
            self.timederivative_evaluators[o.lhs.symbol] = self.visit(o.rhs_map)



    def VisitRegimeDispatchMap(self,o,**kwargs):


        rt_graph = o.get_rt_graph()

        rhs_functors = dict([(regime, self.visit(rhs)) for (regime,rhs) in o.rhs_map.items()])
        from neurounits.misc import SeqUtils
        try:
            default = SeqUtils.filter_expect_single(rhs_functors.keys(), lambda r:r.name == None)
            assert not None in rhs_functors
            rhs_functors[None] = rhs_functors[default]
        except ValueError:
            pass





        def f3(state_data, **kw):
            regime_states = state_data.rt_regimes
            #print 'Getting regime_state for RT graph:', repr(rt_graph)

            curr_state = regime_states[rt_graph]
            if curr_state in rhs_functors:
                rhs_functor = rhs_functors[curr_state]
            else:
                rhs_functor = rhs_functors[None]

            return rhs_functor(state_data=state_data, **kw)

        return f3

        assert len(o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0])

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


    def VisitInEquality(self, o ,**kwargs):
        lt = self.visit( o.less_than )
        gt = self.visit( o.greater_than )
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

    def VisitBuiltInFunction(self, o, **kwargs):
        if not self.as_float_in_si:

            def eFunc(state_data, func_params, **kw):
                if o.funcname == '__abs__':
                    ParsingBackend = MHUnitBackend
                    assert len(func_params) == 1
                    return ParsingBackend.Quantity( float( np.abs( ( func_params.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
                if o.funcname == '__exp__':
                    ParsingBackend = MHUnitBackend
                    assert len(func_params) == 1
                    return ParsingBackend.Quantity( float( np.exp( ( func_params.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
                if o.funcname == '__sin__':
                    assert len(func_params) == 1
                    ParsingBackend = MHUnitBackend
                    return ParsingBackend.Quantity( float( np.sin( ( func_params.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
                if o.funcname == '__pow__':
                    assert len(func_params) == 2
                    ParsingBackend = MHUnitBackend
                    return ParsingBackend.Quantity( float( np.power( ( func_params['base'] ).dimensionless() ,( func_params['exp'] ).dimensionless() )  ), ParsingBackend.Unit() )
                else:
                    assert False, "Sim can't handle function: %s" % o.funcname
        else:
            def eFunc(**kw):
                if o.funcname == 'exp':
                    assert len(kw) == 1
                    return float(np.exp(kw.values()[0]))
                if o.funcname == 'sin':
                    assert len(kw) == 1
                    return float(np.sin(kw.values()[0]))
                if o.funcname == 'pow':
                    assert len(kw) == 2
                    return float(np.power(kw['base'], kw['exp']))
                else:
                    assert False

        return eFunc

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

        def eFunc2(state_data, **kw):
            v = state_data.states_in[o.symbol]
            assert o.get_dimension().is_compatible(v.get_units())
            return v

        return with_number_check( eFunc2, o )

    def VisitParameter(self, o, **kwargs):
        def eFunc(state_data,**kw):
            #v = kw[o.symbol]
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
                from neurounits.units_backends.mh import MMUnit, MMQuantity
                return MMQuantity( 0 , o.get_dimension() )
            return eFunc
        else:
            assert False,'TODO: Need to multiply next lines by unit...'
            def eFunc(**kw):
                return 0
            return eFunc



    def VisitSuppliedValue(self, o, **kwargs):
        def eFunc(state_data, **kw):
            v = state_data.suppliedvalues[o.symbol]
            return v
        return eFunc


    def VisitAssignedVariable(self, o, **kwargs):
        # We are at an assignment. We resolve this by looking up the
        # Right hand side of the assigned variable:
        #print self.assignment_evaluators.keys()
        #print 'Assigned Var:', o, o.symbol

        assignment_rhs = self.assignment_evaluators[o.symbol]
        def eFunc(**kw):
            res = assignment_rhs(**kw)
            #print 'Value of: %s is %s' %( o.symbol, res)
            return res
        return with_number_check(eFunc, o)

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
        return with_number_check( eFunc, o)

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
        return with_number_check(eFunc,o)

    def VisitExpOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        def eFunc(**kw):
            return f_lhs(**kw) ** o.rhs
        return eFunc

    def VisitFunctionDefInstantiation(self, o, **kwargs):

        # Param Functors:
        param_functors = {}
        for p in o.parameters:
            param_functors[p] = self.visit(o.parameters[p])
        func_call_functor = self.visit(o.function_def)
        def eFunc(**kw):
            #print 'kw', kw
            #print o
            func_params_new = dict([(p, func( **kw)) for (p, func) in param_functors.iteritems()])
            if 'func_params' in kw:
                del kw['func_params']
            res = func_call_functor(func_params=func_params_new,**kw)
            return res

        return eFunc

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        f_rhs = self.visit(o.rhs_ast)
        def eFunc(**kw):
            return f_rhs(**kw)
        return eFunc

    def VisitFunctionDef(self, o, **kwargs):
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_rhs(**kw)
        return eFunc

    def VisitFunctionDefParameter(self, o, **kwargs):
        def eFunc(func_params,**kw):
            #print 'Param:', kw
            if not o.symbol in func_params:
                print "Couldn't find %s in %s" % (o.symbol, func_params.keys())
            return func_params[o.symbol]
        return eFunc

    def VisitEmitEvent(self, o, **kwargs):


        param_evals = {}
        for param in o.parameters:
            param_evals[param] = self.visit(param.rhs)

        def f(state_data,**kw):
            parameter_values = {}
            for p in o.parameters:
                val = param_evals[p](state_data=state_data, **kw)
                parameter_values[p.port_parameter_obj.symbol] = val
            # Emit the event!:
            state_data.event_manager.emit_event(  port=o.port, parameter_values=parameter_values )
        return f




