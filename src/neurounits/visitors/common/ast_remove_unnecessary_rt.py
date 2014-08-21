
#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------

import neurounits.ast as ast

class RemoveUnusedRT(object):

    def visit(self, component):
        from neurounits.visitors.common.ast_replace_node import ReplaceNode

        if not isinstance(component, ast.NineMLComponent):
            return

        # Lets look for any RT-graphs with a single Regime:
        for rt_graph in component.rt_graphs:
            if len(rt_graph.regimes) == 1:
                assert list(rt_graph.regimes)[0].name == None, 'This might not nessesarily be true...'

                # Does the assignment do lookups, based on this rt-graph?
                for ass in component.assignments + component.timederivatives:
                    if isinstance(ass.rhs_map, ast.EqnRegimeDispatchMap) and ass.rhs_map.get_rt_graph()==rt_graph:
                        #print 'Remapping RHS-Map to equation'
                        assert len(ass.rhs_map.rhs_map) == 1
                        direct_target = list(ass.rhs_map.rhs_map.values())[0]
                        ReplaceNode.replace_and_check(
                                srcObj = ass.rhs_map,
                                dstObj = direct_target,
                                root=component
                                )


