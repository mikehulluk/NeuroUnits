


import neurounits

import numpy as np
import pylab
from neurounits.units_backends.mh import MMQuantity, MMUnit
from neurounits.visitors.bases.base_actioner import ASTActionerDepthFirst
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits import NeuroUnitParser



class VarAnnot(object):
    def __init__(self, val_min = None, val_max = None ):
        from neurounits import NeuroUnitParser
        if isinstance(val_min, basestring):
            val_min = NeuroUnitParser.QuantitySimple(val_min)
        if isinstance(val_max, basestring):
            val_max = NeuroUnitParser.QuantitySimple(val_max)

        self.val_min = val_min
        self.val_max = val_max
        self.fixed_scaling_power = None
        self.value_as_int = None


    def __str__(self):
        sc = str(self.fixed_scaling_power) if self.fixed_scaling_power is not None else "??"
        return "VarAnnot( fixed_scaling_power:%s,  min:{%s} max:{%s},   )" % (sc, self.val_min, self.val_max)








import operator
def do_op(a,b,op):
    if a is None or b is None:
        return None
    try:
        return op(a,b)
    except ZeroDivisionError:
        assert False
        return None








class ASTDataAnnotator(ASTVisitorBase):


    def __getitem__(self, k):
        return self.annotations[k]


    def __init__(self, component, annotations_in):
        self.component = component
        self.annotations = {}

        # Change string to node:
        for ann,val in annotations_in.items():
            if not component.has_terminal_obj(ann):
                continue
            if isinstance(ann, basestring):
                self.annotations[component.get_terminal_obj(ann)] = val
            else:
                self.annotations[ann] = val

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
        if ann_lhs.val_min is None and  ann_rhs.val_min is not None:
            ann_lhs.val_min = ann_rhs.val_min

        if ann_lhs.val_max is None and  ann_rhs.val_max is not None:
            ann_lhs.val_max = ann_rhs.val_max




    def VisitTimeDerivativeByRegime(self, o):
        self.visit(o.rhs_map)
        self.visit(o.lhs)


        ann_lhs = self.annotations[o.lhs]
        ann_rhs = self.annotations[o.rhs_map]

        # Need to be a bit careful here - because  rememeber that rhs is multiplied by dt!
        
        ## Min:
        #if ann_lhs.val_min is None and  ann_rhs.val_min is not None:
        #    ann_lhs.val_min = ann_rhs.val_min * 
        #
        #if ann_lhs.val_max is None and  ann_rhs.val_max is not None:
            #ann_lhs.val_max = ann_rhs.val_max




    def VisitRegimeDispatchMap(self, o):
        assert len(o.rhs_map) == 1
        # Don't worry about regime maps:
        for v in o.rhs_map.values():
            self.visit( v )

        var_annots = [ self.annotations[v] for v in  o.rhs_map.values() ]
        mins =   sorted( [ann.val_min for ann in var_annots if ann.val_min is not None] )
        maxes =  sorted( [ann.val_max for ann in var_annots if ann.val_max is not None] )

        if not mins:
            mins = [None]
        if not maxes:
            maxes = [None]

        self.annotations[o] = VarAnnot( mins[0], maxes[-1] )
        #self.annotations[o] = self.visit( o.rhs_map.values()[0])



    def VisitFunctionDefBuiltInInstantiation(self,o):
        print
        for p in o.parameters.values():
            self.visit(p)
        # We should only have builtin functions by this point
        assert o.function_def.is_builtin()

        # Handle exponents:
        assert o.function_def.funcname is '__exp__'
        param_node_ann = self.annotations[ o.parameters.values()[0].rhs_ast ]
        print param_node_ann

        min=None
        max=None
        if param_node_ann.val_min is not None:
            v = param_node_ann.val_min.dimensionless()
            min = MMQuantity( np.exp(v),  MMUnit() )
        if param_node_ann.val_max is not None:
            v = param_node_ann.val_max.dimensionless()
            max = MMQuantity( np.exp(v),  MMUnit() )

        self.annotations[o] = VarAnnot(val_min=min, val_max=max)
        #assert False



    def VisitFunctionDefUserInstantiation(self,o):
        # We should only have builtin functions by this point
        assert False












    def VisitFunctionDefInstantiationParater(self, o):
        self.visit(o.rhs_ast)
        ann = self.annotations[o.rhs_ast]
        self.annotations[o] =  VarAnnot(val_min=ann.val_min, val_max=ann.val_max)






    def _VisitBinOp(self, o, op):
        self.visit(o.lhs)
        self.visit(o.rhs)
        ann1 = self.annotations[o.lhs]
        ann2 = self.annotations[o.rhs]

        extremes = [
            do_op(ann1.val_min, ann2.val_min, op ),
            do_op(ann1.val_min, ann2.val_max, op ),
            do_op(ann1.val_max, ann2.val_min, op ),
            do_op(ann1.val_max, ann2.val_max, op ),
            ]
        extremes = sorted([e for e in extremes if e is not None])
        
        print extremes

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = VarAnnot(val_min=min, val_max=max)



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
            ann1.val_min,
            ann1.val_max,
            ann2.val_min,
            ann2.val_max,
                ]
        extremes = sorted([e for e in extremes if e is not None])

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = VarAnnot(val_min=min, val_max=max)




    def VisitInEquality(self, o):
        self.visit(o.lesser_than)
        self.visit(o.greater_than)

        ann1 = self.annotations[o.lesser_than]
        ann2 = self.annotations[o.greater_than]

        extremes = [
            ann1.val_min,
            ann1.val_max,
            ann2.val_min,
            ann2.val_max,
                ]
        extremes = sorted([e for e in extremes if e is not None])

        if len(extremes) < 2:
            min = None
            max = None
        else:
            min = extremes[0]
            max = extremes[-1]

        self.annotations[o] = VarAnnot(val_min=min, val_max=max)




    def VisitParameter(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitSymbolicConstant(self, o):
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)


    # Handled in the __init__ function:
    def VisitStateVariable(self, o):
        if o.initial_value:
            self.visit(o.initial_value)

    def VisitAssignedVariable(self, o):
        pass
        #return self.get_var_str(o.symbol)

    def VisitConstant(self, o):
        print 'Visiting Constant: ', o
        self.annotations[o] = VarAnnot(val_min=o.value, val_max=o.value)

    def VisitSuppliedValue(self, o):
        pass
        #return o.symbol








