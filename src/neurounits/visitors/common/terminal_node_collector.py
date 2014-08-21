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

from neurounits.visitors.bases.base_actioner import SingleVisitPredicate
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from collections import defaultdict
import itertools

import neurounits

class EqnsetVisitorNodeCollector(ASTActionerDefault):

    def __init__(self, obj=None):
        self.nodes = defaultdict(set)
        ASTActionerDefault.__init__(self,
                                    action_predicates=[SingleVisitPredicate()])
        if obj is not None:
            self.visit(obj)


    def all(self):
        return itertools.chain(*self.nodes.values())

    def ActionNode(self, n):
        N = type(n)

        # Special cases for builtin things, that might be subclasses:
        if isinstance(n, neurounits.ast.RandomVariable):
            N = neurounits.ast.RandomVariable
        #if isinstance(n, neurounits.ast.BuiltinFunction):
        #    N = neurounits.ast.BuiltinFunction

        self.nodes[N].add(n)


