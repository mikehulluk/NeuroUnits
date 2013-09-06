

import mako
from mako.template import Template

from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing


import numpy as np

import os
from neurounits.visitors.bases.base_visitor import ASTVisitorBase



#class Eqn(object):
#    def __init__(self, node, rhs_cstr):
#        self.node = node
#        self.rhs_cstr = rhs_cstr

class IntermediateNodeFinder(ASTActionerDefaultIgnoreMissing):

    def __init__(self, component):
        self.valid_nodes = {}
        super(IntermediateNodeFinder,self).__init__(component=component)

    # How many values do we store per operation:
    def ActionAddOp(self, o, **kwargs):
        self.valid_nodes[o] = 3

    def ActionSubOp(self, o, **kwargs):
        self.valid_nodes[o] = 3

    def ActionMulOp(self, o, **kwargs):
        self.valid_nodes[o] = 3

    def ActionDivOp(self, o, **kwargs):
        self.valid_nodes[o] = 3

    def ActionExpOp(self, o, **kwargs):
        assert False
        self.valid_nodes[o] = 3

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        assert o.function_def.funcname in ['__exp__', '__ln__']
        self.valid_nodes[o] = 2

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        assert False








class CBasedFixedWriterStd(ASTVisitorBase):
    def add_range_check(self, node, expr):

        return """CHECK_IN_RANGE_NODE(%s, IntType(%d), %g, %g, "%s")""" %(
                    expr,
                    node.annotations['fixed-point-format'].upscale,
                    node.annotations['node-value-range'].min,
                    node.annotations['node-value-range'].max,
                    repr(node)+str(node)+' ID: ' + str(node.annotations['node-id'])
                )

    def to_c(self, obj, population_access_index=None, data_prefix=None):
        population_access_index_prev = self.population_access_index
        self.population_access_index = population_access_index
        data_prefix_prev = self.data_prefix
        self.data_prefix = data_prefix
        res =  self.visit(obj)
        self.population_access_index = population_access_index_prev
        self.data_prefix = data_prefix_prev
        return res

    def VisitRegimeDispatchMap(self, o):
        assert len (o.rhs_map) == 1
        return self.add_range_check(o, self.visit(o.rhs_map.values()[0]) )


    def DoOpOpComplex(self, o, op):

        expr_lhs = self.visit(o.lhs)
        expr_rhs = self.visit(o.rhs)
        expr_num = o.annotations['node-id']
        res = "do_%s_op( %s, IntType(%d), %s, IntType(%d), IntType(%d), IntType(%d))" % (
                                            op,
                                            expr_lhs, o.lhs.annotations['fixed-point-format'].upscale,
                                            expr_rhs, o.rhs.annotations['fixed-point-format'].upscale,
                                            o.annotations['fixed-point-format'].upscale,
                                            expr_num,
                                                     )
        return self.add_range_check(o, res)


    def VisitAddOp(self, o):
        res = self.DoOpOpComplex(o, 'add')
        return self.add_range_check(o, res)

    def VisitSubOp(self, o):
        res = self.DoOpOpComplex(o, 'sub')
        return self.add_range_check(o, res)

    def VisitMulOp(self, o):
        res = self.DoOpOpComplex(o, 'mul')
        return self.add_range_check(o, res)

    def VisitDivOp(self, o):
        res = self.DoOpOpComplex(o, 'div')
        return self.add_range_check(o, res)




    def VisitIfThenElse(self, o):
        res = "( (%s) ? auto_shift(%s, IntType(%d)) : auto_shift(%s, IntType(%d)) )" % (
                    self.visit(o.predicate),
                    self.visit(o.if_true_ast),
                    -1* (o.annotations['fixed-point-format'].upscale - o.if_true_ast.annotations['fixed-point-format'].upscale),
                    self.visit(o.if_false_ast),
                    -1* (o.annotations['fixed-point-format'].upscale - o.if_false_ast.annotations['fixed-point-format'].upscale),
                )
        return self.add_range_check(o, res)

    def VisitInEquality(self, o):
        ann_lt_upscale = o.lesser_than.annotations['fixed-point-format'].upscale
        ann_gt_upscale = o.greater_than.annotations['fixed-point-format'].upscale

        if ann_lt_upscale < ann_gt_upscale:
            res= "( ((%s)>>IntType(%d)) < ( (%s)) )" %( self.visit(o.lesser_than), (ann_gt_upscale-ann_lt_upscale),  self.visit(o.greater_than) )
        elif ann_lt_upscale > ann_gt_upscale:
            res= "( (%s) < ( (%s)>>IntType(%d)))" %( self.visit(o.lesser_than), self.visit(o.greater_than), (ann_lt_upscale-ann_gt_upscale) )
        else:
            res= "( (%s) < (%s) )" %( self.visit(o.lesser_than), self.visit(o.greater_than) )
        return res



    def VisitBoolAnd(self, o):
        res = " ((%s) && (%s))"% (self.visit(o.lhs), self.visit(o.rhs))
        return res
    def VisitBoolOr(self, o):
        res = " ((%s) || (%s))"% (self.visit(o.lhs), self.visit(o.rhs))
        return res
    def VisitBoolNot(self, o):
        res = " (!(%s))"% (self.visit(o.lhs))
        return res

    def VisitFunctionDefUserInstantiation(self,o):
        assert False

    def VisitFunctionDefBuiltInInstantiation(self,o):
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'
        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast)

        # Add range checking:
        param_term = self.add_range_check(param, param_term)
        ann_func_upscale = o.annotations['fixed-point-format'].upscale
        ann_param_upscale = param.rhs_ast.annotations['fixed-point-format'].upscale
        expr_num = o.annotations['node-id']
        res = """ int_exp( %s, IntType(%d), IntType(%d), IntType(%d) )""" %(param_term, ann_param_upscale, ann_func_upscale, expr_num )
        return self.add_range_check(o, res)

    def VisitFunctionDefInstantiationParameter(self, o):
        assert False
        res = o.symbol
        return self.add_range_check(o, res)

    def VisitEqnAssignmentByRegime(self, o):
        rhs_c = self.visit(o.rhs_map)
        res =  " auto_shift( %s, IntType(%d) )" % (rhs_c, o.rhs_map.annotations['fixed-point-format'].upscale - o.lhs.annotations['fixed-point-format'].upscale )
        return res


    def VisitTimeDerivativeByRegime(self, o):
        delta_upscale = o.lhs.annotations['fixed-point-format'].delta_upscale
        c1 = "do_mul_op(%s , IntType( %d ), dt_int, IntType(dt_upscale), IntType(%d), IntType(-1) ) " % ( self.visit(o.rhs_map), o.rhs_map.annotations['fixed-point-format'].upscale, delta_upscale  )
        c2 = "auto_shift( d_%s, IntType(%d) - IntType(%d) )" % ( o.lhs.symbol, delta_upscale, o.lhs.annotations['fixed-point-format'].upscale)
        return c1, c2






