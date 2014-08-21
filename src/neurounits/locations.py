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
import pkg_resources

class Locations(object):

    @classmethod
    def get_default_9ml_locations(cls):
        src_loc = 'data/test_data/l4-9ml/std/'
        fnames = sorted( pkg_resources.resource_listdir('neurounits', src_loc) )
        fnames = [os.path.join(src_loc, f) for f in fnames]
        fnames = [fname for fname in fnames if fname.endswith('.9ml')]
        if not fnames:
            raise RuntimeError("Can't find any 9ml test files, perhaps the something in wring in packaging")
        return fnames



    class Test(object):
        @classmethod
        def get_nuts_fileobjs(cls):

            fobjs = [
                pkg_resources.resource_stream('neurounits', 'data/test_data/thesis_l1.nuts'),
                pkg_resources.resource_stream('neurounits', 'data/test_data/valid_l1.nuts')
                ]
            return fobjs
