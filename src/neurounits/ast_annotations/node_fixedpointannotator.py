from neurounits.ast_annotations.bases import ASTTreeAnnotator
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
#from neurounits.ast_annotations.common import NodeRangeAnnotator

import numpy as np






class FixedPointData(object):
    def __init__(self, datatype, upscale, const_value_as_int=None, delta_upscale=None, ):
        self.datatype = datatype
        self.upscale = upscale
        self.const_value_as_int = const_value_as_int
        self.delta_upscale = delta_upscale

    def __repr__(self):
        return "<FixedPointData: upscale=%s, const_value_as_int=%s>" % (self.upscale, self.const_value_as_int )





class NodeFixedPointFormatAnnotator(ASTTreeAnnotator, ASTActionerDefault):

    #annotator_dependancies = [NodeRangeAnnotator]

    def __init__(self, nbits, datatype='int'):
        super(NodeFixedPointFormatAnnotator, self ).__init__()
        self.nbits = nbits
        self.datatype=datatype


    def annotate_ast(self, ninemlcomponent):
        self.visit(ninemlcomponent)


    @classmethod
    def encode_value_cls(self, value, upscaling_pow, nbits):
        #print
        #print 'Encoding', value, "using upscaling power:", upscaling_pow
        value_scaled = value * ( 2**(-upscaling_pow))
        #print ' --Value Scaled:', value_scaled
        res = int( round( value_scaled * (2**(nbits-1) ) ) )
        #print ' --Value int:', res
        return res


    def encode_value(self, value, upscaling_pow):
        return self.encode_value_cls(value, upscaling_pow, nbits=self.nbits)


    def ActionNodeStd(self, o):

        vmin = o.annotations['node-value-range'].min
        vmax = o.annotations['node-value-range'].max

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

    def ActionFunctionDefInstantiationParameter(self,o):
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
        o.annotations['fixed-point-format'] = FixedPointData( upscale = upscaling_pow, const_value_as_int = self.encode_value(v, upscaling_pow),  datatype=self.datatype)

    def ActionSymbolicConstant(self, o):
        self.ActionConstant(o)
    def ActionRegimeDispatchMap(self, o):
        self.ActionNodeStd(o)
    def ActionConstantZero(self, o):
        self.ActionNodeStd(o)
    def ActionRandomVariable(self, o, **kwargs):
        self.ActionNodeStd(o)
    def ActionRandomVariableParameter(self, o, **kwargs):
        self.ActionNodeStd(o)
    def ActionOnEventDefParameter(self, o, ):
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
        pass
    def ActionInEventPortParameter(self, o):
        pass
    def ActionOutEventPort(self, o):
        pass
    def ActionInEventPort(self, o):
        pass
    def ActionEmitEvent(self, o):
        pass
