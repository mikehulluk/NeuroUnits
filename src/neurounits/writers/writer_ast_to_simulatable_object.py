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

import pylab
import mredoc

class Mode:

    RetainUnits = 'RetainUnits'
    AssumeSIFloat = 'AssumeSIFloat'


class EqnSimulator(object):

    """A class to allow the evaluation of eqnsets.
    A simulator object is created using
    """

    def __init__(self, ast):

        self.ast = ast
        self.fObj = FunctorGenerator(ast, as_float_in_si=True)

        # Set the variable order:
        self.timederivatives = list(ast.timederivatives)
        self.timederivatives_evaluators = [ self.fObj.timederivative_evaluators[td.lhs.symbol] for td in self.timederivatives ]




    def build_redoc( self, time_data, traces= None, phase_plots=None, params={}, state0In={}, default_state0=None):
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
            f = pylab.figure()
            pylab.plot(res['t'], res[sym])
            pylab.xlabel('Time (s)')
            pylab.ylabel('Symbol: %s')
            return mredoc.Figure(f)

        def build_phase_plot(sym1, sym2):
            f = pylab.figure()
            pylab.plot(res[sym1], res[sym2])
            pylab.xlabel('Symbol: %s' % sym1)
            pylab.ylabel('Symbol: %s' % sym2)
            return mredoc.Figure(f)


        return mredoc.Section( "Simulation Results for: %s",
                 [ build_trace_plot(tr) for tr in traces ] + [ build_phase_plot(*tr) for tr in phase_plots ]
                )



    def __call__(self, time_data, params={}, state0In={}, default_state0 = None ):
        if len(self.ast.timederivatives) == 0:
            return

        assert isinstance(time_data, np.ndarray)

        def get_as_si(o):
            if isinstance(o, (float, int)):
                return o
            return o.float_in_si()

        initial_condition_map = {}
        for s in self.ast.initial_conditions:
            assert isinstance(s.value, basestring)
            v = neurounits.NeuroUnitParser.QuantitySimple(s.value)
            initial_condition_map[s.symbol] = v

        def get_initial_condition(symbol):
            if symbol in state0In:
                return state0In[symbol]
            if symbol in initial_condition_map:
                return initial_condition_map[symbol]
            if default_state0:
                return default_state0
            raise ValueError('No Starting Value for StateVariable: %s found'
                              % symbol)

        # Resolve the starting values:
        state0 = [ get_as_si(get_initial_condition(td.lhs.symbol) ) for td in self.timederivatives ]



        def rebuild_kw_dict(raw_state_data, params, t0):
            kw_states = dict([(td.lhs.symbol, y) for (td, y) in
                             zip(self.timederivatives, raw_state_data)])
            kw = safe_dict_merge(kw_states, params)
            kw['t'] = t0
            return kw

        def evaluate_gradient(y, t0):
            # Create a dictionary containing the current states and
            # the parameters:
            kw = rebuild_kw_dict(raw_state_data=y, params=params,t0=t0)
            return [ ev(**kw) for ev in self.timederivatives_evaluators ]


        ## Sanity Check:
        #for a,ev in self.fObj.assignment_evaluators.iteritems():
        #    x = state0In
        #    x.update(params)
        #    x['t'] = self.ast.library_manager.backend.Quantity(0.0,self.ast.library_manager.backend.Unit(second=1) )
        #    ev(**state0In)

        # ACTION!
        #evaluate_gradient(state0, 0.0)


        # Evaluate:
        y = scipy.integrate.odeint( evaluate_gradient, state0, t=time_data )

        # Add the units back to the states:
        res = {}
        res['t'] = time_data  # , self.ast.library_manager.backend.Unit(second=1)
        for (i, td) in enumerate(self.timederivatives):
            res[td.lhs.symbol] = y[:, i]


        # Re-evaluate the assignments:
        print 'Re-evaluating assignments'
        nAssignments = len(self.fObj.assignment_evaluators)
        ass_data = [list() for i in range(nAssignments)]

        ass_units = [None for i in range(nAssignments)]
        ass_names = [None for i in range(nAssignments)]
        for t in time_data:
            state_data = y[t, :]
            kw = rebuild_kw_dict(raw_state_data=state_data,
                                 params=params, t0=t)

            for (i, (a, afunctor)) in \
                enumerate(self.fObj.assignment_evaluators.iteritems()):

                aVal = afunctor(**kw)

                if ass_names[i] is None:
                    ass_names[i] = a

                aValRaw = aVal # .rescale(ass_units[i])

                ass_data[i].append(aValRaw)

        for (i, (name, unit)) in enumerate(zip(ass_names, ass_units)):
            d = np.array(ass_data[i])
            res[name] = d
            print 'Ass;', name

        return res






