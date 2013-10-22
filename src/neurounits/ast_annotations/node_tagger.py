from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits import ast




class NodeTagger(ASTActionerDefault):
    def __init__(self, manual_tags, **kwargs):
        self.manual_tags = manual_tags
        super(NodeTagger, self).__init__(**kwargs)

    def ActionNode(self,o):
        if not 'tags' in o.annotations:
            o.annotations['tags'] = set()

        if not isinstance(o, ast.ASTSymbolNode):
            return
        if o.symbol in self.manual_tags:
            o.annotations['tags'] |= set([t.strip() for t in self.manual_tags[o.symbol].split(",")])


