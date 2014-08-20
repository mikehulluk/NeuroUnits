
from astobjects_randomvariables import RandomVariable



class RandomVariableUniform(RandomVariable):
    class Meta:
        expected_parameters = ['min','max']
        _name = 'uniform'

    def accept_RVvisitor(self, v, **kwargs):
        return v.VisitRVUniform(self, **kwargs)

class RandomVariableNormal(RandomVariable):
    class Meta:
        expected_parameters = ['loc','scale']
        _name = 'normal'

    def accept_RVvisitor(self, v, **kwargs):
        return v.VisitRVNormal(self, **kwargs)



