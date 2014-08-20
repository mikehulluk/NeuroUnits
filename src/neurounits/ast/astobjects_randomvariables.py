

from .astobjects import ASTExpressionObject
from neurounits.units_misc import LookUpDict
from neurounits.units_backends.mh import MMUnit


class InvalidParametersError(RuntimeError):
    pass

class RandomVariable(ASTExpressionObject):
    def __init__(self, parameters, modes):
        super(RandomVariable, self).__init__()

        self.functionname = self.Meta._name
        self.parameters = LookUpDict(parameters)
        self.modes = modes

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality(MMUnit())

        # Check that the parameter-names match the expected names:
        p_found = set([p.name for p in parameters])
        p_expected = set(self.Meta.expected_parameters)
        if p_found != p_expected:
            raise InvalidParametersError('Bad parameters for RandomVariable: %s [Expected: %s, Found:%s]' %(self.functionname, p_expected, p_found) )

    def accept_visitor(self, v, XX_mhchecked=False, **kwargs):
        return v.VisitRandomVariable(self, **kwargs)















class RandomVariableParameter(ASTExpressionObject):
    def __init__(self, name, rhs_ast):
        super(RandomVariableParameter, self).__init__()
        self.name = name
        self.rhs_ast = rhs_ast

        # Assume that the parameters and random variables are dimensionless
        self.set_dimensionality(MMUnit())

    def accept_visitor(self, v, **kwargs):
        return v.VisitRandomVariableParameter(self, **kwargs)



class AutoRegressiveModel(ASTExpressionObject):
    def __init__(self, coefficients):
        super(AutoRegressiveModel, self).__init__()
        self.coefficients = coefficients

        # Assume that the parameters and radnom variables are dimensionless
        self.set_dimensionality(MMUnit())

    def accept_visitor(self, v, **kwargs):
        return v.VisitAutoRegressiveModel(self, **kwargs)
