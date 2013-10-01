

#assert False, 'To remove!'

from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate
from neurounits.ast_annotations.common import _NodeRangeFloat


class RangeExpander(ASTActionerDefault):

    def __init__(self, ):
        super(RangeExpander, self).__init__( action_predicates=[SingleVisitPredicate()])
        self.expand_by = 0.25
    def ActionNode(self,o):
        #print o
        if not 'node-value-range' in o.annotations:
            #print 'Skipping'
            return

        if o.annotations['node-value-range'].min == o.annotations['node-value-range'] .max:
            val = o.annotations['node-value-range'].min
            if val > 0:
                min_ = val * (1-self.expand_by)
                max_ = val * (1+self.expand_by)
            else:
                min_ = val * (1+self.expand_by)
                max_ = val * (1-self.expand_by)
        else:
            rng = o.annotations['node-value-range']
            rng_width = rng.max - rng.min
            assert rng_width > 0
            min_ = rng.min - rng_width * self.expand_by
            max_ = rng.max + rng_width * self.expand_by
        
        o.annotations['node-value-range'] = _NodeRangeFloat(
            min_ = min_,
            max_ = max_
        )
        #print o, o.annotations
        #print 'Min:',  o.annotations['node-value-range'].min
        #print 'Max:',  o.annotations['node-value-range'].max
        assert (o.annotations['node-value-range'].min < o.annotations['node-value-range'].max) or ( o.annotations['node-value-range'].min == o.annotations['node-value-range'].max == 0)