#def SimulateEquations(ast,):
#    evaluator = EqnSimulator(ast)
#
#    import pylab
#
#    nPlots = len(ast.summary_data)
#    f = pylab.figure()
#
#    for i,s in enumerate(ast.summary_data):
#
#        res = evaluator(state0In=s.y0, params=s.params,time_data=s.t)
#
#        ax = f.add_subplot(nPlots,1,i)
#        x,xunit = res[s.x]
#        y,yunit = res[s.y]
#
#        ax.plot( x,y, 'r')
#        FormatUnit
#        ax.set_xlabel("%s (Unit: %s)"%(s.x, FormatUnit(xunit) ))
#        ax.set_ylabel("%s (Unit: %s)"%(s.y, FormatUnit(yunit) ))
#

class FunctorGenerator(ASTVisitorBase):

    def __init__(self, eqnset=None, as_float_in_si=False):
        self.ast = None

        self.assignment_evaluators = {}
        self.timederivative_evaluators = {}

        self.as_float_in_si = as_float_in_si

        if eqnset is not None:
            assert isinstance(eqnset, ast.EqnSet)
            self.visit(eqnset)

    def VisitEqnSet(self, o, **kwargs):
        self.ast = o

        deps = VisitorFindDirectSymbolDependance()
        deps.visit(o)
        self.assignee_to_assigment = {}
        for a in o.assignments:
            self.assignee_to_assigment[a.lhs] = a

        assignment_deps = deps.dependancies
        resolved = set()

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
            self.visit(a)

    def VisitEqnAssignment(self, o, **kwargs):
        self.assignment_evaluators[o.lhs.symbol] = self.visit(o.rhs)

    def VisitEqnTimeDerivative(self, o, **kwargs):
        self.timederivative_evaluators[o.lhs.symbol]  = self.visit(o.rhs)

    def VisitIfThenElse(self, o, **kwargs):
        fpred = self.visit(o.predicate)
        ftrue = self.visit(o.if_true_ast)
        ffalse = self.visit(o.if_false_ast)

        def f(**kw):
            if fpred(**kw):
                return ftrue(**kw)
            else:
                return ffalse(**kw)
        return f


    def VisitInEquality(self, o ,**kwargs):
        lt = self.visit( o.less_than )
        gt = self.visit( o.greater_than )
        def f(**kw):
            return lt(**kw) < gt(**kw)
        return f

    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    def VisitBuiltInFunction(self, o, **kwargs):
        def eFunc(**kw):
            if o.funcname == 'exp':
                ParsingBackend = MHUnitBackend
                return ParsingBackend.Quantity( float( np.exp( ( kw.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
            if o.funcname == 'sin':
                ParsingBackend = MHUnitBackend
                return ParsingBackend.Quantity( float( np.sin( ( kw.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
            if o.funcname == 'pow':
                ParsingBackend = MHUnitBackend
                return ParsingBackend.Quantity(
                        float( np.power( ( kw['base'] ).dimensionless() ,( kw['exp'] ).dimensionless() )  ),
                        ParsingBackend.Unit() )
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
        def eFunc2(**kw):
            return kw[o.symbol]

        return eFunc2


    def VisitParameter(self, o, **kwargs):
        def eFunc(**kw):
            return kw[o.symbol]

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



    def VisitSuppliedValue(self, o, **kwargs):
        def eFunc(**kw):
            return kw[ o.symbol]
        return eFunc


    def VisitAssignedVariable(self, o, **kwargs):
        #print 'Visiting', o.symbol
        # We are at an assignment. We resolve this by looking up the
        # Right hand side of the assigned variable:
        assignment_rhs = self.assignment_evaluators[o.symbol]
        def eFunc(**kw):
            return assignment_rhs(**kw)
        return eFunc

    def VisitAddOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_lhs(**kw) + f_rhs(**kw)
        return eFunc

    def VisitSubOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_lhs(**kw) - f_rhs(**kw)
        return eFunc

    def VisitMulOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_lhs(**kw) * f_rhs(**kw)
        return eFunc

    def VisitDivOp(self, o, **kwargs):
        f_lhs = self.visit(o.lhs)
        f_rhs = self.visit(o.rhs)
        def eFunc(**kw):
            return f_lhs(**kw) / f_rhs(**kw)
        return eFunc

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
            func_params = dict([(p, func(**kw)) for (p, func) in param_functors.iteritems() ] )
            return func_call_functor(**func_params)
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
        def eFunc(**kw):
            if not o.symbol in kw:
                print "Couldn't find %s in %s" % (o.symbol, kw.keys())
            return kw[o.symbol]
        return eFunc
