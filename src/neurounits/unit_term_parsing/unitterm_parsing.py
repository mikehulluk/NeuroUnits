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

import ply

from ..unit_errors import UnitError, InvalidUnitTermError
from .unitterm_lexing import UnitTermLexer
from ..units_data_unitterms import UnitTermData
from ..units_misc import EnsureExisits




# Import the tokens:
tokens = UnitTermLexer().tokens


# YACC'ing
##########

def p_unit_term_unpowered_no_multipler(p):
    """unit_term_unpowered :  long_basic_unit
    """
    p[0] = p[1]

def p_unit_term_unpowered_with_multipler(p):
    """unit_term_unpowered :    long_basic_multiplier long_basic_unit
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



def p_error(p):
    raise UnitError('Parsing Error %s' % p)









import os

username = 'tmp_%d' % os.getuid()
tables_loc = EnsureExisits('/tmp/%s/nu/yacc/parse_term' % username)
unit_expr_parser = ply.yacc.yacc(start='unit_term_unpowered',  tabmodule='neurounits_parsing_parse_eqn_term', outputdir=tables_loc,errorlog=ply.yacc.NullLogger() )



def _parse_candela(text,backend):
    assert text.endswith('cd')


def _parse_single_letter(text,backend):
    assert len(text) == 1
    lut = UnitTermData.getUnitLUTShort(backend=backend)
    if not text in lut:
        raise InvalidUnitTermError('Unknown unit: %s' % text)
    return lut[text]



def _parse_double_letter(text,backend):
    assert len(text) == 2
    str_prefix = text[0]
    str_unit = text[1]

    #  prefix:
    lut_prefix = UnitTermData.getMultiplierLUTShort(backend=backend)
    if not str_prefix in lut_prefix:
        raise InvalidUnitTermError('Unknown prefix: "%s" while parsing: %s' % (str_prefix,text))
    prefix_term = lut_prefix[str_prefix]

    #  unit:
    lut_unit = UnitTermData.getUnitLUTShort(backend=backend)
    if not str_unit in lut_unit:
        raise InvalidUnitTermError('Unknown unit: "%s" while parsing: %s' % (str_unit,text))
    unit_term = lut_unit[str_unit]

    return prefix_term * unit_term



def parse_term(text, backend):

    text = text.strip()


    lut_unit_short= UnitTermData.getUnitLUTShort(backend=backend)
    lut_prefix_short = UnitTermData.getMultiplierLUTShort(backend=backend)


    # Single letters are single:
    if len(text) == 0:
        raise InvalidUnitTermError()

    # Is it just a unit string (no prefix)?, 'Hz', 'm', 'cd'
    if text in lut_unit_short:
        return lut_unit_short[text]

    # If its only one letter long, we have a problem:
    if len(text) == 1:
        raise InvalidUnitTermError('Unknown unit: "%s" ' % text)

    # What about if we ignore the first letter, then is is in? e.g. 'MHz'
    if text[1:] in lut_unit_short:
        if text[0] not in lut_prefix_short:
            raise InvalidUnitTermError('Unknown prefix: "%s" while parsing: %s' % (text[0],text))

        prefix_term = lut_prefix_short[text[0]]
        unit_term = lut_unit_short[text[1:]]
        return prefix_term * unit_term


    # No luck so far? Its probably a long-unit:
    unit_expr_parser.backend = backend

    lexer = UnitTermLexer()
    res = unit_expr_parser.parse(text, lexer=lexer)

    return res


