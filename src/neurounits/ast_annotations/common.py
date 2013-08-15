



from neurounits.ast_annotations.bases import ASTNodeAnnotationData, ASTTreeAnnotationManager, ASTTreeAnnotator
#from neurounits.Zdev.fixed_point_annotations import VarAnnot, ASTDataAnnotator#, CalculateInternalStoragePerNode
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault

import numpy as np
import neurounits

import numpy as np
import pylab
from neurounits.units_backends.mh import MMQuantity, MMUnit
from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits import ast
from neurounits import NeuroUnitParser



import itertools


import operator
def do_op(a,b,op):
    if a is None or b is None:
        return None

    return op(a,b)
    #except ZeroDivisionError:
    #    assert False
    #    return None








#propagation_rules = """
#
#AddOp [self.min <= lhs.min + rhs.min], [self.rhs <= self.min - rhs.min], [self.lhs <= self.min - lhs.min]
#
#
#"""


def check_array_returned(func):
    def new_func(*args,**kwargs):
        array = func(*args,**kwargs)
        #print func
        assert isinstance(array, np.ndarray)
        return array
    return new_func

class LargeArrayPropagator(ASTVisitorBase):
    def __init__(self, component, assignment_node, sv_order, sv_values):
        """sv_order - list of terminal
           sv_values - dictionary mapping terminals to values"""
        self.component = component
        self.sv_order = sv_order
        self.sv_values = sv_values

        #print 'LARGE ARRAY PROPAGATION FOR: ', repr(assignment_node)
        array = self.visit(assignment_node.rhs_map)
        #print assignment_node.rhs_map
        #print array

        assert isinstance(array, np.ndarray)
        #print array

        min_val = np.min(array)
        max_val = np.max(array)

        print 'For %s, min/max are: %s %s' %(repr(assignment_node), min_val, max_val)

        #assert False

    @check_array_returned
    def VisitRegimeDispatchMap(self,o):
        assert len(o.rhs_map) == 1
        r = self.visit( list(o.rhs_map.values())[0] )

        return r

    @check_array_returned
    def VisitAddOp(self, o):
        a1 = self.visit(o.lhs)
        a2 = self.visit(o.rhs)
        a3 =  a1+a2
        assert a1.shape == a2.shape
        assert a3.shape == a2.shape
        return a3
    
    @check_array_returned
    def VisitSubOp(self, o):
        a1 = self.visit(o.lhs)
        a2 = self.visit(o.rhs)
        a3 =  a1-a2
        assert a1.shape == a2.shape
        assert a3.shape == a2.shape
        return a3

    @check_array_returned
    def VisitMulOp(self, o):
        a1 = self.visit(o.lhs)
        a2 = self.visit(o.rhs)
        a3 =  a1*a2
        assert a1.shape == a2.shape
        assert a3.shape == a2.shape
        return a3

    @check_array_returned
    def VisitDivOp(self, o):
        a1 = self.visit(o.lhs)
        a2 = self.visit(o.rhs)
        a3 =  a1/a2
        assert a1.shape == a2.shape
        assert a3.shape == a2.shape
        return a3

    @check_array_returned
    def VisitConstant(self, o):
        return self._VisitConstant( o)
    @check_array_returned
    def VisitSymbolicConstant(self, o):
        return self._VisitConstant( o)
    
    @check_array_returned
    def _VisitConstant(self, o):
        # print 'Constructing const-array'
        new_array = np.ones( [len(self.sv_values[sv]) for sv in self.sv_order] ) * o.value.float_in_si()
        #print 'OK!'
        return new_array
        assert False



    @check_array_returned
    def VisitAssignedVariable(self, o):
        '''March straight through assigned variables'''
        return self.visit( self.component._eqn_assignment.get_single_obj_by(lhs=o).rhs_map )



    def _fixed_array(self, o):
        #print 'Building fixed array for:', repr(o)
        #print self.sv_order
        assert o in self.sv_order
        o_vals = self.sv_values[o].copy()
        shape = tuple( [(len(o_vals) if sv==o else 1) for sv in self.sv_order] )
        o_vals = o_vals.reshape( shape ) 
        o_tile = tuple( [(len(self.sv_values[sv]) if sv!=o else 1) for sv in self.sv_order] ) 
        mat = np.tile(o_vals, o_tile)
        return mat

    def VisitStateVariable(self, o):
        return self._fixed_array(o)
    
    def VisitRandomVariable(self, o):
        return self._fixed_array(o)

    def VisitSuppliedValue(self, o):
        return self._fixed_array(o)

    @check_array_returned
    def VisitFunctionDefBuiltInInstantiation(self, o):
        if o.function_def.funcname != '__exp__':
            assert False
        
        p = o.parameters.values()[0]
        a = self.visit(p.rhs_ast)

        return np.exp(a)
        assert False




    def VisitIfThenElse(self, o):
        pred = self.visit(o.predicate)
        if_true = self.visit(o.if_true_ast)
        if_false = self.visit(o.if_false_ast)
        
        res = if_false.copy()
        res[pred] = if_true[pred]

        return res
        #assert False


    def VisitBoolAnd(self, o):
        return np.logical_and( self.visit(o.lhs), self.visit(o.rhs))

    
    def VisitInEquality(self, o):
        a1 = self.visit(o.greater_than)
        a2 = self.visit(o.lesser_than)
        a3 =  a1>a2
        assert a1.shape == a2.shape
        assert a3.shape == a2.shape
        return a3






