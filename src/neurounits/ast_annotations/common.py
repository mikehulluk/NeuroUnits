#!/usr/bin/python
# -*- coding: utf-8 -*-




from neurounits.ast_annotations.bases import ASTTreeAnnotator

import numpy as np

from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits import ast

from node_toint import NodeToIntAnnotator
from node_tagger import NodeTagger
from node_fixedpointannotator import NodeFixedPointFormatAnnotator


class _NodeRangeFloat(object):
    def __init__(self, min_, max_):
        self.min_ = min_
        self.max_ = max_

    def __repr__(self):
        return '<NodeRangeFloat: %s, %s>' % (self.min_, self.max_)

    @property
    def min(self):
        return self.min_
    @property
    def max(self):
        return self.max_

class NodeRange(object):
    def __init__(self, min=None, max=None):

        from neurounits import NeuroUnitParser
        if isinstance(min, basestring):
            min = NeuroUnitParser.QuantitySimple(min)
        if isinstance(max, basestring):
            max = NeuroUnitParser.QuantitySimple(max)

        if min is not None and max is not None:
            assert min.is_compatible(max.unit)


        self._min = min
        self._max = max

    def __repr__(self):
        return '<NodeRange: %s to %s>' % (self._min, self._max)

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, value):
        self._min = value

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, value):
        self._max = value

