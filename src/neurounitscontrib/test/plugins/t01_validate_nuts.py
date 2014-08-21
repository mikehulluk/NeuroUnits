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


from neurounitscontrib.test import TestingPluginBase


from neurounits import NutsIO, Locations


class TestNutsFiles(TestingPluginBase):

    def __init__(self,):
        self.results = None

    def get_name(self):
        return 'Test NUTS'

    def print_results(self):
        good_res, bad_res, error_res = self.results
        print 'Good:'
        for res in good_res:
            print res

        print 'Bad:'
        for res in bad_res:
            print res

        print 'Error:'
        for res in error_res:
            print res


    def run(self, args):
        assert self.results == None





        files = Locations.Test.get_nuts_fileobjs()
        print 'Files:', files


        good_results = []
        bad_results = []
        error_results = []
        for fname in files:
            try:
                res = NutsIO.validate(fname)
                good_results.append((fname, res))
            except Exception, e:
                print 'Exception Raised'
                error_results.append((fname, e))



        self.results = good_results, bad_results, error_results
        self.print_results()


