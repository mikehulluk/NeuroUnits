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

from neurounits.visitors import ASTVisitorBase,ASTActionerDefault
from neurounits.visitors.bases.base_actioner import SingleVisitPredicate, ASTActionerDepthFirst
from neurounits import ast
from neurounits.visitors.common import ASTNodeLabels
from neurounits.units_misc import EnsureExisits
from neurounits.visitors.common import ActionerFormatStringsAsIDs
from neurounits.unit_errors import panic, UnitMismatchError


class ASTVisitorCollectorAll(ASTActionerDefault):

    def __init__(self, eqnset, **kwargs):
        ASTActionerDefault.__init__(self, **kwargs)
        self.objects = set()
        self.visit(eqnset)

    def ActionNode(self, o):
        self.objects.add(o)


class VerifyUnitsInTree(ASTActionerDepthFirst):

    def __init__(self, obj, unknown_ok):
        super(VerifyUnitsInTree, self).__init__(action_predicates=[SingleVisitPredicate()])
        self.unknown_ok = unknown_ok

        if unknown_ok:
            return

        self.visit(obj)

    def verify_equal_units(self, objs):
        from neurounits.units_backends.mh import MMUnit
        from neurounits.ast import ASTExpressionObject
        print 'Checking', objs
        if len(objs) == 0:
            return
        o0 = objs[0]
        for o in objs:
            print o, o0
            assert isinstance(o, ASTExpressionObject)
            assert isinstance(o0, ASTExpressionObject)
            if not o.get_dimension().is_compatible(o0.get_dimension()):
                print 'Units mismatch'
                print o, o0
                assert False,' %s, %s (%s %s)' %(o,o0, o.get_dimension(), o0.get_dimension())

    def ActionEqnSet(self, o, **kwargs):
        pass

    def ActionLibrary(self, o, **kwargs):
        pass

    def ActionNineMLComponent(self, o, **kwargs):
        pass

    def ActionIfThenElse(self, o, **kwargs):
        self.verify_equal_units([o, o.if_true_ast, o.if_false_ast])

    def ActionInEquality(self, o, **kwargs):
        pass

    def ActionBoolAnd(self, o, **kwargs):
        pass

    def ActionBoolOr(self, o, **kwargs):
        pass

    def ActionBoolNot(self, o, **kwargs):
        pass

    # Function Definitions:
    def ActionFunctionDef(self, o, **kwargs):
        self.verify_equal_units([o, o.rhs])

    def ActionBuiltInFunction(self, o, **kwargs):
        pass

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

    def ActionAnalogReducePort(self, o, **kwargs):
        self.verify_equal_units([o] + o.rhses)

    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        from neurounits.units_backends.mh import MMUnit
        (o.lhs.get_dimension()).check_compatible(o.rhs_map.get_dimension() * MMUnit(second=1))

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        self.verify_equal_units([o.lhs, o.rhs_map])

    def ActionRegimeDispatchMap(self, o, **kwargs):
        self.verify_equal_units([o] + o.rhs_map.values())

    def ActionAddOp(self, o, **kwargs):
        self.verify_equal_units([o, o.lhs, o.rhs])

    def ActionSubOp(self, o, **kwargs):
        self.verify_equal_units([o, o.lhs, o.rhs])

    def ActionMulOp(self, o, **kwargs):
        (o.lhs.get_dimension() * o.rhs.get_dimension()).check_compatible(o.get_dimension())

    def ActionDivOp(self, o, **kwargs):
        (o.lhs.get_dimension() / o.rhs.get_dimension()).check_compatible(o.get_dimension())

    def ActionExpOp(self, o, **kwargs):
        assert o.is_dimensionless()
        assert o.lhs.is_dimensionless()
        assert o.rhs.is_dimensionless()

    def ActionFunctionDefInstantiation(self, o, **kwargs):
        self.verify_equal_units([o, o.function_def])

    def ActionFunctionDefInstantiationParater(self, o, **kwargs):
        self.verify_equal_units([o, o.rhs_ast, o._function_def_parameter])

    def ActionOnEventStateAssignment(self, o, **kwargs):
        self.verify_equal_units([o, o.lhs, o.rhs])

    def ActionOnEvent(self, o, **kwargs):
        pass

    def ActionOnTransitionTrigger(self, o, **kwarg):
        pass

    def ActionOnTransitionEvent(self, o, **kwargs):
        pass

    def ActionEmitEvent(self, o, **kwargs):
        pass

    def ActionOnEventDefParameter(self, o, **kwargs):
        # self.verify_equal_units([o,
        pass


