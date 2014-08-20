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

import string


class ASTObject(object):

    def is_resolved(self):
        return True

    def __init__(self):
        self._metadata = None

        from neurounits.ast_annotations import ASTNodeAnnotationData
        self._annotations = ASTNodeAnnotationData(node=self)

    def set_metadata(self, md):
        self._metadata = md

    # Annotations:
    @property
    def annotations(self):
        assert self._annotations is not None
        return self._annotations

    # These should be implemented to allow nodes to be printed in different
    # situations:
    def _summarise_node_full(self):
        raise NotImplementedError()

    def _summarise_node_short(self, use_latex=False):
        raise NotImplementedError()

    def summarise_node_full(self):
        try:
            print type(self)
            return self._summarise_node_full()
        except NotImplementedError:
            return '[??]'

    def summarise_node_short(self):
        try:
            return self._summarise_node_short()
        except NotImplementedError:
            print self
            assert False
            return '[??]'

    def __str__(self):
        return unicode(self)

    def __repr__(self):
        return unicode(self)

    def __unicode__(self):
        return string.Template('<${class_name} [id:${id}] ${node_data} ${annotation_data}>').substitute(
                class_name=type(self).__name__.split('.')[-1], id=id(self),
                node_data=self.summarise_node_full(),
                annotation_data=self.annotations.get_summary_str()
                )







