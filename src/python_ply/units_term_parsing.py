
from units_core import Unit, UnitError
import ply
from units_data import multipliers, units, special_unit_abbrs

multiplier_names_short = [ 'SHORT_%s'%m[0].upper() for m in multipliers]
multiplier_names_long =  [ 'LONG_%s'%m[0].upper() for m in multipliers]

unit_names_short = [ 'SHORT_%s'%m[0].upper() for m in units]
unit_names_long =  [ 'LONG_%s'%m[0].upper() for m in units]

tokens = multiplier_names_short + multiplier_names_long + unit_names_short + unit_names_long 

unitDefs = dict( [(u[0],u[2]) for u in units] + [(u[1],u[2]) for u in units] )
multiplierDefs = dict( [(u[0],Unit(powerTen=u[2])) for u in multipliers] + [(u[1],Unit(powerTen=u[2])) for u in multipliers] )

# LEXING:
#########

# Register all the MULTIPLIER regular expressions:
# [Programmatically, opposed to writing lines like:
# t_SHORT_GIGA  = r"""G"""
# t_LONG_GIGA  = r"""giga"""
# ]
for name, abbr, multiplier in multipliers:
    vName_short = 't_SHORT_%s'%name.upper()
    vName_long = 't_LONG_%s'%name.upper()
    globals()[vName_short] = r"%s"% abbr
    globals()[vName_long] = name


# Register all the UNIT regular expressions:
# [Programmatically, opposed to writing lines like:
# t_SHORT_VOLT = r"""V"""
# t_LONG_VOLT = r"""volt"""
# ]
for name, abbr, u_def in units:
    vName_short = 't_SHORT_%s'%name.upper()
    vName_long = 't_LONG_%s'%name.upper()
    globals()[vName_short] = abbr
    globals()[vName_long] = name


def t_error(t):
    raise UnitError( "Illegal character '%s'" % t.value[0])


lexer = ply.lex.lex()









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
                        | LONG_OHM
                        | LONG_COULOMB
                        | LONG_FARAD
                        | LONG_METER
                        | LONG_GRAM
                        | LONG_SECOND
                        | LONG_KELVIN
                        | LONG_MOLE
                        | LONG_CANDELA
                        """
    p[0] = unitDefs[ p[1] ]

def p_short_basic_unit(p):
    """short_basic_unit : SHORT_VOLT 
                        | SHORT_AMP 
                        | SHORT_SIEMEN
                        | SHORT_OHM
                        | SHORT_COULOMB
                        | SHORT_FARAD
                        | SHORT_METER
                        | SHORT_GRAM
                        | SHORT_SECOND
                        | SHORT_KELVIN
                        | SHORT_MOLE
                        | SHORT_CANDELA
                        """
    p[0] = unitDefs[ p[1]  ]


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
    p[0] = multiplierDefs[ p[1] ]
            

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
    p[0] = multiplierDefs[ p[1] ]

def p_error(p):
    raise UnitError( "Parsing Error " )















def parse_term( text ):
    text = text.strip()

    # CHECK FOR STANDARD DEFINITIONS:
    for u, u_def in special_unit_abbrs:
        if u == text:
            return u_def

    # Parse as per normal: 
    parser = ply.yacc.yacc(tabmodule='unit_term_parser_parsetab', outputdir='/tmp/')
    return parser.parse(text, lexer=lexer)


