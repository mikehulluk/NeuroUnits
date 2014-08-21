


from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault


class NodeToIntLabeller(ASTActionerDefault):


    def __init__(self, component):
        self.node_to_int = {}
        self.int_to_node = {}
        super(ASTActionerDefault,self).__init__()
        self.visit(component)

    def ActionNode(self, n, **kwargs):
        if n in self.node_to_int:
            return

        val = len(self.node_to_int)
        self.node_to_int[n] = val
        self.int_to_node[val] = n




