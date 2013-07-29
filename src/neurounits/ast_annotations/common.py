



from neurounits.ast_annotations.bases import ASTNodeAnnotationData, ASTTreeAnnotationManager, ASTTreeAnnotator 
from neurounits.Zdev.fixed_point_annotations import VarAnnot, ASTDataAnnotator, CalculateInternalStoragePerNode
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault

import numpy as np



class NodeRange(object):
    def __init__(self, min=None, max=None):
        
        from neurounits import NeuroUnitParser
        if isinstance(min, basestring):
            val_min = NeuroUnitParser.QuantitySimple(min)
        if isinstance(max, basestring):
            val_max = NeuroUnitParser.QuantitySimple(max)
        assert(min.is_compatible(max.unit))
            
            
        self._min = min
        self._max = max
        
    def __repr__(self):
        return "<NodeRange: %s to %s>" % (self._min, self._max) 

    @property
    def min(self):
        return self._min
    @property
    def max(self):
        return self._max


class NodeRangeAnnotator(ASTTreeAnnotator):
    def __init__(self, manual_range_annotations):
        self._manual_range_annotations = manual_range_annotations
    
    def annotate_ast(self, ninemlcomponent ):
        anns = ASTDataAnnotator( ninemlcomponent, annotations_in = self._manual_range_annotations)
        
        
        import neurounits.ast as ast
        # Copy accross:
        for ast_node in ninemlcomponent.all_ast_nodes():
            
            print ast_node
            
            if ast_node in anns.annotations:
                ann = anns.annotations[ast_node]
                ast_node.annotations.add('node-value-range', NodeRange(min=ann.val_min,max=ann.val_max) )
                                                                        
        
        print anns
        
        
        #raise NotImplementedError()

        #self.val_min = val_min
        #self.val_max = val_max
        #self.fixed_scaling_power = None
        #self.value_as_int = None





class FixedPointData(object):
    def __init__(self, upscale, const_value_as_int=None):
        self.upscale = upscale
        self.const_value_as_int = const_value_as_int
        
    def __repr__(self):
        return "<FixedPointData: upscale=%s, const_value_as_int=%s>" % (self.upscale, self.const_value_as_int )


class NodeFixedPointFormatAnnotator(ASTTreeAnnotator, ASTActionerDefault):
    
    annotator_dependancies = [NodeRangeAnnotator] 
    
    def __init__(self, nbits):
        super(NodeFixedPointFormatAnnotator, self ).__init__()
        self.nbits = nbits
        
        
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
        #vmin = ann.min.float_in_si()
        #vmax = ann.val_max.float_in_si()
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


        #ann.fixed_scaling_power = upscaling_pow
        o.annotations['fixed-point-format'] = FixedPointData( upscale = upscaling_pow) 
        
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
        #if o.initial_value:
        #    
        #    print o.initial_value
        #    assert False
        #    ann = self.annotations[o]
        #    ann.initial_value = self.encode_value(o.initial_value.value.float_in_si(), ann.fixed_scaling_power)
            
        
        
            
        

    def ActionSuppliedValue(self, o):
        self.ActionNodeStd(o)

    def ActionConstant(self, o):
        print
        print 'Converting: ', o, o.value

        v = o.value.float_in_si()
        if o.value.magnitude == 0.0:
            upscaling_pow = 0
        else:
            upscaling_pow = int( np.ceil( np.log2(np.fabs(v)) ) )

        o.annotations['fixed-point-format'] = FixedPointData( upscale = upscaling_pow, const_value_as_int = self.encode_value(v, upscaling_pow))

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

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        