class CBasedFixedWriter(CBasedFixedWriterStd):

    def __init__(self, component, population_access_index=None, data_prefix=None ):
        super(CBasedFixedWriter, self).__init__()
        self.population_access_index=population_access_index
        self.data_prefix=data_prefix

    def get_var_str(self, name):
        s = name
        if self.data_prefix:
            s = self.data_prefix + s
        if self.population_access_index!=None:
            s += '[%s]'%self.population_access_index
        return s


    def VisitFunctionDefParameter(self, o):
        assert False
        res = o.symbol
        return self.add_range_check(o, res)

    def VisitStateVariable(self, o):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitParameter(self, o):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitSymbolicConstant(self, o):
        res = "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int
        return self.add_range_check(o, res)

    def VisitAssignedVariable(self, o):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitConstant(self, o):
        res = "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int
        return self.add_range_check(o, res)

    def VisitConstantZero(self, o):
        res = "IntType(0)"
        return self.add_range_check(o, res)


    def VisitSuppliedValue(self, o):
        if o.symbol == 't':
            return 't'
        return self.get_var_str(o.symbol)



    def VisitRandomVariable(self, o):

        assert o.modes['when'] in ('SIM_INIT')
        assert o.modes['share'] in ('PER_NEURON', 'PER_POPULATION')

        node_name = 'RV%s' % o.annotations['node-id']

        if o.modes['share'] =='PER_NEURON':
            res = 'd.%s[i]' % node_name
        elif o.modes['share'] == 'PER_POPULATION':
            res = 'd.%s' % node_name
        else:
            assert False


        return self.add_range_check(o, res)


    def VisitOnEventStateAssignment(self, o):
        rhs_c = self.visit(o.rhs)
        rhs_str = "%s = auto_shift( %s, IntType(%d) )" % (
                self.get_var_str(o.lhs.symbol),
                rhs_c, o.rhs.annotations['fixed-point-format'].upscale - o.lhs.annotations['fixed-point-format'].upscale )
        return rhs_str

    def VisitEmitEvent(self, o):
        return 'event_handlers::on_%s(IntType(i), time_info)'% o.port.symbol


    def VisitOnEventDefParameter(self, o):
        return 'evt.%s' % o.symbol

















