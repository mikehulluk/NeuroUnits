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


import mreorg

import sys
import os, traceback
import warnings

import numpy as np
import pylab





class Proxy(object):
    def __init__(self, target_object):
        self._count = {}
        self._obj = target_object

    def __getattr__(self, attr):
        if attr in self._count:
            self._count[attr]+=1
        else:
            self._count[attr]=1
        return getattr(self._obj, attr)

    def write(self, *args, **kwargs):
        rv = self._obj.write(*args, **kwargs)
        for filename, lineno, function, line in traceback.extract_stack():
            if 'print' in line:
                if os.environ.get('TRACE_PRINT', None) == 'traceback':
                    traceback.print_stack()
                else:
                    sys.stderr.write("%s:%d (%s): %s\n" % (filename, lineno, function, line))
                break

if os.environ.get('TRACE_PRINT', None):
    sys.stdout = Proxy(sys.stdout)
#sys.stdout = Proxy(sys.stdout)










from neurounitscontrib.demo import DemoPluginBase
class Demo4(DemoPluginBase):


    def get_name(self):
        return '4'

    def run(self, args):
        test4()






import pkg_resources


def test4():
    import neurounits

    src_files =  [pkg_resources.resource_stream('neurounits',f) for f in neurounits.Locations.get_default_9ml_locations()]
    library_manager = neurounits.NeuroUnitParser.Parse9MLFiles(src_files)

    print
    print 'Available MultiportInterfaceDefs:'
    for comp in library_manager.interfaces:
        print '  ',  repr(comp)
    print

    print 'Available Components:'
    for comp in library_manager.components:
        print '  ', repr(comp)
    print







    general_neuron_with_step_inj = library_manager.get('general_neuron_with_step_inj')


    res = general_neuron_with_step_inj.simulate(
                times = np.arange(0, 0.1,0.00001),
                )


    res.auto_plot()


def main():
    warnings.simplefilter('error', UserWarning)
    warnings.simplefilter('error', Warning)







    test4()
    pylab.show()


if __name__=='__main__':
    main()
