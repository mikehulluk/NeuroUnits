

import mako
from mako.template import Template

from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np

import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase




#class IntermediateNodeFinder(ASTActionerDefaultIgnoreMissing):
#
#    def __init__(self, component):
#        self.valid_nodes = {}
#        super(IntermediateNodeFinder,self).__init__(component=component)
#
#    # How many values do we store per operation:
#    def ActionAddOp(self, o, **kwargs):
#        self.valid_nodes[o] = 3
#
#    def ActionSubOp(self, o, **kwargs):
#        self.valid_nodes[o] = 3
#
#    def ActionMulOp(self, o, **kwargs):
#        self.valid_nodes[o] = 3
#
#    def ActionDivOp(self, o, **kwargs):
#        self.valid_nodes[o] = 3
#
#    def ActionExpOp(self, o, **kwargs):
#        assert False
#        self.valid_nodes[o] = 3
#
#    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
#        assert o.function_def.funcname in ['__exp__', '__ln__']
#        self.valid_nodes[o] = 2
#
#    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
#        assert False








class CBasedFixedWriterStd(ASTVisitorBase):

    def to_c(self, obj, population_access_index=None, data_prefix=None):
        population_access_index_prev = self.population_access_index
        self.population_access_index = population_access_index
        data_prefix_prev = self.data_prefix
        self.data_prefix = data_prefix

        res =  self.visit(obj)


        self.population_access_index = population_access_index_prev
        self.data_prefix = data_prefix_prev

        return res

    def VisitRegimeDispatchMap(self, o, **kwargs):
        assert len (o.rhs_map) == 1
        return self.add_range_check(o, self.visit(o.rhs_map.values()[0], **kwargs) )


    def DoOpOpComplex(self, o, op, **kwargs):

        expr_lhs = self.visit(o.lhs, **kwargs)
        expr_rhs = self.visit(o.rhs, **kwargs)
        res = "%s<%d>::%s( %s, %s )" % (    self.op_scalar_op,
                                            o.annotations['fixed-point-format'].upscale,
                                            op,
                                            expr_lhs,
                                            expr_rhs,
                                                     )
        return self.add_range_check(o, res)


    def VisitAddOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'add', **kwargs)

    def VisitSubOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'sub', **kwargs)

    def VisitMulOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'mul', **kwargs)

    def VisitDivOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'div', **kwargs)






    def VisitIfThenElse(self, o, **kwargs):
        L = " ( (%s) ? (%s).rescale_to<%d>() :  (%s).rescale_to<%d>() )" % (
                    self.visit(o.predicate,  **kwargs),
                    self.visit(o.if_true_ast,  **kwargs),
                    o.annotations['fixed-point-format'].upscale,
                    self.visit(o.if_false_ast, **kwargs),
                    o.annotations['fixed-point-format'].upscale,
                    )
        return self.add_range_check(o, L)





    def _VisitOnConditionCrossing(self, o, **kwargs):
        return " ( (%s) < (%s) )" % (
                self.visit(o.crosses_lhs, **kwargs),
                self.visit(o.crosses_rhs, **kwargs),
                )




    def VisitInEquality(self, o, **kwargs):
        return " ( (%s) < (%s) )" % (
                self.visit(o.lesser_than, **kwargs),
                self.visit(o.greater_than, **kwargs),
                )



    def VisitOnConditionCrossing(self, o, **kwargs):
        node_name = "d.C_%s_lhs_is_gt_rhs[i]" % o.annotations['node-id']
        node_name_prev = "d.C_%s_lhs_is_gt_rhs_prev[i]" % o.annotations['node-id']
        expr = None
        if o.on_rising and o.on_falling:
            expr = "(%s != %s)" % (node_name_prev, node_name)
        elif o.on_rising and not o.on_falling:
            expr = "((%s == false) && (%s==true))" % (node_name_prev, node_name)
        elif not o.on_rising and o.on_falling:
            expr = "((%s == true) && (%s==false))" % (node_name_prev, node_name)
        else:
            assert False


        return "(is_condition_activation_guard && %s)" % expr


    def VisitBoolAnd(self, o, **kwargs):
        res = " ((%s) && (%s))"% (self.visit(o.lhs, **kwargs), self.visit(o.rhs, **kwargs))
        return res
    def VisitBoolOr(self, o, **kwargs):
        res = " ((%s) || (%s))"% (self.visit(o.lhs, **kwargs), self.visit(o.rhs, **kwargs))
        return res
    def VisitBoolNot(self, o, **kwargs):
        res = " (!(%s))"% (self.visit(o.lhs, **kwargs))
        return res

    def VisitFunctionDefUserInstantiation(self,o):
        assert False

    def VisitFunctionDefBuiltInInstantiation(self,o,  **kwargs):
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'

        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast, **kwargs)
        res = """ ScalarOp<%d>::exp( %s )""" %(o.annotations['fixed-point-format'].upscale, param_term)
        return res


    def VisitFunctionDefInstantiationParameter(self, o):
        assert False
        res = o.symbol
        return self.add_range_check(o, res)



    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        res =  "(%s)" % self.visit(o.rhs_map, **kwargs)
        return res



    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        delta_upscale = o.lhs.annotations['fixed-point-format'].delta_upscale
        c1 = "%s<%d>::mul(%s , dt_fixed) " % (
                self.op_scalar_op,
                delta_upscale,
                self.visit(o.rhs_map, **kwargs),
                )

        c2 = ''
        return c1, c2








