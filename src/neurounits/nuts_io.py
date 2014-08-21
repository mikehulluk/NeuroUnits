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

import json
import neurounits
import copy
import math


from neurounits.errors import NutsIOValidationError



class NutsIO(object):

    @classmethod
    def load(cls, filename):
        options = NutsOptions()
        nuts_lines = []

        src_lines = None
        if hasattr(filename, 'read'):
            src_lines = filename.readlines()
        else:
            with open(filename) as f:
                src_lines = f.readlines()


        for (lineno, line) in enumerate(src_lines):
            line = line.strip()
            if not line:
                continue
            elif line.startswith('#@'):
                options = copy.deepcopy(options)
                options.update(line[2:])
            elif line.startswith('#'):
                pass
            else:
                nuts_lines.append(NutsIOLine(line=line, lineno=lineno, options=options))


        return nuts_lines

    @classmethod
    def validate(cls, filename):
        print 'Checking nuts files', filename
        nuts_lines = cls.load(filename)

        for ln in nuts_lines:
            print 'Validating:', ln.line
            res = ln.validate()
            if not res:
                raise NutsIOValidationError('NUTS Validation failed: %s' % ln.line)

        print len(nuts_lines)







default_eps = 1.e-14

class NutsOptions():
    valid_attrs = {
        'type': None,
        'test-gnu-unit':True,
        'eps': default_eps
        }

    def __init__(self):
        for (k, v) in NutsOptions.valid_attrs.items():
            setattr(self, k, v)

    def update(self, line):
        line = line.replace("'", '"')
        new_options = json.loads(line)
        for (k, v) in new_options.items():
            assert k in NutsOptions.valid_attrs, 'Invalid option: %s' % k
            setattr(self, k, v)









def compare_l1A(u1, u2, eps=None):
    return u1==u2
    #eps = eps if eps is not None else default_eps
    #return math.fabs(float(u1-u2))< eps
    #return u1==u2

def compare_l1B(u1,u2, eps=None):
    eps = eps if eps is not None else default_eps
    return math.fabs((u1-u2).float_in_si())< eps

def compare_l2(u1,u2, eps=None):
    eps = eps if eps is not None else default_eps
    return math.fabs((u1-u2).float_in_si())< eps

parse_func_lut = {
        'L1A':neurounits.NeuroUnitParser.Unit,
        'L1B':neurounits.NeuroUnitParser.QuantitySimple,
        'L2':neurounits.NeuroUnitParser.QuantityExpr,
        }

comp_func_lut = {
        'L1A': compare_l1A,
        'L1B': compare_l1B,
        'L2': compare_l2,
        }




class NutsIOLine(object):
    def __init__(self, line, lineno, options):

        line = line.strip()

        if line.startswith('!!'):
            self.line = line[2:]
            self.is_valid = False
        else:
            self.line = line
            self.is_valid = True
        self.lineno = lineno
        self.options = options

    def validate(self):

        if self.is_valid:
            return self.test_valid()
        else:
            return self.test_invalid()

    def test_valid(self):
        parse_func = parse_func_lut[self.options.type]
        comp_func = comp_func_lut[self.options.type]
        if '==' in self.line:
            toks = self.line.split('==')

            for t in toks[1:]:
                print ' -- Checking: %s == %s' % tuple([toks[0], t])
                print self.options.__dict__
                are_equal = comp_func(
                        parse_func(toks[0]),
                        parse_func(t),
                        eps=self.options.eps
                        )
                if not are_equal:
                    return False
            return True

        if '!=' in self.line:
            toks = self.line.split('!=')
            assert len(toks) == 2
            print ' -- Checking: %s != %s' % tuple(toks)
            are_equal = comp_func(
                    parse_func(toks[0]),
                    parse_func(toks[1])
                    )
            if are_equal:
                return False
            return True

        else:
            # Make sure all the tokens (separated by commas) can be parsed'
            tokens = self.line.split(',')
            for t in tokens:
                parse_func(t)
            return True


    def test_invalid(self):
        parse_func = parse_func_lut[self.options.type]
        comp_func = comp_func_lut[self.options.type]
        for tok in self.line.split(','):
            try:
                print ' -- Checking: %s is invalid' % tok
                parse_func(tok)
                # An exception should be raised, so we shouldn't get here:!
                return False
            except Exception, e:
                print ' -- Exception raised (OK)!', e
                pass
        return True


