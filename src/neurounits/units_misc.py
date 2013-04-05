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

import os
import UserDict

import json

from .unit_errors import DuplicateKeyError


def EnsureExisits(l):
    if not os.path.exists(l):
        os.makedirs(l)
    return l


def safe_dict_merge(*args):
    out_dct = {}
    for dct in args:
        for (k, v) in dct.iteritems():
            if k in out_dct:
                raise DuplicateKeyError(k)
            out_dct[k] = v
    return out_dct


class SingleSetDict(dict):

    def __setitem__(self, key, val):
        if key in self:
            raise ValueError('SingleSetDictionary - setting Key twice: %s'
                              % key)
        dict.__setitem__(self, key, val)


# http://code.activestate.com/recipes/305268-chained-map-lookups/

class Chainmap(UserDict.DictMixin):

    """Combine multiple mappings for sequential lookup.

    For example, to emulate Python's normal lookup sequence:

        import __builtin__
        pylookup = Chainmap(locals(), globals(), vars(__builtin__))
    """

    def __init__(self, *maps):
        self._maps = maps

    def __getitem__(self, key):
        for mapping in self._maps:
            try:
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)


def IterateDictValueByKeySorted(d):
    keys = sorted(d.keys())
    for k in keys:
        yield d[k]



def read_json(s):
    x = json.loads(s)
    return x





class LookUpDict(object):
    def __init__(self, objs = None, unique_attrs=None, accepted_obj_types=None):
        self.unique_attrs = unique_attrs if unique_attrs is not None else []
        self.accepted_obj_types = accepted_obj_types

        self._objs = set([])
        if objs:
            for obj in objs:
                self._add_item(obj)

    def __repr__(self,):
        return '<LUD: %s>'% repr(self._objs)

    def get_attr_value(self, obj, attr):
        res =  getattr(obj, attr)
        print 'Finding attr: %s on:%s -> %s' %(attr,obj,res)
        return res


    def _add_item(self, obj, expect_existing=False):

        if self.accepted_obj_types:
            assert isinstance(obj, self.accepted_obj_types), 'Adding item of type: %s but I expected %s' %(type(obj), self.accepted_obj_types)

        # Some error checking:
        # Check we are not adding an object with an existing name:
        for unique_attr in self.unique_attrs:
            new_attr = self.get_attr_value(obj, unique_attr)
            existing_attrs = [ self.get_attr_value(o, unique_attr) for o in self._objs ]
            assert not new_attr in existing_attrs

        self._objs.add(obj)

    def get_objs_by(self, **kwargs):
        possible_objs = list( self._objs )
        for attr, value in kwargs.items():
            possible_objs = [ p for p in possible_objs if self.get_attr_value(p, attr) == value]
        return possible_objs



    def get_single_obj_by(self, **kwargs):
        possible_objs = self.get_objs_by(**kwargs)
        assert len(possible_objs) == 1
        return possible_objs[0]

    def get_objects_attibutes(self, attr=None, **kwargs):
        assert attr is not None

        possible_objs = self.get_objs_by(**kwargs)
        return [ getattr(p, attr) for p in possible_objs]

    def __iter__(self):
        return iter(self._objs)

    def __len__(self):
        return len(self._objs)

    def has_obj(self, **kwargs):
        r = self.get_objs_by(**kwargs)
        assert len(r) in (0,1)
        if len(r) == 0:
            return False
        else:
            return True



    def copy(self):
        return LookUpDict( objs = self._objs, unique_attrs=self.unique_attrs, accepted_obj_types=self.accepted_obj_types)