class DimensionResolver(ASTVisitorBase):

    def EnsureEqualDimensions(self, args, reason=None):
        assigned_dimensions = [a for a in args if a.is_dimension_known()]

        # No dimensions known?
        if len(assigned_dimensions) == 0:
            return []

        u = assigned_dimensions[0]

        for au in assigned_dimensions[1:]:
            try:
                u.get_dimension().check_compatible(au.get_dimension())
                u.get_dimension() == au.get_dimension()
            except UnitMismatchError, e:
                raise UnitMismatchError(unitA=u.get_dimension(), unitB=au.get_dimension(), objA=u, objB=au)
            #check_dimension_compatible(u, au)

        unassigned_dimensions = [a for a in args if not a.is_dimension_known()]
        for au in unassigned_dimensions:
            u.get_dimension()
            self.RegisterDimensionPropogation(obj=au, new_dimension=u.get_dimension(), reason=reason)
        return unassigned_dimensions

    # visit each node, and try and propogate dimensions.
    # Each method should return a list of nodes resolved.

    def __init__(self, ast, obj_label_dict=None):
        self.ast = ast
        self.history = []
        self.obj_label_dict = obj_label_dict
        self.Initialise()

    def DumpUnitStateToHistoryAll(self):
        for (obj, name) in self.obj_label_dict.iteritems():
            if not isinstance(obj, ast.ASTExpressionObject):
                continue

            obj_dimensionality = (obj.get_dimensionality() if obj.is_dimensionality_known() else '<Dimension Unknown>')
            obj_unit = None
            self.history.append(' %s -> Dim: %s Unit: %s' % (name,
                                obj_dimensionality, obj_unit))

    def DumpUnitStateToHistorySymbols(self):
        for (obj, name) in self.obj_label_dict.iteritems():
            if not isinstance(obj, ast.ASTExpressionObject):
                continue

            try:
                obj_dim = obj.get_dimension() if obj.is_dimension_known() else "<Dimension Unknown>"
                obj_unit = None
                self.history.append(' %s - %s - %s %s' % (name,obj.symbol, obj_dim, obj_unit) )
            except:
                pass

    def SummariseUnitState(self, title):
        return
        if title is not None:
            self.history.append(title)

        self.history.append('Symbols:')
        self.DumpUnitStateToHistorySymbols()

        self.history.append('All:')
        self.DumpUnitStateToHistoryAll()
        self.history.append('')

    def Initialise(self):
        self.SummariseUnitState(title='Initially')

    def RegisterDimensionPropogation(self, obj, new_dimension, reason):
        obj.set_dimension(new_dimension)

    def VisitEqnSet(self, o, **kwargs):
        pass

    def VisitLibrary(self, o, **kwargs):
        pass

    def VisitNineMLComponent(self, o, **kwargs):
        pass

    def VisitOnEvent(self, o, **kwargs):
        return

    def VisitOnEventStateAssignment(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs])

    def VisitIfThenElse(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.if_true_ast, o.if_false_ast])

    def VisitInEquality(self, o, **kwargs):
        self.EnsureEqualDimensions([o.less_than, o.greater_than])

    def VisitBoolAnd(self, o, **kwargs):
        pass

    def VisitBoolOr(self, o, **kwargs):
        pass

    def VisitBoolNot(self, o, **kwargs):
        pass

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
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
        return []

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    def VisitTimeDerivativeByRegime(self, o, **kwargs):

        if o.lhs.is_dimension_known() and o.rhs_map.is_dimension_known():
            return
        if not o.lhs.is_dimension_known() and not o.rhs_map.is_dimension_known():
            return

        one_sec = self.ast.library_manager.backend.Unit(second=1)
        if o.lhs.is_dimension_known():
            self.RegisterDimensionPropogation(o.rhs_map, new_dimension=o.lhs.get_dimension() / one_sec, reason='TimeDerivative')
            return
        if o.rhs_map.is_dimension_known():
            self.RegisterDimensionPropogation(o.lhs, new_dimension=o.rhs_map.get_dimension() * one_sec, reason='TimeDerivative')
            return

    def VisitRegimeDispatchMap(self, o, **kwargs):

        if len([True for i in [o] +o.rhs_map.values() if i.is_dimension_known()]) == len(o.rhs_map) + 1:
            return
        if len([True for i in [o] +o.rhs_map.values() if i.is_dimension_known()]) == 0:
            return

        for rhs in o.rhs_map.values():
            if o.is_dimension_known() and not rhs.is_dimension_known():
                self.RegisterDimensionPropogation(rhs, new_dimension=o.get_dimension(), reason='TD-Regime')
                continue
            if rhs.is_dimension_known() and not o.is_dimension_known():
                self.RegisterDimensionPropogation(o, new_dimension=rhs.get_dimension(), reason='TD-Regime')
                continue

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return self.EnsureEqualDimensions([o.lhs, o.rhs_map],reason='EqnAssignmentPerRegime')



    def VisitAddOp(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs], reason='AddOp')

    def VisitSubOp(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs], reason='SubOp')

    def VisitMulOp(self, o, **kwargs):
        if len([True for i in (o, o.lhs, o.rhs)
               if i.is_dimension_known()]) != 2:
            return

        if o.is_dimension_known():
            if o.lhs.is_dimension_known():
                self.RegisterDimensionPropogation(o.rhs, new_dimension=o.get_dimension() / o.lhs.get_dimension(), reason='MulOp')
            else:
                self.RegisterDimensionPropogation(o.lhs, new_dimension=o.get_dimension() / o.rhs.get_dimension(), reason='MulOp')
        else:
            self.RegisterDimensionPropogation(o, new_dimension=o.lhs.get_dimension() * o.rhs.get_dimension(), reason='MulOp')



    def VisitDivOp(self, o, **kwargs):
        # If we don't have 2 unknowns, we can't do much:
        if len([True for i in (o, o.lhs, o.rhs)
               if i.is_dimension_known()]) != 2:
            return

        if o.is_dimension_known():
            if o.lhs.is_dimension_known():
                o.rhs.set_dimension(o.lhs.get_dimension() / o.get_dimension())
            else:
                o.lhs.set_dimension(o.get_dimension() * o.rhs.get_dimension())
        else:
            o.set_dimension(o.lhs.get_dimension() / o.rhs.get_dimension())


    def VisitExpOp(self, o, **kwargs):
        if o.lhs.is_dimension_known():
            assert o.lhs.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False),  'LHS Expected to be dimensionless, actually %s'%(o.lhs.get_dimension())
        if o.is_dimension_known():
            assert o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False)

        if not o.lhs.is_dimension_known():
            o.lhs.set_dimension(self.ast.library_manager.backend.Unit())
        if not o.is_dimension_known():
            o.set_dimension(self.ast.library_manager.backend.Unit())

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.rhs])

    def VisitFunctionDefParameter(self, o, **kwargs):
        pass

    def VisitFunctionDefInstantiation(self, o, **kwargs):

        # Check the parameters tie up:
        for p in o.parameters.values():
            self.EnsureEqualDimensions([p.rhs_ast, p])
            self.EnsureEqualDimensions([p, p._function_def_parameter])
            self.EnsureEqualDimensions([p.rhs_ast, p._function_def_parameter])
            #self.EnsureEqualDimensions([p, p._function_def_parameter.rhs_ast])

        # powint and sqrt need to  be handled differently, since thier
        # dimensions depend on the input and output:
        if isinstance(o.function_def, ast.BuiltInFunction) and o.function_def.funcname in ['powint','sqrt']:

            if o.function_def.funcname == 'powint':
                #assert False
                p = o.parameters['x']
                n = int( o.parameters['n'].rhs_ast.value.magnitude )
                d = int( o.parameters['d'].rhs_ast.value.magnitude )
                if o.is_dimension_known() and not p.is_dimension_known():
                    odim = o.get_dimension()
                    assert odim.powerTen == 0
                    pdim = self.ast.library_manager.backend.Unit(
                        meter=odim.meter * 2,
                        second=odim.second * 2,
                        ampere=odim.ampere * 2,
                        kelvin=odim.kelvin * 2,
                        mole=odim.mole * 2,
                        candela=odim.candela * 2,
                        )
                    p.set_dimension(pdim)
                    assert False
                if p.is_dimension_known() and not o.is_dimension_known():
                    pdim = p.get_dimension()
                    assert pdim.powerTen == 0
                    odim = self.ast.library_manager.backend.Unit(
                        meter=pdim.meter / 2,
                        second=pdim.second / 2,
                        ampere=pdim.ampere / 2,
                        kelvin=pdim.kelvin / 2,
                        mole=pdim.mole / 2,
                        candela=pdim.candela / 2,
                        )
                    o.set_dimension(odim)
                    assert False
            elif o.function_def.funcname == 'sqrt':
                p = o.parameters.values()[0]

                if o.is_dimension_known() and not p.is_dimension_known():
                    odim = o.get_dimension()
                    assert odim.powerTen == 0
                    pdim = self.ast.backend.Unit(
                        meter=odim.meter * 2,
                        second=odim.second * 2,
                        ampere=odim.ampere * 2,
                        kelvin=odim.kelvin * 2,
                        mole=odim.mole * 2,
                        candela=odim.candela * 2,
                        )
                    p.set_dimension(pdim)
                    assert False
                if p.is_dimension_known() and not o.is_dimension_known():
                    pdim = p.get_dimension()
                    assert pdim.powerTen == 0
                    odim = self.ast.backend.Unit(
                        meter=pdim.meter / 2,
                        second=pdim.second / 2,
                        ampere=pdim.ampere / 2,
                        kelvin=pdim.kelvin / 2,
                        mole=pdim.mole / 2,
                        candela=pdim.candela / 2,
                        )
                    o.set_dimension(odim)
                    assert False
            else:
                assert False
        else:

            self.EnsureEqualDimensions([o, o.function_def])

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.get_function_def_parameter(),
                                   o.rhs_ast],
                                   reason='Parameter Instantiation')

    def VisitBuiltInFunction(self, o, **kwargs):
        dimensionless_functions = [
                'sin','cos','tan',
                'sinh','cosh','tanh',
                'asin','acos','atan','atan2',
                'exp','ln','log2','log10',
                'pow','ceil','fabs','floor',
                ]
        if o.funcname in dimensionless_functions:
            return

        return
        print 'Dealing with special'
        assert o.funcname in dimensionless_functions

        return
        raise NotImplementedError()

    def VisitOnTransitionTrigger(self, o, **kwargs):
        for a in o.actions:
            self.visit(a)
        self.visit(o.trigger)

    def VisitOnTransitionEvent(self, o, **kwargs):
        for p in o.parameters.values():
            self.visit(p)

    def VisitEmitEvent(self, o, **kwargs):
        pass

    def VisitOnEventDefParameter(self, o, **kwargs):
        pass


