#import re
import ply.yacc as yacc
import units_expr_lexer
from units_expr_lexer import tokens
#from units_core import Unit, UnitError, Quantity
from units_core import UnitError, Quantity



def p_gen_expr( p ):
    """gen_expr : unit_expr
                | quantity_expr
    """
    p[0] = p[1]



# QUANTITY EXPRESSIONS:
def p_quantity_expr_1(p):
    r"""quantity_expr : quantity_term
                      | quantity_term_parethesised
    """
    p[0] = p[1]

def p_quantity_expr_2(p):
    r"""quantity_expr : quantity_term_parethesised SLASH quantity_term_parethesised
    """
    p[0] = p[1] / p[3]


def p_quantity_term_parathesised( p ):
    """quantity_term_parethesised :  LBRACKET quantity_term RBRACKET
                                   | LBRACKET quantity_term_parethesised RBRACKET
    """
    p[0] = p[2]




# QUANTITY TERMS:
def p_quantity_term_1( p ):
    """quantity_term : FLOAT unit_expr
                     | INTEGER unit_expr"""
    p[0] = Quantity( p[1], p[2] )

# QUANTITY TERMS:
def p_quantity_term_2( p ):
    """quantity_term : FLOAT WHITESPACE unit_expr
                     | INTEGER WHITESPACE unit_expr"""
    p[0] = Quantity( p[1], p[3] )


# UNIT EXPRESSIONS:
def p_unit_expr_1( p ):
    """unit_expr : unit_term_grp"""
    p[0] = p[1]

def p_unit_expr_2( p ):
    """unit_expr : unit_term_grp SLASH unit_term_grp"""
    p[0] = p[1] / p[3]


def p_unit_expr_3( p ):
    """unit_expr : parameterised_unit_term SLASH parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_4( p ):
    """unit_expr : unit_term_grp SLASH parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_5( p ):
    """unit_expr : parameterised_unit_term SLASH unit_term_grp"""
    p[0] = p[1] / p[3]

def p_unit_expr_6( p ):
    """unit_expr : parameterised_unit_term"""
    p[0] = p[1]

def p_unit_expr_7( p ):
    """unit_expr : unit_term_grp SLASH WHITESPACE unit_term_grp"""
    p[0] = p[1] / p[4]


#Parameterised Unit Term
#########################

def p_paramterised_unit_term_1( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp RBRACKET"""
    p[0] = p[2]

def p_paramterised_unit_term_2( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp SLASH unit_term_grp RBRACKET"""
    p[0] = p[2] / p[4]


# [Allow additional trailing whitespace]:
def p_paramterised_unit_term_4( p ):
    """parameterised_unit_term : parameterised_unit_term WHITESPACE """
    p[0] = p[1] 


# Unit term Group
#################

def p_unit_term_grp_1(p):
    """unit_term_grp : unit_term"""
    p[0] = p[1]

def p_unit_term_grp_2(p):
    """unit_term_grp : unit_term_grp WHITESPACE unit_term"""
    p[0] = p[1] * p[3]

# [Allow additional trailing whitespace]:
def p_unit_term_grp_3(p):
    """unit_term_grp : unit_term_grp WHITESPACE """
    p[0] = p[1] 



# Unit_terms:
##############

def p_unit_term_1(p):
    """unit_term : unit_term_unpowered"""
    p[0] = p[1]

def p_unit_term_2(p):
    """unit_term : unit_term_unpowered INTEGER"""
    p[0] = p[1].raise_to_power( int(p[2]) )



# Unpowered unit terms:
########################
def p_unit_term_unpowered_token(p):
    """unit_term_unpowered :    ALPHATOKEN
    """
    #from units_core import Unit
    #return Unit()
    from units_term_parsing import parse_term
    p[0] = parse_term( p[1] )


def p_error(p):
    raise UnitError( "Parsing Error %s" % (p) )
    



def parse_expr(text):
    #import logging
    #logging.basicConfig(
    #    level = logging.DEBUG,
    #    filename = "parselog.txt",
    #    filemode = "w",
    #    format = "%(filename)10s:%(lineno)4d:%(message)s"
    #)
    #log = logging.getLogger()

    #parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True, debuglog=log ) 
    #return parser.parse(text, lexer=units_expr_lexer.lexer, debug=True, )

    parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True ) 
    return parser.parse(text, lexer=units_expr_lexer.lexer)


