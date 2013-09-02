



#from neurounits.ast_annotations.bases import ASTNodeAnnotationData, ASTTreeAnnotationManager, ASTTreeAnnotator
from neurounits.ast_annotations.bases import ASTTreeAnnotator
#from neurounits.Zdev.fixed_point_annotations import VarAnnot, ASTDataAnnotator#, CalculateInternalStoragePerNode
#from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault

#import numpy as np
#import neurounits

import numpy as np
#import pylab
#from neurounits.units_backends.mh import MMQuantity, MMUnit
#from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits import ast








from node_toint import NodeToIntAnnotator
from node_tagger import NodeTagger
from node_fixedpointannotator import NodeFixedPointFormatAnnotator
#from node_rangeexpander import RangeExpander 








































#propagation_rules = """
#
#AddOp [self.min <= lhs.min + rhs.min], [self.rhs <= self.min - rhs.min], [self.lhs <= self.min - lhs.min]
#
#
#"""
class _NodeRangeFloat(object):
    def __init__(self, min_, max_):
        self.min_=min_
        self.max_=max_
    def __repr__(self, ):
        return "<NodeRangeFloat: %s, %s>" %(self.min_, self.max_)

    @property
    def min(self):
        return self.min_
    @property
    def max(self):
        return self.max_

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


