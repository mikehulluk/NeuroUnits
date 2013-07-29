



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
from neurounits import NeuroUnitParser






import operator
def do_op(a,b,op):
    if a is None or b is None:
        return None
    try:
        return op(a,b)
    except ZeroDivisionError:
        assert False
        return None








propagation_rules = """

AddOp [self.min = lhs.min + rhs.min], [self.rhs = self.min - rhs.min], [self.lhs = self.min - lhs.min]


"""


class NodeValueRangePropagator(ASTVisitorBase):



    def get_annotation(self, node):
        return self.annotations[node]
        
    def set_annotation(self, node, ann):
        self.annotations[node] = ann
        
        
    #def __getitem__(self, k):
    #    assert False
    #    return self.annotations[k]






    def __init__(self, component, annotations_in):
        self.component = component
        self.annotations = {}

        # Change string to node:
        for ann,val in annotations_in.items():
            if not component.has_terminal_obj(ann):
                continue
            
            assert isinstance(ann, basestring)
            self.annotations[component.get_terminal_obj(ann)] = val
            
            #else:
            #    assert False
            #    self.annotations[ann] = val

        self.visit(component)

    def VisitNineMLComponent(self, component):

        for i in range(2):
            for o in component.symbolicconstants:
                self.visit(o)
            for o in component.ordered_assignments_by_dependancies:
                self.visit(o)
            for o in component.timederivatives:
                self.visit(o)




    def VisitEqnAssignmentByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)


        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs_map]

        #Min:
        if ann_lhs.min is None and  ann_rhs.min is not None:
            ann_lhs.min = ann_rhs.min

        if ann_lhs.max is None and  ann_rhs.max is not None:
            ann_lhs.max = ann_rhs.max




    def VisitTimeDerivativeByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)


        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs_map]

        # Need to be a bit careful here - because  rememeber that rhs is multiplied by dt!
        
        ## Min:
        #if ann_lhs.min is None and  ann_rhs.min is not None:
        #    ann_lhs.min = ann_rhs.min * 
        #
        #if ann_lhs.max is None and  ann_rhs.max is not None:
            #ann_lhs.max = ann_rhs.max




    def VisitRegimeDispatchMap(self, o):
        assert len(o.rhs_map) == 1
        # Don't worry about regime maps:
        for v in o.rhs_map.values():
            self.visit( v )

        var_annots = [ self.annotations[v] for v in  o.rhs_map.values() ]
        mins =   sorted( [ann.min for ann in var_annots if ann.min is not None] )
        maxes =  sorted( [ann.max for ann in var_annots if ann.max is not None] )

        if not mins:
            mins = [None]
        if not maxes:
            maxes = [None]

        self.annotations[o] = NodeRange( mins[0], maxes[-1] )
        #self.annotations[o] = self.visit( o.rhs_map.values()[0])



    def VisitFunctionDefBuiltInInstantiation(self,o):
        print
        for p in o.parameters.values():
            self.visit(p)
        # We should only have builtin functions by this point
        #assert o.function_def.is_builtin()

        # Handle exponents:
        assert o.function_def.funcname is '__exp__'
        param_node_ann = self.annotations[ o.parameters.values()[0].rhs_ast ]
        print param_node_ann

        min=None
        max=None
        if param_node_ann.min is not None:
            v = param_node_ann.min.dimensionless()
            min = MMQuantity( np.exp(v),  MMUnit() )
        if param_node_ann.max is not None:
            v = param_node_ann.max.dimensionless()
            max = MMQuantity( np.exp(v),  MMUnit() )

        self.annotations[o] = NodeRange(min=min, max=max)
        #assert False

    def VisitFunctionDefUserInstantiation(self,o):
        assert False



    def VisitFunctionDefInstantiationParater(self, o):
        self.visit(o.rhs_ast)
        ann = self.annotations[o.rhs_ast]
        self.annotations[o] =  NodeRange(min=ann.min, max=ann.max)






    def _VisitBinOp(self, o, op):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]

        extremes = [
            do_op(ann1.min, ann2.min, op ),
            do_op(ann1.min, ann2.max, op ),
            do_op(ann1.max, ann2.min, op ),
            do_op(ann1.max, ann2.max, op ),
            ]
        extremes = sorted([e for e in extremes if e is not None])
        
        print extremes

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = NodeRange(min=min, max=max)



    def VisitAddOp(self, o):
        self._VisitBinOp(o, op=operator.add)

    def VisitSubOp(self, o):
        self._VisitBinOp(o, op=operator.sub)

    def VisitMulOp(self, o):
        self._VisitBinOp(o, op=operator.mul)

    def VisitDivOp(self, o):
        self._VisitBinOp(o, op=operator.div)
        



    def VisitIfThenElse(self, o):
        self.visit(o.if_true_ast)
        self.visit(o.if_false_ast)
        self.visit(o.predicate)

        ann1 = self.annotations[o.if_true_ast]
        ann2 = self.annotations[o.if_false_ast]

        extremes = [
            ann1.min,
            ann1.max,
            ann2.min,
            ann2.max,
                ]
        extremes = sorted([e for e in extremes if e is not None])

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = NodeRange(min=min, max=max)




    def VisitInEquality(self, o):
        self.visit(o.less_than)
        self.visit(o.greater_than)

        ann1 = self.annotations[o.less_than]
        ann2 = self.annotations[o.greater_than]

        extremes = [
            ann1.min,
            ann1.max,
            ann2.min,
            ann2.max,
                ]
        extremes = sorted([e for e in extremes if e is not None])

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = NodeRange(min=min, max=max)




    def VisitParameter(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        self.annotations[o] = NodeRange(min=o.value, max=o.value)


    def VisitStateVariable(self, o):
        if o.initial_value:
            self.visit(o.initial_value)

    def VisitAssignedVariable(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        print 'Visiting Constant: ', o
        self.annotations[o] = NodeRange(min=o.value, max=o.value)

    def VisitSuppliedValue(self, o):
        pass
        #return o.symbol





































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
        anns = NodeValueRangePropagator( ninemlcomponent, annotations_in = self._manual_range_annotations)
        
        
        import neurounits.ast as ast
        # Copy accross:
        for ast_node in ninemlcomponent.all_ast_nodes():
            
            print ast_node
            
            if ast_node in anns.annotations:
                ann = anns.annotations[ast_node]
                ast_node.annotations.add('node-value-range', NodeRange(min=ann.min,max=ann.max) )
                                                                        
        
        print anns
        
        







































class FixedPointData(object):
    def __init__(self, datatype, upscale, const_value_as_int=None):
        self.datatype = datatype
        self.upscale = upscale
        self.const_value_as_int = const_value_as_int
        
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
        
    


    def encode_value(self, value, upscaling_pow):
        #print
        print 'Encoding', value, "using upscaling power:", upscaling_pow
        value_scaled = value * ( 2**(-upscaling_pow))
        print ' --Value Scaled:', value_scaled
        res = int( round( value_scaled * (2**(self.nbits-1) ) ) )
        print ' --Value int:', res
        return res

    
    
    
    #def ActionNode(self, node):
    #    print 'Calculating storage for: ', node
        
        
        
    
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

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        