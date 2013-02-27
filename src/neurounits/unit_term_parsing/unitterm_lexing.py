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


import ply.lex as lex


from ..unit_errors import UnitError


from ..units_data_unitterms import UnitTermData



class UnitTermLexer(object):

    def add_token(self, t):
        self.tokens.append(t)

    def __init__(self, **kwargs):
        self.tokens = []

        # Register all the MULTIPLIER regular expressions:
        # [Programmatically, opposed to writing lines like:
        # t_SHORT_GIGA  = r"""G"""
        # t_LONG_GIGA  = r"""giga"""
        # ]

        for (name, abbr) in UnitTermData.getMultiplierKeys():
            #vName_short = 'SHORT_%s' % name.upper()
            vName_long = 'LONG_%s' % name.upper()
            #setattr(self, 't_' + vName_short, r" %s" % abbr)
            setattr(self, 't_' + vName_long, name)
            #self.add_token(vName_short)
            self.add_token(vName_long)

        # Register all the UNIT regular expressions:
        # [Programmatically, opposed to writing lines like:
        # t_SHORT_VOLT = r"""V"""
        # t_LONG_VOLT = r"""volt"""
        # ]
        for (name, abbr) in UnitTermData.getUnitKeys():
            #vName_short = 'SHORT_%s' % name.upper()
            vName_long = 'LONG_%s' % name.upper()

            # Ignore 'm' terms, since they should be
            #if abbr != 'm':
            #    setattr(self, 't_' + vName_short, r" %s" % abbr)
            setattr(self, 't_' + vName_long, name)
            #self.add_token(vName_short)
            self.add_token(vName_long)


        self.lexer = lex.lex(module=self, **kwargs)


    def input(self,*args, **kwargs):
        return self.lexer.input(*args, **kwargs)

    def token(self, *args, **kwargs):
        t = self.lexer.token(*args, **kwargs)
        return t

    def t_error(self, t):
        raise UnitError("Illegal character '%s'" % t.value[0])

