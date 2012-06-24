#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
from unit_errors import DuplicateKeyError


import os
def EnsureExisits(l):
    if not os.path.exists(l):
        os.makedirs(l)
    return l

def safe_dict_merge(*args):
    out_dct = {}
    for dct in args:
        for k,v in dct.iteritems():
            if k in out_dct:
                raise DuplicateKeyError(k)
            out_dct[k] = v
    return out_dct

#def ExpectSingle(l):
#    if not len(l) == 1:
#        raise ValueError("Expect list of len 1, found iterable len: %d"% len(l))
#    #assert len(l) == 1
#    return l[0]



class SingleSetDict(dict):

    def __setitem__(self, key, val):
        if key in self:
            raise ValueError('SingleSetDictionary - setting Key twice: %s'%key)
        dict.__setitem__(self, key, val)



import UserDict
#http://code.activestate.com/recipes/305268-chained-map-lookups/
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
                #print mapping
                return mapping[key]
            except KeyError:
                pass
        raise KeyError(key)



def IterateDictValueByKeySorted(d):
    keys = sorted( d.keys() )
    for k in keys:
        yield d[k]




import json

def read_json(s):
    print 'Reading JSON:', s
    x = json.loads(s)
    return x


#def SeqUtils.expect_single(l):
#    assert len(l) == 1
#    return l[0]