class CalculateInternalStoragePerNode(ASTActionerDepthFirst):

    def __init__(self, annotations, nbits):
        super(CalculateInternalStoragePerNode, self).__init__()
        self.annotations = annotations
        self.nbits = nbits

    def encode_value(self, value, upscaling_pow):
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
        ann = self.annotations.annotations[o]
        print ann

        # Lets go symmetrical, about 0:
        vmin = ann.val_min.float_in_si()
        vmax = ann.val_max.float_in_si()
        ext = max( [np.abs(vmin),np.abs(vmax) ] )   
        if ext != 0.0:
            #Include some padding:
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


        ann.fixed_scaling_power = upscaling_pow

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


    def ActionInEquality(self, o):
        pass

    def ActionIfThenElse(self, o ):
        self.ActionNodeStd(o)



    def ActionFunctionDefParameter(self, o):
        pass

    def ActionFunctionDefBuiltIn(self, o):
        pass

    def ActionAssignedVariable(self, o):
        self.ActionNodeStd(o)
    def ActionStateVariable(self, o, **kwargs):
        self.ActionNodeStd(o)
        
        # Convert the initial value:
        if o.initial_value:
            ann = self.annotations[o]
            ann.initial_value = self.encode_value(o.initial_value.value.float_in_si(), ann.fixed_scaling_power)
            
        
        
            
        

    def ActionSuppliedValue(self, o):
        self.ActionNodeStd(o)

    def ActionConstant(self, o):
        print
        print 'Converting: ', o, o.value

        v = o.value.float_in_si()
        ann = self.annotations.annotations[o]
        if o.value.magnitude == 0.0:
            upscaling_pow = 0
            ann.fixed_scaling_power = upscaling_pow
            ann.value_as_int = self.encode_value(v, upscaling_pow)

        else:
            upscaling_pow = int( np.ceil( np.log2(np.fabs(v)) ) )
            ann.fixed_scaling_power = upscaling_pow
            ann.value_as_int = self.encode_value(v, upscaling_pow)

    def ActionSymbolicConstant(self, o):
        self.ActionConstant(o)

    def ActionRegimeDispatchMap(self, o):
        self.ActionNodeStd(o)

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
