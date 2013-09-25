

from .astobjects import ASTExpressionObject
from neurounits.units_misc import LookUpDict
from neurounits.units_backends.mh import MMQuantity, MMUnit


class RandomVariable(ASTExpressionObject):
    def __init__(self, function_name, parameters, modes ):
        super(RandomVariable,self).__init__()

        self.functionname = function_name
        self.parameters = LookUpDict(parameters)
        self.modes = modes

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality( MMUnit() )

    def accept_visitor(self, v, **kwargs):
        return v.VisitRandomVariable(self, **kwargs)



class RandomVariableParameter(ASTExpressionObject):
    def __init__(self, name, rhs_ast ):
        super(RandomVariableParameter,self).__init__()
        self.name = name
        self.rhs_ast = rhs_ast

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality( MMUnit() )

    def accept_visitor(self, v, **kwargs):
        return v.VisitRandomVariableParameter(self, **kwargs)



class AutoRegressiveModel(ASTExpressionObject):
    def __init__(self, coefficients):
        super(AutoRegressiveModel, self).__init__()
        self.coefficients = coefficients

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality( MMUnit() )

    def accept_visitor(self, v, **kwargs):
        return v.VisitAutoRegressiveModel(self, **kwargs)
