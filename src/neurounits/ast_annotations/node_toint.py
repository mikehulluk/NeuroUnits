#!/usr/bin/python
# -*- coding: utf-8 -*-


from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault


class NodeToIntAnnotator(ASTActionerDefault):
    def __init__(self):
        self.node_to_int = {}
        self.int_to_node = {}
        super(ASTActionerDefault, self).__init__()


    def annotate_ast(self, component):
        assert self.node_to_int == {}
        self.visit(component)

    def ActionNode(self, n, **kwargs):
        if n in self.node_to_int:
            return

        val = len(self.node_to_int)
        self.node_to_int[n] = val
        self.int_to_node[val] = n
        n.annotations['node-id'] = val
