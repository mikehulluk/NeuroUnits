

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
        return expr

        return """CHECK_IN_RANGE_NODE(%s, IntType(%d), %g, %g, "%s")""" %(
                    expr,
                    node.annotations['fixed-point-format'].upscale,
                    node.annotations['node-value-range'].min,
                    node.annotations['node-value-range'].max,
                    repr(node)+str(node)+' ID: ' + str(node.annotations['node-id'])
                )

    def to_c(self, obj, population_access_index=None, data_prefix=None, for_bluevec=False):
        population_access_index_prev = self.population_access_index
        self.population_access_index = population_access_index
        data_prefix_prev = self.data_prefix
        self.data_prefix = data_prefix
        res =  self.visit(obj, for_bluevec=for_bluevec)
        self.population_access_index = population_access_index_prev
        self.data_prefix = data_prefix_prev
        return res

    def VisitRegimeDispatchMap(self, o, **kwargs):
        assert len (o.rhs_map) == 1
        return self.add_range_check(o, self.visit(o.rhs_map.values()[0], **kwargs) )


    def DoOpOpComplex(self, o, op, **kwargs):

        expr_lhs = self.visit(o.lhs, **kwargs)
        expr_rhs = self.visit(o.rhs, **kwargs)
        res = "ScalarOp<%d>::%s( %s, %s )" % (
                                            o.annotations['fixed-point-format'].upscale,
                                            op,
                                            expr_lhs,
                                            expr_rhs,
                                                     )
        return self.add_range_check(o, res)


    def VisitAddOp(self, o, **kwargs):
        res = self.DoOpOpComplex(o, 'add', **kwargs)
        return self.add_range_check(o, res)

    def VisitSubOp(self, o, **kwargs):
        res = self.DoOpOpComplex(o, 'sub', **kwargs)
        return self.add_range_check(o, res)

    def VisitMulOp(self, o, **kwargs):
        res = self.DoOpOpComplex(o, 'mul', **kwargs)
        return self.add_range_check(o, res)

    def VisitDivOp(self, o, **kwargs):
        res = self.DoOpOpComplex(o, 'div', **kwargs)
        return self.add_range_check(o, res)




    def _VisitIfThenElse(self, o, **kwargs):


        L = " ( (%s) ? (%s).rescale_to<%d>() :  (%s).rescale_to<%d>() )" % (
                    self.visit(o.predicate, for_bluevec=False, **kwargs),
                    self.visit(o.if_true_ast, for_bluevec=False, **kwargs),
                    o.annotations['fixed-point-format'].upscale,
                    self.visit(o.if_false_ast, for_bluevec=False, **kwargs),
                    o.annotations['fixed-point-format'].upscale,
                    )
        return self.add_range_check(o, L)


    def VisitIfThenElse(self, o, for_bluevec, **kwargs):

        if not for_bluevec:
            return self._VisitIfThenElse(o, **kwargs)



        # For BlueVec:
        L = "ScalarType<%d>( do_ifthenelse_op(%s, %s, %d, %s, %d ) )"

        res = L % (
                    o.annotations['fixed-point-format'].upscale,
                    self.visit(o.predicate, for_bluevec=for_bluevec, **kwargs),
                    self.visit(o.if_true_ast, for_bluevec=for_bluevec, **kwargs),
                    -1* (o.annotations['fixed-point-format'].upscale - o.if_true_ast.annotations['fixed-point-format'].upscale),
                    self.visit(o.if_false_ast, for_bluevec=for_bluevec, **kwargs),
                    -1* (o.annotations['fixed-point-format'].upscale - o.if_false_ast.annotations['fixed-point-format'].upscale),
                )
        return self.add_range_check(o, res)



    def VisitInEquality(self, o, **kwargs):
        ann_lt_upscale = o.lesser_than.annotations['fixed-point-format'].upscale
        ann_gt_upscale = o.greater_than.annotations['fixed-point-format'].upscale

        if ann_lt_upscale < ann_gt_upscale:
            res= "( ((%s).to_int() >>IntType(%d)) < ( (%s).to_int()) )" %( self.visit(o.lesser_than, **kwargs), (ann_gt_upscale-ann_lt_upscale),  self.visit(o.greater_than, **kwargs) )
        elif ann_lt_upscale > ann_gt_upscale:
            res= "( (%s).to_int() < ( (%s).to_int() >>IntType(%d)))" %( self.visit(o.lesser_than, **kwargs), self.visit(o.greater_than, **kwargs), (ann_lt_upscale-ann_gt_upscale) )
        else:
            res= "( (%s).to_int() < (%s).to_int() )" %( self.visit(o.lesser_than, **kwargs), self.visit(o.greater_than, **kwargs) )
        return res



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

    def VisitFunctionDefBuiltInInstantiation(self,o, for_bluevec, **kwargs):
        assert o.function_def.is_builtin() and o.function_def.funcname == '__exp__'

        param = o.parameters.values()[0]
        param_term = self.visit(param.rhs_ast, for_bluevec=for_bluevec, **kwargs)
        res = """ ScalarOp<%d>::exp( %s )""" %(o.annotations['fixed-point-format'].upscale, param_term)
        return res


    def VisitFunctionDefInstantiationParameter(self, o):
        assert False
        res = o.symbol
        return self.add_range_check(o, res)



    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        res =  "(%s).rescale_to<NrnPopData::T_%s::UP>()" % (
                self.visit(o.rhs_map, **kwargs),
                o.lhs.symbol
                )
        return res



    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        delta_upscale = o.lhs.annotations['fixed-point-format'].delta_upscale
        c1 = "ScalarOp<%d>::mul(%s , dt_fixed) " % (
                delta_upscale,
                self.visit(o.rhs_map, **kwargs),
                )

        c2 = ''
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
        res = "ScalarType<%d>(%d)" % (
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitAssignedVariable(self, o, **kwargs):
        res = self.get_var_str(o.symbol)
        return self.add_range_check(o, res)

    def VisitConstant(self, o, **kwargs):
        res = "ScalarType<%d>(%d)" % (
                o.annotations['fixed-point-format'].upscale,
                o.annotations['fixed-point-format'].const_value_as_int )
        return self.add_range_check(o, res)

    def VisitConstantZero(self, o, **kwargs):
        res = "ScalarType<0>(0)"
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
        print 'AR updscale: ', o.annotations['fixed-point-format'].upscale

        # Upscaling of the coefficients, (by default probably between zero and 1

        node_name = 'AR%s' % o.annotations['node-id']
        node_upscale = o.annotations['fixed-point-format'].upscale


        rhs = "ScalarType<0>(0) "
        for i,coeff_as_int in enumerate(o.annotations['fixed-point-format'].coeffs_as_consts):
            i_prev_value_name = "d._%s_t%d[i]" % (node_name, i)

            rhs_term = "ScalarOp<%d>::mul( %s, ScalarType<%d>(%d) )" %(
                        node_upscale,
                        i_prev_value_name,
                        o.annotations['fixed-point-format'].coefficient_upscale,
                        coeff_as_int)

            rhs = """ScalarOp<%d>::add(%s, %s) """ % (node_upscale, rhs, rhs_term)


        # Lets add the random bit:
        # USE uniform random numbers (hack!) should be gaussian:

        res = """ScalarOp<%d>::add( 
                    ScalarType<0>( rnd::rand_kiss()-((1>>7)*2 >> 8)), 
                    %s )  """ % (
                    node_upscale,
                    rhs,
                )


        return res

    def VisitAutoRegressiveModel(self, o, **kwargs):
        node_name = 'AR%s' % o.annotations['node-id']
        return self.get_var_str( node_name )


    def VisitOnEventStateAssignment(self, o, **kwargs):

        res =  "%s = (%s).rescale_to<NrnPopData::T_%s::UP>()" % (
                self.get_var_str(o.lhs.symbol),
                self.visit(o.rhs, **kwargs),
                o.lhs.symbol
                )
        return res


    def VisitEmitEvent(self, o, **kwargs):
        return 'event_handlers::on_%s(IntType(i), time_info)'% o.port.symbol


    def VisitOnEventDefParameter(self, o, **kwargs):
        return 'evt.%s' % o.symbol

















