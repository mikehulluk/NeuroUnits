from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits import ast




class NodeTagger(ASTActionerDefault):
    def __init__(self, manual_tags):
        self.manual_tags = manual_tags

    def ActionNode(self,o):
        o.annotations['tags'] = []
        
        if not isinstance(o, ast.ASTSymbolNode):
            return
        if o.symbol in self.manual_tags:
            o.annotations['tags'] +=self.manual_tags[o.symbol].split(",")