class PropogateDimensions(object):

    @classmethod
    def propogate_dimensions(cls, eqnset):

        VerifyUnitsInTree(eqnset, unknown_ok=True)

        labels = None

        all_symbols = ASTVisitorCollectorAll(eqnset).objects
        obj_with_dimension = [s for s in all_symbols if isinstance(s, ast.ASTExpressionObject)]


        # Action, lets walk over the tree and try and resolve the dimensions:
        try:
            uR = DimensionResolver(ast=eqnset, obj_label_dict=labels)

            while True:
                nUnresolvedPre = len([s for s in obj_with_dimension if not s.is_dimension_known()])
                #res_symbols = [uR.visit(s) for s in all_symbols]
                for s in all_symbols:
                    # print s
                    uR.visit(s)
                nUnresolvedPost = len([s for s in obj_with_dimension if not s.is_dimension_known()])

                if nUnresolvedPre == nUnresolvedPost:
                    break
        except UnitMismatchError, e:

            raise

            # print 'Error with: '
            # print ' - ', labels[e.objA], "Unit:", e.objA.get_dimension()
            # print ' - ', labels[e.objB], "Unit:", e.objB.get_dimension()
            # print
            # s1 = StringWriterVisitor().visit(e.objA)
            # s2 = StringWriterVisitor().visit(e.objB)
            # print 'S1:', s1
            # print 'S2:',  s2
            # #assert False
            # raise

        # Look for unresolved symbols:
        symbols_without_dimension = [s for s in all_symbols if isinstance(s, ast.ASTExpressionObject) and not s.is_dimension_known()]
        if symbols_without_dimension:
            print 'Unable to resolve the dimensions of the following symbols:'
            for s in symbols_without_dimension:
                try:
                    print '\tObj:', type(s), s,
                    print '\t  -',
                    print '\t', s.symbol
                except:
                    pass
                    print
            print
            assert False

        VerifyUnitsInTree(eqnset, unknown_ok=False)