#class CBasedFixedWriterBlueVec(CBasedFixedWriterStd):
#
#    def __init__(self, component):
#        super(CBasedFixedWriterBlueVec, self).__init__()
#        #self.population_access_index=population_access_index
#
#    def get_var_str(self, name):
#        s =  "d.%s" % name
#        if self.population_access_index!=None:
#            s += '[%s]'%self.population_access_index
#        return s
#
#
#    def VisitFunctionDefParameter(self, o):
#        assert False
#        res = o.symbol
#        return self.add_range_check(o, res)
#
#    def VisitStateVariable(self, o):
#        res = self.get_var_str(o.symbol)
#        return self.add_range_check(o, res)
#
#    def VisitParameter(self, o):
#        res = self.get_var_str(o.symbol)
#        return self.add_range_check(o, res)
#
#    def VisitSymbolicConstant(self, o):
#        res = "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int
#        return self.add_range_check(o, res)
#
#    def VisitAssignedVariable(self, o):
#        res = self.get_var_str(o.symbol)
#        return self.add_range_check(o, res)
#
#    def VisitConstant(self, o):
#        res = "IntType(%d)" % o.annotations['fixed-point-format'].const_value_as_int
#        return self.add_range_check(o, res)
#
#    def VisitConstantZero(self, o):
#        res = "IntType(0)"
#        return self.add_range_check(o, res)
#
#
#    def VisitSuppliedValue(self, o):
#        if o.symbol == 't':
#            return 't'
#        return self.get_var_str(o.symbol)
#
#
#
#    def VisitRandomVariable(self, o):
#
#        assert o.modes['when'] in ('SIM_INIT')
#        assert o.modes['share'] in ('PER_NEURON', 'PER_POPULATION')
#
#        node_name = 'RV%s' % o.annotations['node-id']
#
#        if o.modes['share'] =='PER_NEURON':
#            res = 'd.%s[i]' % node_name
#        elif o.modes['share'] == 'PER_POPULATION':
#            res = 'd.%s' % node_name
#        else:
#            assert False
#
#
#        return self.add_range_check(o, res)
#
#
#    def VisitOnEventStateAssignment(self, o):
#        rhs_c = self.visit(o.rhs)
#        rhs_str = "%s = auto_shift( %s, IntType(%d) )" % (
#                self.get_var_str(o.lhs.symbol),
#                rhs_c, o.rhs.annotations['fixed-point-format'].upscale - o.lhs.annotations['fixed-point-format'].upscale )
#        return rhs_str
#
#    def VisitEmitEvent(self, o):
#        return 'event_handlers::on_%s(IntType(i), time_info)'% o.port.symbol
#
#
#    def VisitOnEventDefParameter(self, o):
#        return 'evt.%s' % o.symbol