class CBasedFixedWriter(CBasedFixedWriterStd):

    def add_range_check(self, o, res ):
        return res


    def __init__(self, component, population_access_index=None, data_prefix=None ):
        super(CBasedFixedWriter, self).__init__()
        self.population_access_index=population_access_index
        self.data_prefix=data_prefix


        self.op_scalar_type = 'ScalarType'
        self.op_scalar_op = 'ScalarOp'

    def get_var_str(self, name):
        s = name
        if self.data_prefix:
            s = self.data_prefix + s
        if self.population_access_index!=None:
            s += '[%s]'%self.population_access_index
        return s


    def VisitFunctionDefParameter(self, o, **kwargs):
        assert False
        res = o.symbol
        return self.add_range_check(o, res)

    def VisitStateVariable(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitParameter(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitSymbolicConstant(self, o, **kwargs):
        res = "%s<%d>(%d)" % (
                self.op_scalar_type,
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitAssignedVariable(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitConstant(self, o, **kwargs):
        res = "%s<%d>(%d)" % (
                self.op_scalar_type,
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitConstantZero(self, o, **kwargs):
        res = "%s<0>(0)" %(self.op_scalar_type)
        return self.add_range_check(o, res)


    def VisitSuppliedValue(self, o, **kwargs):
        return self.get_var_str(o.symbol)


    def VisitTimeVariable(self, o, **kwargs):
        return 't'






    def VisitRandomVariable(self, o, **kwargs):

        assert o.modes['when'] in ('SIM_INIT')
        assert o.modes['share'] in ('PER_NEURON', 'PER_POPULATION')

        node_name = 'RV%s' % o.annotations['node-id']

        if o.modes['share'] =='PER_NEURON':
            res = self.get_var_str( name=node_name) #'d.%s[i]' % node_name
        elif o.modes['share'] == 'PER_POPULATION':
            res = 'd.%s' % node_name
        else:
            assert False

        return self.add_range_check(o, res)


    def VisitAutoRegressiveModelUpdate(self, o, **kwargs):
        print 'AR upscale: ', o.annotations['fixed-point-format'].upscale

        # Upscaling of the coefficients, (by default probably between zero and 1

        node_name = 'AR%s' % o.annotations['node-id']
        node_upscale = o.annotations['fixed-point-format'].upscale


        rhs = "%s<0>(0) " % self.op_scalar_type
        for i,coeff_as_int in enumerate(o.annotations['fixed-point-format'].coeffs_as_consts):
            i_prev_value_name = "d._%s_t%d[i]" % (node_name, i)

            rhs_term = "%s<%d>::mul( %s, ScalarType<%d>(%d) )" %(
                        self.op_scalar_op,
                        node_upscale,
                        i_prev_value_name,
                        o.annotations['fixed-point-format'].coefficient_upscale,
                        coeff_as_int)

            rhs = """%s<%d>::add(%s, %s) """ % (
                    self.op_scalar_op,
                    node_upscale,
                    rhs,
                    rhs_term)


        # Lets add the random bit:
        # USE uniform random numbers (hack!) should be gaussian:

        #ScalarType<0>( rnd::rand_kiss()-((1>>7)*2 >> 8)),
        #//- (1<<24)
        res = """%s<%d>::add(
                    %s<0>( ((int) rnd::rand_kiss() ) - (1<<23) ),
                    %s )  """ % (
                    self.op_scalar_op,
                    node_upscale,
                    self.op_scalar_type,
                    rhs,
                )


        return res

    def VisitAutoRegressiveModel(self, o, **kwargs):
        node_name = 'AR%s' % o.annotations['node-id']
        return self.get_var_str( node_name )


    def VisitOnEventStateAssignment(self, o, **kwargs):

        res =  "%s = (%s)" % (
                self.get_var_str(o.lhs.symbol),
                self.visit(o.rhs, **kwargs),
                )
        return res


    def VisitEmitEvent(self, o, **kwargs):
        return 'event_handlers::on_%s(IntType(i), time_info)'% o.port.symbol


    def VisitOnEventDefParameter(self, o, **kwargs):
        return 'evt.%s' % o.symbol















class CBasedFixedWriterBlueVecOps(ASTVisitorBase):
#class CBasedFixedWriterBlueVecOps(CBasedFixedWriterStd):

    def add_range_check(self, o, res):
        return res

    def __init__(self, component, population_access_index=None, data_prefix='bv_' ):
        super(CBasedFixedWriterBlueVecOps, self).__init__()
        self.population_access_index=population_access_index
        self.data_prefix=data_prefix


        self.op_scalar_type = 'FixedPointStream'
        self.op_scalar_op = 'FixedPointStreamOp'


    def to_c(self, obj, population_access_index=None, data_prefix='bv_', ):
        population_access_index_prev = self.population_access_index
        self.population_access_index = population_access_index
        data_prefix_prev = self.data_prefix
        self.data_prefix = data_prefix

        res =  self.visit(obj)


        self.population_access_index = population_access_index_prev
        self.data_prefix = data_prefix_prev

        return res

    def VisitEqnAssignmentByRegime(self, o):
        return "(%s)" % (
                    self.visit(o.rhs_map),
                    )

    def VisitRegimeDispatchMap(self, o, **kwargs):
        assert len (o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0], **kwargs)



    def DoOpOpComplex(self, o, op, **kwargs):

        expr_lhs = self.visit(o.lhs, **kwargs)
        expr_rhs = self.visit(o.rhs, **kwargs)
        res = "%s<%d>::%s( %s, %s )" % (    self.op_scalar_op,
                                            o.annotations['fixed-point-format'].upscale,
                                            op,
                                            expr_lhs,
                                            expr_rhs,
                                                     )
        return self.add_range_check(o, res)


    def VisitAddOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'add', **kwargs)

    def VisitSubOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'sub', **kwargs)

    def VisitMulOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'mul', **kwargs)

    def VisitDivOp(self, o, **kwargs):
        return self.DoOpOpComplex(o, 'div', **kwargs)


    def VisitSymbolicConstant(self, o, **kwargs):
        res = "%s<%d>(%d)" % (
                self.op_scalar_type,
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitAssignedVariable(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitConstant(self, o, **kwargs):
        res = "%s<%d>(%d)" % (
                self.op_scalar_type,
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitConstantZero(self, o, **kwargs):
        res = "%s<0>(0)" %(self.op_scalar_type)
        return self.add_range_check(o, res)

    
    def VisitParameter(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitSuppliedValue(self, o, **kwargs):
        return self.get_var_str(o.symbol)


    def VisitTimeVariable(self, o, **kwargs):
        return 'bv_t'
    def VisitStateVariable(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitRandomVariable(self, o, **kwargs):

        assert o.modes['when'] in ('SIM_INIT')
        assert o.modes['share'] in ('PER_NEURON', 'PER_POPULATION')

        node_name = 'RV%s' % o.annotations['node-id']

        if o.modes['share'] =='PER_NEURON':
            res = self.get_var_str( name=node_name) #'d.%s[i]' % node_name
        elif o.modes['share'] == 'PER_POPULATION':
            res = 'd.%s' % node_name
        else:
            assert False

        return self.add_range_check(o, res)

    def VisitFunctionDefBuiltInInstantiation(self,o,  **kwargs):
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'

        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast, **kwargs)
        res = """ %s<%d>::exp( %s )""" %( 
                self.op_scalar_op,
                o.annotations['fixed-point-format'].upscale, 
                param_term)
        return res


    def get_var_str(self, name):
        s = name
        if self.data_prefix:
            s = self.data_prefix + s
        if self.population_access_index!=None:
            s += '[%s]'%self.population_access_index
        return s



    def VisitIfThenElse(self, o, **kwargs):
        #L = " ( (%s) ? (%s).rescale_to<%d>() :  (%s).rescale_to<%d>() )" % (
        L = "  %s<%d>::ifthenelse(%s, %s,  %s)" % (
                    self.op_scalar_op,
                    o.annotations['fixed-point-format'].upscale,
                    self.visit(o.predicate,  **kwargs),
                    self.visit(o.if_true_ast,  **kwargs),
                    #o.annotations['fixed-point-format'].upscale,
                    self.visit(o.if_false_ast, **kwargs),
                    #o.annotations['fixed-point-format'].upscale,
                    )
        return self.add_range_check(o, L)


    def VisitInEquality(self, o, **kwargs):
        return " ( (%s) < (%s) )" % (
                self.visit(o.lesser_than, **kwargs),
                self.visit(o.greater_than, **kwargs),
                )


    def VisitOnConditionCrossing(self, o, **kwargs):
        node_name = "d.C_%s_lhs_is_gt_rhs[i]" % o.annotations['node-id']
        node_name_prev = "d.C_%s_lhs_is_gt_rhs_prev[i]" % o.annotations['node-id']
        expr = None
        if o.on_rising and o.on_falling:
            expr = "(%s != %s)" % (node_name_prev, node_name)
        elif o.on_rising and not o.on_falling:
            expr = "((%s == false) && (%s==true))" % (node_name_prev, node_name)
        elif not o.on_rising and o.on_falling:
            expr = "((%s == true) && (%s==false))" % (node_name_prev, node_name)
        else:
            assert False


        return "(is_condition_activation_guard && %s)" % expr


    def VisitBoolAnd(self, o, **kwargs):
        res = " ((%s) && (%s))"% (self.visit(o.lhs, **kwargs), self.visit(o.rhs, **kwargs))
        return res
    def VisitBoolOr(self, o, **kwargs):
        res = " ((%s) || (%s))"% (self.visit(o.lhs, **kwargs), self.visit(o.rhs, **kwargs))
        return res
    def VisitBoolNot(self, o, **kwargs):
        res = " (!(%s))"% (self.visit(o.lhs, **kwargs))
        return res


    def VisitAutoRegressiveModel(self, o, **kwargs):
        node_name = 'AR%s' % o.annotations['node-id']
        return self.get_var_str( node_name )



