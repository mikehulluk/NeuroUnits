#from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing
from neurounits.visitors.bases.base_actioner import SingleVisitPredicate
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from collections import defaultdict
import itertools




class EqnsetVisitorNodeCollector(ASTActionerDefault):

    def __init__(self):
        self.nodes = defaultdict( set )
        ASTActionerDefault.__init__(self, action_predicates = [SingleVisitPredicate() ])

    def all(self):
        return itertools.chain( *self.nodes.values() )



    def ActionNode(self, n):
        self.nodes[type(n)].add(n)

