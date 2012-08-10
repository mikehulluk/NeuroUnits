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
            'if':   'IF',
            'else': 'ELSE',
            'and':  'AND',
            'or':   'OR',
            'not':  'NOT',

            'from': 'FROM',
            'import':'IMPORT',
            'as':'AS',
            'LIBRARY':'LIBRARY',
            'EQNSET': 'EQNSET',

            }


    tokens = [
        "IO_LINE",
        "ONEVENT_SYMBOL",

        "INTEGER",
        "FLOAT",
        "SLASH",
        "SLASHSLASH",
        "WHITESPACE",
        "LBRACKET",
        "RBRACKET",
        "LCURLYBRACKET","RCURLYBRACKET",
        "ALPHATOKEN",
        "TIMES","PLUS","MINUSMINUS",
        "TILDE",
        "COMMA",
        "EQUALS",
        "COLON",
        "NO_UNIT",
        "TIMESTIMES",
        "NEWLINE",
#        "COMMENT",
        "PRIME",
        "LSQUAREBRACKET",
        "RSQUAREBRACKET",
        "SEMICOLON",

        "DOT",

        "LESSTHAN",
        "GREATERTHAN",



        ] + list(reserved.values())

    t_MINUSMINUS = r"""--"""

    def t_NO_UNIT(self, t):
        r"""NO_UNIT"""
        return t

    def t_FLOAT(self, t):
        #r"""[-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?"""
        r"""([-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?)|([-]?[0-9]+([eE][+-]?[0-9]+))"""
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t):
        r"""[-]?[0-9]+"""
        t.value = int(t.value)
        return t

    def t_ALPHATOKEN(self, t):
        r"""[a-zA-Z_]+"""
        t.type = UnitExprLexer.reserved.get(t.value, t.type)
        return t

    def t_COMMENT(self, t):
        r"""\#.*"""
        return t

    def t_NEWLINE(self, t):
        r"""\n+"""
        t.lexer.lineno += len(t.value)
        return t

    t_IO_LINE = r"""<=> [^;]*"""

    t_ONEVENT_SYMBOL = r"""==>>"""

    t_LESSTHAN = r"""<"""
    t_GREATERTHAN = r""">"""
    t_SLASHSLASH = r"""//"""
    t_SLASH = r"""/"""
    t_WHITESPACE = r"""[ \t]+"""
    t_LBRACKET = r"""\("""
    t_RBRACKET = r"""\)"""
    t_LCURLYBRACKET = r"""\{"""
    t_RCURLYBRACKET = r"""\}"""
    t_LSQUAREBRACKET = r"""\["""
    t_RSQUAREBRACKET = r"""\]"""
    t_TIMESTIMES = r"""\*\*"""
    t_PRIME = r"""'"""
    t_SEMICOLON = r""";"""

    t_TILDE = r"""~"""
    t_DOT = r"""\."""
    t_TIMES = r"""\*"""
    t_PLUS = r"""\+"""

    # t_NEWLINE = r"""\n"""

    t_COMMA = r""","""
    t_COLON = r""":"""
    t_EQUALS = r"""="""



    # {~xyz} units

    def t_error(self, t):
        raise UnitError("Illegal character '%s'" % t.value[0])


    def __init__(self):
        self.lexer = ply.lex.lex(module=self)

    def input(self, *args, **kwargs):
        return self.lexer.input(*args, **kwargs)

    def token(self, *args, **kwargs):
        t = self.lexer.token(*args, **kwargs)

        # print 'TOKEN:',t
        return t

