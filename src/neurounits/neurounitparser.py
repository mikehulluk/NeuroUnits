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
import units_expr_yacc


class NeuroUnitParser(object):


    @classmethod
    def getDefaultBackend(cls):
        from units_backends.mh import MHUnitBackend as defaultbackend
        
        #from default import DefaultParsingBackend as defaultbackend
        return defaultbackend()


    @classmethod
    def Unit(cls, text, debug=False,backend=None):    
        backend = backend or cls.getDefaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L1_Unit, backend=backend ) 
        
    @classmethod
    def QuantitySimple(cls, text, debug=False,backend=None):
        backend = backend or cls.getDefaultBackend()    
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L2_QuantitySimple, backend=backend )

    @classmethod
    def QuantityExpr(cls, text, debug=False, backend=None):
        backend = backend or cls.getDefaultBackend()    
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L3_QuantityExpr, backend=backend)


    #@classmethod
    #def EqnSet(cls, text, debug=False, backend=None):
    #    backend = backend or cls.getDefaultBackend()    
    #    return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L4_EqnSet,backend=backend)
    
    @classmethod
    def Library(cls, text,debug=False, backend=None):
        backend = backend or cls.getDefaultBackend()    
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L5_Library,backend=backend)

    @classmethod
    def File(cls, text, working_dir=None,debug=False,backend=None ):
        backend = backend or cls.getDefaultBackend()
        return units_expr_yacc.parse_expr(text, parse_type=units_expr_yacc.ParseTypes.L6_TextBlock, working_dir=working_dir, backend=backend)