class NodeValueRangePropagator(ASTVisitorBase):

    def get_annotation(self, node):
        return node.annotations['node-value-range']

    def set_annotation(self, node, ann):
        node.annotations.add_overwrite('node-value-range', ann )
        print 'Setting Annotation:'
        print '  Node: ', node
        print '  Ann:  ', ann

    def has_annotation(self, node):
        return 'node-value-range' in node.annotations


    def __init__(self, component, annotations_in):
        self.component = component

        # Change string to node:
        for ann,val in annotations_in.items():
            if not component.has_terminal_obj(ann):
                continue

            assert isinstance(ann, basestring)
            self.set_annotation(component.get_terminal_obj(ann), val)


        self.visit(component)

    def VisitNineMLComponent(self, component):


        # Constants should be fine:
        for o in component.symbolicconstants:
            self.visit(o)

        # Constants should be fine:
        for o in component.random_variable_nodes:
            self.visit(o)

        # Parameters & supplied values need to have thier ranges supplied:
        for o in list(component.parameters) + list(component.suppliedvalues):
            assert self.has_annotation(o)

        # State varaibles all need an annotation, since this is difficult to infer reliably:
        for o in list(component.state_variables) :
            assert self.has_annotation(o), "Not annotation given for state variable: %s" % o.symbol



        # This now leaves the assignments, and the delta-state variables to calculate:
        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
        deps = VisitorSymbolDependance(component)
        for ass in sorted(component.assignments, key=lambda o:o.lhs.symbol):
            ass_deps = list(deps.get_terminal_dependancies(ass, expand_assignments=True, include_random_variables=True))

            # Work out the values to test for each state variable:
            n_values_tested = 5
            tested_vals = {}
            for sv in ass_deps:
                assert isinstance(sv, (ast.RandomVariable, ast.StateVariable, ast.SuppliedValue))
                tested_vals[sv] = np.linspace( sv.annotations['node-value-range'].min.float_in_si(), sv.annotations['node-value-range'].max.float_in_si(), num=n_values_tested)

            # And propagate the array through the tree!
            LargeArrayPropagator(component=component, assignment_node=ass, sv_order=ass_deps, sv_values=tested_vals)





            #sv_dependancies = component.getSymbolDependancicesIndirect(ass.lhs, include_ass_in_output=False)
            #print sv_dependancies
        #while unresolved_terminals:
        #    node_resolved = False
        #
        #    # Try and resolve symbols:
        #    for terminal in unresolved_terminals:
        #        print 'Trying to resolve terminal:', repr(terminal)
        #        dependancies = component.getSymbolDependancicesDirect(terminal)
        #        print dependancies
        #        unresolved_dependancies = [d for d in dependancies if not self.has_annotation(d)]
        #        print 'Unresolved:', unresolved_dependancies
        #        if not unresolved_dependancies:
        #



        #    if node_resolved==False:
        #        print 'Unable to resolve the ranges of the nodes!'
        #        print unresolved_terminals
        #        assert False


        assert False




    #    for i in range(4):
    #        for o in component.symbolicconstants:
    #            self.visit(o)
    #        for o in component.ordered_assignments_by_dependancies:
    #            self.visit(o)
    #        for o in component.timederivatives:
    #            self.visit(o)
    #        for tr in component.transitions:
    #            self.visit(tr)




    #def VisitEqnAssignmentByRegime(self, o):
    #    self.visit(o.rhs_map)
    #    self.visit(o.lhs)

    #    print repr(o.lhs)
    #    ann_lhs = self.get_annotation(o.lhs)
    #    ann_rhs = self.get_annotation(o.rhs_map)
    #    #ann_rhs = self.annotations[o.rhs_map]

    #    #Min:
    #    if ann_lhs.min is None and  ann_rhs.min is not None:
    #        ann_lhs.min = ann_rhs.min

    #    if ann_lhs.max is None and  ann_rhs.max is not None:
    #        ann_lhs.max = ann_rhs.max




    #def VisitTimeDerivativeByRegime(self, o):
    #    self.visit(o.rhs_map)
    #    self.visit(o.lhs)


    #    #ann_lhs = self.annotations[o.lhs]
    #    #ann_rhs = self.annotations[o.rhs_map]
    #    ann_lhs = self.get_annotation(o.lhs)
    #    ann_rhs = self.get_annotation(o.rhs_map)

    #    # Need to be a bit careful here - because  rememeber that rhs is multiplied by dt!

    #    ## Min:
    #    #if ann_lhs.min is None and  ann_rhs.min is not None:
    #    #    ann_lhs.min = ann_rhs.min *
    #    #
    #    #if ann_lhs.max is None and  ann_rhs.max is not None:
    #        #ann_lhs.max = ann_rhs.max




    #def VisitRegimeDispatchMap(self, o):
    #    assert len(o.rhs_map) == 1
    #    # Don't worry about regime maps:
    #    for v in o.rhs_map.values():
    #        self.visit( v )

    #    var_annots = [ self.get_annotation(v) for v in  o.rhs_map.values() ]
    #    mins =   sorted( [ann.min for ann in var_annots if ann.min is not None] )
    #    maxes =  sorted( [ann.max for ann in var_annots if ann.max is not None] )

    #    if not mins:
    #        mins = [None]
    #    if not maxes:
    #        maxes = [None]

    #    self.set_annotation(o, NodeRange( mins[0], maxes[-1] ) )
    #    #self.annotations[o] = self.visit( o.rhs_map.values()[0])



    #def VisitFunctionDefBuiltInInstantiation(self,o):
    #    print
    #    for p in o.parameters.values():
    #        self.visit(p)
    #    # We should only have builtin functions by this point
    #    #assert o.function_def.is_builtin()

    #    # Handle exponents:
    #    assert o.function_def.funcname is '__exp__'
    #    param_node_ann = self.get_annotation( o.parameters.values()[0].rhs_ast )
    #    print param_node_ann

    #    min=None
    #    max=None
    #    if param_node_ann.min is not None:
    #        v = param_node_ann.min.dimensionless()
    #        min = MMQuantity( np.exp(v),  MMUnit() )
    #    if param_node_ann.max is not None:
    #        v = param_node_ann.max.dimensionless()
    #        max = MMQuantity( np.exp(v),  MMUnit() )

    #    self.set_annotation(o, NodeRange(min=min, max=max) )
    #    #assert False

    #def VisitFunctionDefUserInstantiation(self,o):
    #    assert False



    #def VisitFunctionDefInstantiationParater(self, o):
    #    self.visit(o.rhs_ast)
    #    ann = self.get_annotation(o.rhs_ast)
    #    self.set_annotation(o, NodeRange(min=ann.min, max=ann.max) )






    #def _VisitBinOp(self, o, op):
    #    self.visit(o.lhs)
    #    self.visit(o.rhs)
    #    ann1 = self.get_annotation(o.lhs)
    #    ann2 = self.get_annotation(o.rhs)

    #    extremes = [
    #        do_op(ann1.min, ann2.min, op ),
    #        do_op(ann1.min, ann2.max, op ),
    #        do_op(ann1.max, ann2.min, op ),
    #        do_op(ann1.max, ann2.max, op ),
    #        ]
    #    extremes = sorted([e for e in extremes if e is not None])
    #    assert len(extremes)==4
    #    print extremes

    #    if len(extremes) < 2:
    #        _min = None
    #        _max = None
    #    else:
    #        _min = extremes[0]
    #        _max = extremes[-1]



    #    self.set_annotation(o, NodeRange(min=_min, max=_max) )
    #    print 'Finding limits for: ', o, self.get_annotation(o)
    #    print '   (LHS): ', o.lhs, self.get_annotation(o.lhs)
    #    print '   (RHS): ', o.rhs, self.get_annotation(o.rhs)



    #def VisitAddOp(self, o):
    #    self._VisitBinOp(o, op=operator.add)

    #def VisitSubOp(self, o):
    #    self._VisitBinOp(o, op=operator.sub)

    #def VisitMulOp(self, o):
    #    self._VisitBinOp(o, op=operator.mul)

    #def VisitDivOp(self, o):
    #    self._VisitBinOp(o, op=operator.div)




    #def VisitIfThenElse(self, o):
    #    self.visit(o.if_true_ast)
    #    self.visit(o.if_false_ast)
    #    self.visit(o.predicate)

    #    ann1 = self.get_annotation(o.if_true_ast)
    #    ann2 = self.get_annotation(o.if_false_ast)

    #    extremes = [
    #        ann1.min,
    #        ann1.max,
    #        ann2.min,
    #        ann2.max,
    #            ]
    #    extremes = sorted([e for e in extremes if e is not None])
    #    assert len(extremes)==4

    #    if len(extremes) < 2:
    #        _min = None
    #        _max = None
    #    else:
    #        _min = extremes[0]
    #        _max = extremes[-1]

    #    self.set_annotation(o, NodeRange(min=_min, max=_max) )




    #def VisitInEquality(self, o):
    #    self.visit(o.lesser_than)
    #    self.visit(o.greater_than)

    #    ann1 = self.get_annotation(o.lesser_than)
    #    ann2 = self.get_annotation(o.greater_than)

    #    extremes = [
    #        ann1.min,
    #        ann1.max,
    #        ann2.min,
    #        ann2.max,
    #            ]
    #    extremes = sorted([e for e in extremes if e is not None])
    #    assert len(extremes)==4

    #    if len(extremes) < 2:
    #        _min = None
    #        _max = None
    #    else:
    #        _min = extremes[0]
    #        _max = extremes[-1]

    #    self.set_annotation(o, NodeRange(min=_min, max=_max) )


    #def VisitBoolAnd(self, o):
    #    self.visit(o.lhs)
    #    self.visit(o.rhs)

    #def VisitBoolOr(self, o):
    #    self.visit(o.lhs)
    #    self.visit(o.rhs)

    #def VisitBoolNot(self, o):
    #    self.visit(o.lhs)

    #def VisitParameter(self, o):
    #    pass

    def VisitSymbolicConstant(self, o):
        self.set_annotation(o, NodeRange(min=o.value, max=o.value) )


    #def VisitStateVariable(self, o):
    #    assert o.initial_value
    #    if o.initial_value:
    #        self.visit(o.initial_value)

    #def VisitAssignedVariable(self, o):
    #    pass

    #def VisitConstant(self, o):
    #    self.set_annotation(o, NodeRange(min=o.value, max=o.value) )

    #def VisitConstantZero(self, o):
    #    self.set_annotation(o, NodeRange(min='0',max='0'))


    #def VisitSuppliedValue(self, o):
    #    pass


    def VisitRandomVariable(self, o):
        assert o.functionname == 'uniform'

        min_rhs = o.parameters.get_single_obj_by(name='min').rhs_ast
        max_rhs = o.parameters.get_single_obj_by(name='max').rhs_ast
        assert isinstance(min_rhs, ast.ConstValue)
        assert isinstance(max_rhs, ast.ConstValue)
        #assert isinstance(o.parameters.get_single_obj_by(name='min').rhs_ast, ast.ConstValue)
        #assert isinstance(o.parameters.get_single_obj_by(name='max').rhs_ast, ast.ConstValue)
        #for p in o.parameters:
        #    self.visit(p)

        #ann_min = self.get_annotation( o.parameters.get_single_obj_by(name='min') )
        #ann_max = self.get_annotation( o.parameters.get_single_obj_by(name='max') )

        #assert(ann_min.min != None and ann_min.max != None)
        #assert(ann_max.min != None and ann_max.max != None)

        self.set_annotation( o, NodeRange( min_rhs.value, max_rhs.value) )



    def VisitRandomVariableParameter(self, o, **kwargs):
        self.visit(o.rhs_ast)
        ann = self.get_annotation(o.rhs_ast)
        self.set_annotation(o, NodeRange( min=ann.min, max=ann.max) )


    #def _VisitTransition(self, n):
    #    for action in n.actions:
    #        self.visit(action)

    #def VisitOnTransitionTrigger(self, n):
    #    self.visit(n.trigger)
    #    self._VisitTransition(n)

    #def VisitOnTransitionEvent(self, n):
    #    for p in n.parameters:
    #        self.visit(p)
    #    self._VisitTransition(n)

    #def VisitOnEventStateAssignment(self, o):
    #    self.visit(o.rhs)
    #    ann_rhs = self.get_annotation(o.rhs)
    #    self.set_annotation(o, NodeRange(min=ann_rhs.min, max=ann_rhs.max))

    #def VisitEmitEvent(self, o):
    #    for p in o.parameters:
    #        self.visit(p)
    #    self.visit(o.port)

    #def VisitOutEventPort(self, o):
    #    for p in o.parameters:
    #        self.visit(p)

    #def VisitInEventPort(self, o):
    #    for p in o.parameters:
    #        self.visit(p)
































