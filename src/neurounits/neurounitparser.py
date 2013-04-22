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

from neurounits.unit_expr_parsing import units_expr_yacc
from neurounits.misc import SeqUtils

import neurounits.nulogging as logging

class NeuroUnitParserOptions(object):
    def __init__(  self,
                    allow_unused_parameter_declarations=False,
                    allow_unused_suppliedvalue_declarations = False):
        self.allow_unused_parameter_declarations = allow_unused_parameter_declarations
        self.allow_unused_suppliedvalue_declarations = allow_unused_suppliedvalue_declarations



class NeuroUnitParser(object):

    @classmethod
    def get_defaultBackend(cls):
        from .units_backends.mh import MHUnitBackend as defaultbackend
        return defaultbackend()

    @classmethod
    def Unit(cls, text, debug=False, backend=None):
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L1_Unit, backend=backend )

    @classmethod
    def QuantitySimple(cls, text, debug=False, backend=None):
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L2_QuantitySimple, backend=backend )

    @classmethod
    def QuantityExpr(cls, text, debug=False, backend=None):
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L3_QuantityExpr, backend=backend)

    @classmethod
    def Function(cls, text, debug=False, backend=None):
        assert False
        """ Should return a callable"""
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L1_Unit, backend=backend)


    @classmethod
    def File(cls, text, working_dir=None, debug=False, backend=None, options=None, name=None ):
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L6_TextBlock, working_dir=working_dir, backend=backend, options=options, name=name)

    @classmethod
    def Parse9MLFile(cls, text, debug=False, backend=None, working_dir=None, options=None, **kwargs):
        logging.log_neurounits.info('Parse9MLFile:')
        logging.log_neurounits.info('Options: %s'%options)
        logging.log_neurounits.info('Text: \n%s' % text)
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.N6_9MLFile, working_dir=working_dir, backend=backend, options=options, **kwargs)


    @classmethod
    def Parse9MLFiles(cls, filenames, debug=False, backend=None, working_dir=None, options=None, **kwargs):
        library_manager = None
        for filename in filenames:
            with open(filename) as f:
                library_manager = cls.Parse9MLFile(text = f.read(), library_manager=library_manager, debug=debug, backend=backend, working_dir=working_dir, options=options)
        return library_manager





def MQ1(s):
    return NeuroUnitParser.QuantitySimple(s)

