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

from neurounits.visitors import ASTActionerDefault
from neurounits.visitors import SingleVisitPredicate
from neurounits.ast_annotations.common import _NodeRangeFloat


class RangeExpander(ASTActionerDefault):

    def __init__(self, expand_by=0.25):
        super(RangeExpander, self).__init__(action_predicates=[SingleVisitPredicate()])
        self.expand_by = expand_by

    def ActionNode(self, o):
        if not 'node-value-range' in o.annotations:
            return

        if o.annotations['node-value-range'].min == o.annotations['node-value-range'].max:
            val = o.annotations['node-value-range'].min
            if val > 0:
                min_ = val * (1 - self.expand_by)
                max_ = val * (1 + self.expand_by)
            else:
                min_ = val * (1 + self.expand_by)
                max_ = val * (1 - self.expand_by)
        else:
            rng = o.annotations['node-value-range']
            rng_width = rng.max - rng.min
            assert rng_width > 0
            min_ = rng.min - rng_width * self.expand_by
            max_ = rng.max + rng_width * self.expand_by

        o.annotations['node-value-range'] = _NodeRangeFloat(
            min_=min_,
            max_=max_
        )

        assert (o.annotations['node-value-range'].min < o.annotations['node-value-range'].max) or ( o.annotations['node-value-range'].min == o.annotations['node-value-range'].max == 0)