class NodeRange(object):
    def __init__(self, min=None, max=None):

        from neurounits import NeuroUnitParser
        if isinstance(min, basestring):
            min = NeuroUnitParser.QuantitySimple(min)
        if isinstance(max, basestring):
            max = NeuroUnitParser.QuantitySimple(max)

        if(min is not None and max is not None):
            assert(min.is_compatible(max.unit))


        self._min = min
        self._max = max

    def __repr__(self):
        return "<NodeRange: %s to %s>" % (self._min, self._max)

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value



class NodeRangeAnnotator(ASTTreeAnnotator):
    def __init__(self, manual_range_annotations):
        self._manual_range_annotations = manual_range_annotations

    def annotate_ast(self, ninemlcomponent ):
        # Propagate the values around the tree:
        NodeValueRangePropagator( ninemlcomponent, annotations_in = self._manual_range_annotations)

































class FixedPointData(object):
    def __init__(self, datatype, upscale, const_value_as_int=None, delta_upscale=None, ):
        self.datatype = datatype
        self.upscale = upscale
        self.const_value_as_int = const_value_as_int
        self.delta_upscale = delta_upscale

    def __repr__(self):
        return "<FixedPointData: upscale=%s, const_value_as_int=%s>" % (self.upscale, self.const_value_as_int )