#def set_minmax_for_node(func):
#    def new_func(self, o, *args,**kwargs):
#        array = func(self, o, *args, **kwargs)
#        #print func
#        #print array, type(array)
#        assert isinstance(array, (np.ndarray,np.float64))
#        print array.dtype
#        assert array.dtype in (np.float64, bool)
#        #assert False
#        assert not np.isnan(array).any()
#        min_val = np.min(array)
#        max_val = np.max(array)
#
#        
#
#        if 'node-value-range' not in o.annotations:
#            o.annotations['node-value-range'] = _NodeRangeFloat(min_=min_val, max_=max_val)
#            o.annotations['node-value-range'].array =array
#            o.annotations['node-value-range'].sv_order = self.sv_order
#            o.annotations['node-value-range'].sv_values = self.sv_values
#
#
#        else:
#
#
#            
#            if not (o.annotations['node-value-range'].min == min_val and o.annotations['node-value-range'].max == max_val):
#                print 'Node', o
#                #print repr(o.lhs), repr(o.rhs)
#
#                print 'Min/Max mismatch:'
#                print 'min'
#                print  '  - Old', o.annotations['node-value-range'].min
#                print  '  - New', min_val
#                print 'max'
#                print  '  - Old', o.annotations['node-value-range'].max
#                print  '  - New', max_val
#
#                print 'sv_order'
#                #print  '  - Old', o.annotations['node-value-range'].sv_order
#                print  '  - New', self.sv_order
#
#                print 'sv_values'
#                #print  '  - Old', o.annotations['node-value-range'].sv_order
#                print  '  - New', self.sv_values
#
#                print 
#                print o
#                print "o.annotations['node-value-range'].min", type( o.annotations['node-value-range'].min ),  o.annotations['node-value-range'].min 
#                print "min_val", type(min_val), min_val
#                assert  o.annotations['node-value-range'].min == min_val
#                assert  o.annotations['node-value-range'].max == max_val
#
#        return array
#    return new_func
#
#
#
#
##def check_array_returned(func):
##    def new_func(*args,**kwargs):
##        array = func(*args,**kwargs)
##        assert isinstance(array, np.ndarray)
##        return array
##    return new_func
#
#class LargeArrayPropagator(ASTVisitorBase):
#    def __init__(self, component, assignment_node, sv_order, sv_values):
#        """sv_order - list of terminal
#           sv_values - dictionary mapping terminals to values"""
#        self.component = component
#        self.sv_order = sv_order
#        self.sv_values = sv_values
#
#
#        self.visit(assignment_node)
#
#        if  not isinstance(assignment_node, ast.OnTriggerTransition):
#            print 'For %s, limits are: %s' %(repr(assignment_node), repr(assignment_node.annotations['node-value-range']) )
#
#
#        ##print array
#        #assert isinstance(array, (np.ndarray,np.float64))
#
#        #min_val = np.min(array)
#        #max_val = np.max(array)
#
#        #print 'For %s, min/max are: %s %s' %(repr(assignment_node), min_val, max_val)
#
#
#
#    # Top level objects:
#    # ======================
#    @set_minmax_for_node
#    def VisitTimeDerivativeByRegime(self, o):
#        return self.visit(o.rhs_map)
#    @set_minmax_for_node
#    def VisitEqnAssignmentByRegime(self, o):
#        return self.visit(o.rhs_map)
#    @set_minmax_for_node
#    def VisitOnEventStateAssignment(self,o):
#        return self.visit(o.rhs)
#    # ======================
#
#
#
#
#
#
#
#    @set_minmax_for_node
#    def VisitRegimeDispatchMap(self,o):
#        assert len(o.rhs_map) == 1
#        r = self.visit( list(o.rhs_map.values())[0] )
#        return r
#
#    @set_minmax_for_node
#    def VisitAddOp(self, o):
#        a1 = self.visit(o.lhs)
#        a2 = self.visit(o.rhs)
#        a3 =  a1+a2
#        assert a1.shape == a2.shape
#        assert a3.shape == a2.shape
#        return a3
#
#    @set_minmax_for_node
#    def VisitSubOp(self, o):
#        a1 = self.visit(o.lhs)
#        a2 = self.visit(o.rhs)
#        a3 =  a1-a2
#        assert a1.shape == a2.shape
#        assert a3.shape == a2.shape
#        return a3
#
#    @set_minmax_for_node
#    def VisitMulOp(self, o):
#        a1 = self.visit(o.lhs)
#        a2 = self.visit(o.rhs)
#        a3 =  a1*a2
#        assert a1.shape == a2.shape
#        assert a3.shape == a2.shape
#        return a3
#
#    @set_minmax_for_node
#    def VisitDivOp(self, o):
#        a1 = self.visit(o.lhs)
#        a2 = self.visit(o.rhs)
#        a3 =  a1/a2
#        assert a1.shape == a2.shape
#        assert a3.shape == a2.shape
#        return a3
#
#    @set_minmax_for_node
#    def VisitConstant(self, o):
#        res = self._VisitConstant( o)
#        return res
#    @set_minmax_for_node
#    def VisitSymbolicConstant(self, o):
#        return self._VisitConstant( o)
#
#    @set_minmax_for_node
#    def _VisitConstant(self, o):
#        if len(self.sv_order)==0:
#            return np.float64( o.value.float_in_si() )
#        else:
#            new_array = np.ones( [len(self.sv_values[sv]) for sv in self.sv_order] ) * float( o.value.float_in_si() )
#        return new_array
#
#
#
#    @set_minmax_for_node
#    def VisitAssignedVariable(self, o):
#        '''March straight through assigned variables'''
#        return self.visit( self.component._eqn_assignment.get_single_obj_by(lhs=o).rhs_map )
#
#
#
#    def _fixed_array(self, o):
#        #print 'Building fixed array for:', repr(o)
#        #print self.sv_order
#        assert o in self.sv_order
#        o_vals = self.sv_values[o].copy()
#        shape = tuple( [(len(o_vals) if sv==o else 1) for sv in self.sv_order] )
#        o_vals = o_vals.reshape( shape )
#        o_tile = tuple( [(len(self.sv_values[sv]) if sv!=o else 1) for sv in self.sv_order] )
#        mat = np.tile(o_vals, o_tile)
#        return mat
#
#    def VisitStateVariable(self, o):
#        return self._fixed_array(o)
#
#    def VisitRandomVariable(self, o):
#        return self._fixed_array(o)
#
#    def VisitSuppliedValue(self, o):
#        return self._fixed_array(o)
#
#    @set_minmax_for_node
#    def VisitFunctionDefBuiltInInstantiation(self, o):
#        if o.function_def.funcname == '__exp__':
#            p = o.parameters.values()[0]
#            a = self.visit(p)
#            return np.exp(a)
#
#        if o.function_def.funcname == '__ln__':
#            p = o.parameters.values()[0]
#            a = self.visit(p)
#            return np.log(a)
#        assert False, 'Not implemented for: %s' % ( o.function_def.funcname )
#
#
#    @set_minmax_for_node
#    def VisitFunctionDefInstantiationParameter(self, o):
#        return self.visit(o.rhs_ast)
#
#
#    @set_minmax_for_node
#    def VisitIfThenElse(self, o):
#        pred = self.visit(o.predicate)
#        if_true = self.visit(o.if_true_ast)
#        if_false = self.visit(o.if_false_ast)
#
#        res = if_false.copy()
#        res[pred] = if_true[pred]
#
#        #print 'pred'
#        #print pred
#
#        #print 'iftrue'
#        #print if_true
#
#        #print 'iffalse'
#        #print if_false
#        return res
#
#
#    def VisitBoolAnd(self, o):
#        return np.logical_and( self.visit(o.lhs), self.visit(o.rhs))
#    def VisitBoolOr(self, o):
#        return np.logical_or( self.visit(o.lhs), self.visit(o.rhs))
#
#
#    @set_minmax_for_node
#    def VisitInEquality(self, o):
#        a1 = self.visit(o.greater_than)
#        a2 = self.visit(o.lesser_than)
#        a3 =  a1>a2
#        assert a1.shape == a2.shape
#        assert a3.shape == a2.shape
#        return a3
#
#
#    def VisitOnTransitionTrigger(self,o):
#        self.visit(o.trigger)
#
#
#
#
#
#
#class NodeValueRangePropagator(ASTVisitorBase):
#
#    def get_annotation(self, node):
#        return node.annotations['node-value-range']
#
#    def set_annotation(self, node, ann):
#        node.annotations.add_overwrite('node-value-range', ann )
#        print 'Setting Annotation:'
#        print '  Node: ', node
#        print '  Ann:  ', ann
#
#    def has_annotation(self, node):
#        return 'node-value-range' in node.annotations
#
#
#    def __init__(self, component, annotations_in):
#        self.component = component
#        self.n_values_tested = 3
#
#        # Change string to node:
#        for ann,val in annotations_in.items():
#            if not component.has_terminal_obj(ann):
#                continue
#
#            assert isinstance(ann, basestring)
#            self.set_annotation(component.get_terminal_obj(ann), _NodeRangeFloat(min_=val.min.float_in_si(), max_=val.max.float_in_si(),  ) )
#
#
#        self.visit(component)
#
#    def VisitNineMLComponent(self, component):
#        from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
#
#
#        # Constants should be fine:
#        print '======== A ==========='
#        for o in component.symbolicconstants:
#            self.visit(o)
#
#        # Constants should be fine:
#        print '======== B ==========='
#        for o in component.random_variable_nodes:
#            self.visit(o)
#
#        # Parameters & supplied values need to have thier ranges supplied:
#        print '======== C ==========='
#        for o in list(component.parameters) + list(component.suppliedvalues):
#            assert self.has_annotation(o)
#
#        # State variables all need an annotation, since this is difficult to infer reliably:
#        print '======== D ==========='
#        for o in list(component.state_variables) :
#            assert self.has_annotation(o), "Not annotation given for state variable: %s" % o.symbol
#            self.visit(o.initial_value)
#
#        # This now leaves the assignments, and the delta-state variables to calculate:
#        print '======== E ==========='
#        deps = VisitorSymbolDependance(component)
#        for ass in sorted(component.assignments+component.timederivatives, key=lambda o:o.lhs.symbol):
#            #print
#            #print "PROPAGATING THROUGH: ", repr(ass)
#            ass_deps = list(deps.get_terminal_dependancies(ass, expand_assignments=True, include_random_variables=True, include_supplied_values=True))
#            #print ass_deps
#
#
#
#            # Work out the values to test for each state variable:
#            tested_vals = {}
#            for sv in sorted(ass_deps, key=lambda o:o.symbol if hasattr(o,'symbol') else id(o)):
#                assert isinstance(sv, (ast.RandomVariable, ast.StateVariable, ast.SuppliedValue))
#                tested_vals[sv] = np.linspace( sv.annotations['node-value-range'].min, sv.annotations['node-value-range'].max, num=self.n_values_tested)
#
#            #print tested_vals
#            # And propagate the array through the tree!
#            LargeArrayPropagator(component=component, assignment_node=ass, sv_order=ass_deps, sv_values=tested_vals)
#
#            # Copy the assignment node value into the assignedvariable range:
#            if isinstance(ass, ast.EqnAssignmentByRegime):
#                ass.lhs.annotations['node-value-range'] = ass.annotations['node-value-range']
#
#
#        # And the state-assignments:
#        print '======== F ==========='
#        for transition in component.transitions:
#            for state_assignment in transition.state_assignments:
#
#                sa_deps = list(deps.get_terminal_dependancies(state_assignment, expand_assignments=True, include_random_variables=True, include_supplied_values=True))
#
#
#                matrix_size = 10.e6
#                n_deps = len(sa_deps)
#                if n_deps > 0:
#                    n_vals = int( np.floor( np.power( matrix_size, 1./n_deps )) )
#                    assert n_vals > 2
#                else:
#                    n_vals=None
#                #print sa_deps
#                #print n_vals
#                #assert False
#
#                # Work out the values to test for each state variable:
#                tested_vals = {}
#                for sv in sa_deps:
#                    assert isinstance(sv, (ast.RandomVariable, ast.StateVariable, ast.SuppliedValue))
#                    #tested_vals[sv] = np.linspace( sv.annotations['node-value-range'].min, sv.annotations['node-value-range'].max, num=self.n_values_tested)
#                    tested_vals[sv] = np.linspace( sv.annotations['node-value-range'].min, sv.annotations['node-value-range'].max, num=n_vals)
#
#                # And propagate the array through the tree!
#                LargeArrayPropagator(component=component, assignment_node=state_assignment, sv_order=sa_deps, sv_values=tested_vals)
#
#        # And the triggered-transitions:
#        for triggered_transition in component.triggertransitions:
#            sa_deps = list(deps.get_terminal_dependancies(triggered_transition, expand_assignments=True, include_random_variables=True, include_supplied_values=True))
#            # Work out the values to test for each state variable:
#            tested_vals = {}
#            for sv in sa_deps:
#                assert isinstance(sv, (ast.RandomVariable, ast.StateVariable, ast.SuppliedValue))
#                tested_vals[sv] = np.linspace( sv.annotations['node-value-range'].min, sv.annotations['node-value-range'].max, num=self.n_values_tested)
#
#            # And propagate the array through the tree!
#            LargeArrayPropagator(component=component, assignment_node=triggered_transition, sv_order=sa_deps, sv_values=tested_vals)
#            
#
#
#
#        #import neurounits.visitors.common
#        #from neurounits.visitors.common.plot_networkx import ActionerPlotNetworkX
#        #colors = {node:('blue' if 'node-value-range' in node.annotations else 'red' )for node in self.component.all_ast_nodes() }
#        #ActionerPlotNetworkX(self.component, colors=colors)
#
#
#        #for node in component.all_ast_nodes():
#        #    if isinstance(node, (ast.FunctionDefParameter,ast.FunctionDefBuiltIn) ):
#        #        continue
#
#        #    if isinstance(node, ast.ASTExpressionObject):
#        #        print
#        #        print 'Node ', node, repr(node)
#
#        #        print 'Node limits', node.annotations._data.get('node-value-range', 'OHHHH NOOOOOO!')
#        #        print 'Node limits', node.annotations['node-value-range']
#
#
#        #assert False
#
#    def VisitSymbolicConstant(self, o):
#        self.set_annotation(o, _NodeRangeFloat(min_=o.value.float_in_si(), max_=o.value.float_in_si()) )
#    def VisitConstant(self, o):
#        self.set_annotation(o, _NodeRangeFloat(min_=o.value.float_in_si(), max_=o.value.float_in_si()) )
#
#
#    def VisitRandomVariable(self, o):
#        assert o.functionname == 'uniform'
#
#        for p in o.parameters:
#            self.visit(p)
#
#        self.set_annotation( o,
#                _NodeRangeFloat(
#                    o.parameters.get_single_obj_by(name='min').annotations['node-value-range'].min,
#                    o.parameters.get_single_obj_by(name='max').annotations['node-value-range'].max,
#                    )
#                )
#
#    def VisitRandomVariableParameter(self, o, **kwargs):
#        self.visit(o.rhs_ast)
#        ann = self.get_annotation(o.rhs_ast)
#        self.set_annotation(o, _NodeRangeFloat( min_=ann.min, max_=ann.max) )
#
#
#
#
#





























#
#
#
#class NodeRangeAnnotator(ASTTreeAnnotator):
#    def __init__(self, manual_range_annotations):
#        self._manual_range_annotations = manual_range_annotations
#
#    def annotate_ast(self, ninemlcomponent ):
#        # Propagate the values around the tree:
#        NodeValueRangePropagator( ninemlcomponent, annotations_in = self._manual_range_annotations)








































