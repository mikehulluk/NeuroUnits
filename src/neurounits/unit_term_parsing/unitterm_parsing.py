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
import ply

from ..unit_errors import UnitError
from unitterm_lexing import UnitTermLexer
from ..units_data_unitterms import UnitTermData
#from morphforge.core.mgrs.locmgr import LocMgr
from ..units_misc import EnsureExisits




# Import the tokens:
tokens = UnitTermLexer().tokens




# YACC'ing
##########

def p_unit_term_unpowered_no_multipler(p):
    """unit_term_unpowered :    short_basic_unit
                              | long_basic_unit
    """
    p[0] = p[1]

def p_unit_term_unpowered_with_multipler(p):
    """unit_term_unpowered :    long_basic_multiplier long_basic_unit
                              | short_basic_multiplier short_basic_unit
                              """
    p[0] = p[1] * p[2]

def p_long_basic_unit(p):
    """long_basic_unit :  LONG_VOLT
                        | LONG_AMP
                        | LONG_SIEMEN
                        | LONG_JOULE
                        | LONG_OHM
                        | LONG_COULOMB
                        | LONG_FARAD
                        | LONG_METER
                        | LONG_GRAM
                        | LONG_SECOND
                        | LONG_KELVIN
                        | LONG_MOLE
                        | LONG_CANDELA
                        | LONG_MOLAR
                        | LONG_HERTZ
                        """
    unit_long_LUT = UnitTermData.getUnitLUTLong(backend=p.parser.backend)
    p[0] = unit_long_LUT[ p[1] ]

def p_short_basic_unit(p):
    """short_basic_unit : SHORT_VOLT
                        | SHORT_AMP
                        | SHORT_SIEMEN
                        | SHORT_JOULE
                        | SHORT_OHM
                        | SHORT_COULOMB
                        | SHORT_FARAD
                        | SHORT_METER
                        | SHORT_GRAM
                        | SHORT_SECOND
                        | SHORT_KELVIN
                        | SHORT_MOLE
                        | SHORT_CANDELA
                        | SHORT_MOLAR
                        | SHORT_HERTZ
                        """
    unit_short_LUT = UnitTermData.getUnitLUTShort(backend=p.parser.backend)
    p[0] = unit_short_LUT[ p[1] ]


def p_long_basic_multiplier(p):
    """long_basic_multiplier :  LONG_GIGA
                              | LONG_MEGA
                              | LONG_KILO
                              | LONG_CENTI
                              | LONG_MILLI
                              | LONG_MICRO
                              | LONG_NANO
                              | LONG_PICO
                              """
    multiplier_long_LUT = UnitTermData.getMultiplierLUTLong(backend=p.parser.backend)
    p[0] = multiplier_long_LUT[ p[1] ]


def p_short_basic_multiplier(p):
    """short_basic_multiplier :   SHORT_GIGA
                                | SHORT_MEGA
                                | SHORT_KILO
                                | SHORT_CENTI
                                | SHORT_MILLI
                                | SHORT_MICRO
                                | SHORT_NANO
                                | SHORT_PICO
                              """
    multiplier_short_LUT = UnitTermData.getMultiplierLUTShort(backend=p.parser.backend)
    p[0] = multiplier_short_LUT[ p[1] ]

def p_error(p):
    raise UnitError( "Parsing Error %s"%p )











tables_loc = EnsureExisits("/tmp/nu/yacc/parse_term")   
unit_expr_parser = ply.yacc.yacc(  start='unit_term_unpowered',  tabmodule="neurounits_parsing_parse_eqn_term", outputdir=tables_loc,errorlog=ply.yacc.NullLogger() )



def parse_term( text, backend ):

    text = text.strip()


    # CHECK FOR STANDARD DEFINITIONS:
    for u, u_def in UnitTermData.getSpecialCaseShortForms(backend=backend):
        if u == text:
            return u_def


    unit_expr_parser.backend = backend

    lexer = UnitTermLexer()
    res =  unit_expr_parser.parse(text, lexer=lexer, )

    return res


