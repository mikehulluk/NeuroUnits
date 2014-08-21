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

from neurounits.errors import ASTMissingAnnotationError


class ASTTreeAnnotationManager(object):

    def __init__(self):
        self._annotators = {}

    def add_annotator(self, name, annotator):
        assert not name in self._annotators
        self._annotators[name] = annotator


class ASTNodeAnnotationData:

    def __init__(self, node):
        self._node = node
        self._mgr = None

        self._data = {}

    def __str__(self):
        return '<ASTNodeAnnotationData: %s >' % str(self._data)

    def add(self, key, value):
        assert not key in self._data
        self._data[key] = value

    def add_overwrite(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        try:
            return self._data[key]
        except KeyError:
            raise ASTMissingAnnotationError(node=self._node, annotation=key)

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def get_summary_str(self):
        if not self._data:
            return ''
        return '[Anns: ' + str(self._data) + ']'

    def get(self, *args, **kwargs):
        return self._data.get(*args, **kwargs)


class ASTTreeAnnotator(object):

    def annotate_ast(self, component):
        raise NotImplementedError()


