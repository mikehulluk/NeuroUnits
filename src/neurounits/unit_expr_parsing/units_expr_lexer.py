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


import ply.lex
from neurounits.unit_errors import UnitError



class UnitExprLexer(object):
    reserved = {
        'if': 'IF',
        'else': 'ELSE',

        'from': 'FROM',
        'import': 'IMPORT',
        'as': 'AS',

        'library': 'LIBRARY',

        'namespace': 'NAMESPACE',
        'define_component': 'DEFINE_COMPONENT',
        'regime': 'REGIME',
        'transition_to': 'TRANSITION_TO',
        'on': 'ON',
        'crosses': 'CROSSES',
        'rising': 'RISING',
        'falling': 'FALLING',

        'emit': 'EMIT',
        'rtgraph': 'RTGRAPH',

        'define_compound_component': 'DEFINE_COMPOUND',
        'instantiate' : 'INSTANTIATE',
        'connect' : 'CONNECT',
        'merge':'MERGE',
        'rename':'RENAME',
        'to':'TO',

        'define_multiport_type': 'DEFINE_MULTIPORT_TYPE',

        'multiport': 'MULTIPORT',
        'set':'SET',

        'multiconnect':'MULTICONNECT',
        'initial':'INITIAL',

        'and':'AND_KW',
        'or':'OR_KW',
        'not':'NOT_KW',

        'ar_model': 'AR_MODEL',


        'TIME': 'TIME',
        'INPUT': 'INPUT',
        'OUTPUT':'OUTPUT',
        'PARAMETER':'PARAMETER',
        'SUMMED_INPUT':'SUMMED_INPUT',

        'in': 'IN',
        'out': 'OUT',

        }

    tokens = [


        #'MULTIPORT_IN',
        #'MULTIPORT_OUT',
        'COMPOUNDPORT_IN',
        'COMPOUNDPORT_OUT',
        'COMPOUNDPORT_IN_OPT',
        'COMPOUNDPORT_OUT_OPT',

        'CONNECTION_SYMBOL',
        'IO_MARKER',

        #'IO_LINE',
        'INTEGER',
        'FLOAT',
        'SLASH',
        'LBRACKET',
        'RBRACKET',
        'LCURLYBRACKET',
        'RCURLYBRACKET',
        'ALPHATOKEN',
        'TIMES',
        'PLUS',
        'MINUS',
        'COMMA',
        'EQUALS',
        'COLON',
        'TIMESTIMES',
        'PRIME',
        'LSQUAREBRACKET',
        'RSQUAREBRACKET',
        'SEMICOLON',
        'DOT',
        'LESSTHAN',
        'GREATERTHAN',
        'AND_SYM',
        'OR_SYM',
        'NOT_SYM',

        'TILDE',


        'METADATA',

        ] + list(reserved.values())


    def t_FLOAT(self, t):
        r"""(([-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?)|([-]?[0-9]+([eE][+-]?[0-9]+)))\s*"""
        t.value = float(t.value.strip())
        return t

    def t_INTEGER(self, t):
        r"""[-]?[0-9]+\s*"""
        t.value = int(t.value.strip())
        return t

    def t_ALPHATOKEN(self, t):
        r"""[a-zA-Z_]+\s*"""
        t.value = t.value.strip()
        t.type = UnitExprLexer.reserved.get(t.value, t.type)
        return t

    WS = '\s*'

    # Automatically slurp up trailing whitespace:

    t_COMPOUNDPORT_IN = r"""==>>""" + WS
    t_COMPOUNDPORT_OUT = r"""<<==""" + WS
    t_COMPOUNDPORT_IN_OPT = r"""==\?>""" + WS
    t_COMPOUNDPORT_OUT_OPT = r"""<\?==""" + WS

    #t_MULTIPORT_IN =  r'<in>' + WS
    #t_MULTIPORT_OUT =  r'<out>' + WS


    #t_IO_LINE = r"""<=> [^;]*"""  + WS
    t_METADATA = r"""METADATA [^;]*"""  + WS
    t_IO_MARKER = r"""<=>""" + WS


    t_MINUS = r"""-""" + WS
    t_CONNECTION_SYMBOL = r"""<==>""" + WS

    t_LESSTHAN = r"""<""" + WS
    t_GREATERTHAN = r""">""" + WS
    t_SLASH = r"""/""" + WS
    t_LBRACKET = r"""\(""" + WS
    t_RBRACKET = r"""\)""" + WS
    t_LCURLYBRACKET = r"""\{""" + WS
    t_RCURLYBRACKET = r"""\}""" + WS
    t_LSQUAREBRACKET = r"""\[""" + WS
    t_RSQUAREBRACKET = r"""\]""" + WS
    t_TIMESTIMES = r"""\*\*""" + WS
    t_PRIME = r"""'""" + WS
    t_SEMICOLON = r""";""" + WS

    t_DOT = r"""\.""" + WS
    t_TIMES = r"""\*""" + WS
    t_PLUS = r"""\+""" + WS

    t_COMMA = r""",""" + WS
    t_COLON = r""":""" + WS
    t_EQUALS = r"""=""" + WS

    t_NOT_SYM = r"""!""" + WS
    t_AND_SYM = r"""&""" + WS
    t_OR_SYM = r"""\|""" + WS
    t_TILDE = r"""~""" + WS







    def t_error(self, t):
        raise UnitError("Illegal character '%s'" % t.value[0])

    def __init__(self):
        self.lexer = ply.lex.lex(module=self)

    def input(self, *args, **kwargs):
        return self.lexer.input(*args, **kwargs)

    def token(self, *args, **kwargs):
        t = self.lexer.token(*args, **kwargs)



        #print 'TOKEN:',t

        return t


