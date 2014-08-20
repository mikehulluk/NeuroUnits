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


import pkg_resources
import neurounits.nulogging as logging

class NeuroUnitParserOptions(object):
    def __init__(  self,
                    allow_unused_parameter_declarations=False,
                    allow_unused_suppliedvalue_declarations = False):
        self.allow_unused_parameter_declarations = allow_unused_parameter_declarations
        self.allow_unused_suppliedvalue_declarations = allow_unused_suppliedvalue_declarations



class NeuroUnitParser(object):
    """
    Interface for parsing NeuroUnit strings and equations
    """

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
    def File(cls, text, working_dir=None, debug=False, backend=None, options=None, name=None ):
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L6_TextBlock, working_dir=working_dir, backend=backend, options=options, name=name)

    @classmethod
    def Parse9MLFile(cls, input_, debug=False, backend=None, working_dir=None, options=None, **kwargs):


        text = None

        if hasattr(input_, 'read'):
            text = input_.read()

        elif isinstance(input_, basestring):

            # 1. Lets try and open the file (normal):
            if not text:
                try:
                    with open(input_) as f:
                        text = f.read()
                except IOError:
                    pass
                except:
                    raise

            # 2. Lets try and open the file (as resource):
            if not text:
                try:
                    text = pkg_resources.resource_string('neurounits', input_)
                except IOError:
                    pass
                except:
                    raise

            # 3. Let assume that string is the contents:
            if not text:
                text = input_

        else:
            assert False, 'Unexpected input: %s %s' % ( type(input_), input_)



        logging.log_neurounits.info('Parse9MLFile:')
        logging.log_neurounits.info('Options: %s'%options)
        logging.log_neurounits.info('Text: \n%s' % text)
        backend = backend or cls.get_defaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.N6_9MLFile, working_dir=working_dir, backend=backend, options=options, **kwargs)


    @classmethod
    def Parse9MLFiles(cls, inputs, debug=False, backend=None, working_dir=None, options=None, **kwargs):
        library_manager = None
        for input_ in inputs:
            library_manager = cls.Parse9MLFile(input_ = input_, library_manager=library_manager, debug=debug, backend=backend, working_dir=working_dir, options=options)
        return library_manager




    @classmethod
    def _string_to_expr_node(cls, s, working_dir=None, debug=False, backend=None, options=None, ):
        import neurounits

        print 'Converting ', s, 'to nodes:'

        if isinstance(s, basestring):
            backend = backend or cls.get_defaultBackend()
            s = units_expr_yacc.parse_expr(s, parse_type=units_expr_yacc.ParseTypes.L6_ExprNode, working_dir=working_dir, backend=backend, options=options,)
            return s
        if isinstance(s, (float,int)):
            from neurounits.units_backends.mh import MMUnit,MMQuantity
            s = neurounits.ast.ConstValue( value=MMQuantity(s, MMUnit() ) )
        
        print s, type(s)
        assert isinstance( s, neurounits.ast.ASTExpressionObject) 
        return s






def MQ1(s):
    return NeuroUnitParser.QuantitySimple(s)