class NodeFixedPointFormatAnnotator(ASTTreeAnnotator, ASTActionerDefault):

    annotator_dependancies = [NodeRangeAnnotator]

    def __init__(self, nbits, datatype='int'):
        super(NodeFixedPointFormatAnnotator, self ).__init__()
        self.nbits = nbits
        self.datatype=datatype


    def annotate_ast(self, ninemlcomponent):
        self.visit(ninemlcomponent)


    @classmethod
    def encore_value_cls(self, value, upscaling_pow, nbits):
        #print
        print 'Encoding', value, "using upscaling power:", upscaling_pow
        value_scaled = value * ( 2**(-upscaling_pow))
        print ' --Value Scaled:', value_scaled
        res = int( round( value_scaled * (2**(nbits-1) ) ) )
        print ' --Value int:', res
        return res


    def encode_value(self, value, upscaling_pow):
        return self.encore_value_cls(value, upscaling_pow, nbits=self.nbits)
        #print
        print 'Encoding', value, "using upscaling power:", upscaling_pow
        value_scaled = value * ( 2**(-upscaling_pow))
        print ' --Value Scaled:', value_scaled
        res = int( round( value_scaled * (2**(self.nbits-1) ) ) )
        print ' --Value int:', res
        return res


    def ActionNodeStd(self, o):
        print
        print repr(o)
        print '-' * len(repr(o))
        #ann = self.annotations.annotations[o]

        vmin = o.annotations['node-value-range'].min.float_in_si()
        vmax = o.annotations['node-value-range'].max.float_in_si()
        #print ann

        # Lets go symmetrical, about 0:
        ext = max( [np.abs(vmin),np.abs(vmax) ] )
        if ext != 0.0:
            upscaling_pow = int( np.ceil( np.log2(ext ) ) )
        else:
            upscaling_pow = 0

        # Lets remap the limits:
        upscaling_val = 2 ** (-upscaling_pow)
        vmin_scaled  = vmin * upscaling_val
        vmax_scaled  = vmax * upscaling_val

        print 'vMin, vMax', vmin, vmax
        print 'Scaling:', '2**', upscaling_pow, ' ->', upscaling_val
        print 'vMin_scaled, vMax_scaled', vmin_scaled, vmax_scaled


        #ann.fixed_scaling_power = upscaling_pow
        o.annotations['fixed-point-format'] = FixedPointData( upscale = upscaling_pow,  datatype=self.datatype)

        assert 0.1 < max( [np.fabs(vmin_scaled), np.fabs(vmax_scaled) ] ) <= 1.0 or  vmin_scaled == vmax_scaled == 0.0








    def ActionAddOp(self, o):
        self.ActionNodeStd(o)
    def ActionSubOp(self, o):
        self.ActionNodeStd(o)
    def ActionMulOp(self, o):
        self.ActionNodeStd(o)
    def ActionDivOp(self, o):
        self.ActionNodeStd(o)

    def ActionFunctionDefUserInstantiation(self, o):
        self.ActionNodeStd(o)

    def ActionFunctionDefBuiltInInstantiation(self, o):
        self.ActionNodeStd(o)

    def ActionFunctionDefInstantiationParater(self,o):
        self.ActionNodeStd(o)




    def ActionIfThenElse(self, o ):
        self.ActionNodeStd(o)

    def ActionAssignedVariable(self, o):
        self.ActionNodeStd(o)

    def ActionStateVariable(self, o, **kwargs):
        self.ActionNodeStd(o)
        # Assume that the delta needs the same range as the original data (safer, but maybe not optimal!)
        o.annotations['fixed-point-format'].delta_upscale = o.annotations['fixed-point-format'].upscale


    def ActionSuppliedValue(self, o):
        self.ActionNodeStd(o)

    def ActionConstant(self, o):
        v = o.value.float_in_si()
        if o.value.magnitude == 0.0:
            upscaling_pow = 0
        else:
            upscaling_pow = int( np.ceil( np.log2(np.fabs(v)) ) )
        o.annotations['fixed-point-format'] = FixedPointData( upscale = upscaling_pow, const_value_as_int = self.encode_value(v, upscaling_pow) ,  datatype=self.datatype)

    def ActionSymbolicConstant(self, o):
        self.ActionConstant(o)

    def ActionRegimeDispatchMap(self, o):
        self.ActionNodeStd(o)

    def ActionConstantZero(self, o):
        self.ActionNodeStd(o)


    def ActionBoolAnd(self, o):
        pass
    def ActionBoolOr(self, o):
        pass
    def ActionBoolNot(self, o):
        pass
    def ActionInEquality(self, o):
        pass
    def ActionFunctionDefParameter(self, o):
        pass
    def ActionFunctionDefBuiltIn(self, o):
        pass
    def ActionEqnAssignmentByRegime(self, o):
        pass
    def ActionTimeDerivativeByRegime(self, o):
        pass
    def ActionRegime(self,o):
        pass
    def ActionRTGraph(self, o):
        pass
    def ActionNineMLComponent(self, o):
        pass
    def ActionOnTransitionTrigger(self, o):
        pass
    def ActionOnTransitionEvent(self, o):
        pass

    def ActionOnEventStateAssignment(self, o):
        self.ActionNodeStd(o)

    def ActionRandomVariable(self, o, **kwargs):
        self.ActionNodeStd(o)
    def ActionRandomVariableParameter(self, o, **kwargs):
        self.ActionNodeStd(o)


    def ActionOutEventPort(self, o):
        pass
    def ActionInEventPort(self, o):
        pass
    def ActionEmitEvent(self, o):
        pass













from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
class NodeToIntAnnotator(ASTActionerDefault):


    def __init__(self):
        self.node_to_int = {}
        self.int_to_node = {}
        super(ASTActionerDefault,self).__init__()


    def annotate_ast(self, component):
        assert self.node_to_int == {}
        self.visit(component)

    def ActionNode(self, n, **kwargs):
        if n in self.node_to_int:
            return

        val = len(self.node_to_int)
        self.node_to_int[n] = val
        self.int_to_node[val] = n
        n.annotations['node-id'] = val











