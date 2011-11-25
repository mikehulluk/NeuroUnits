#import re
import ply.yacc as yacc
import units_expr_lexer
from units_expr_lexer import tokens
from units_core import Unit, UnitError, Quantity



def p_gen_expr( p ):
    """gen_expr : unit_expr
                | quantity_expr
    """
    p[0] = p[1]



def p_quantity_expr_1(p):
    """quantity_expr : quantity_term"""
    p[0] = p[1]

def p_quantity_expr_2(p):
    """quantity_expr : quantity_term SLASH quantity_term"""
    p[0] = p[1] / p[3]


# QUANTITY EXPRESSIONS:
def p_quantity_term_1( p ):
    """quantity_term : FLOAT unit_expr
                     | INTEGER unit_expr"""
    p[0] = Quantity( p[1], p[2] )



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


#Parameterised Unit Term
#########################

def p_paramterised_unit_term_1( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp RBRACKET"""
    p[0] = p[2]

def p_paramterised_unit_term_2( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp SLASH unit_term_grp RBRACKET"""
    p[0] = p[2] / p[4]

# [Allow additional whitespace]:
def p_paramterised_unit_term_3( p ):
    """parameterised_unit_term : WHITESPACE parameterised_unit_term"""
    p[0] = p[2] 

# [Allow additional whitespace]:
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

# [Allow additional whitespace]:
def p_unit_term_grp_3(p):
    """unit_term_grp : unit_term_grp WHITESPACE """
    p[0] = p[1] 

def p_unit_term_grp_4(p):
    """unit_term_grp : WHITESPACE unit_term_grp """
    p[0] = p[2] 


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
    from units_term_parsing import parse_term
    p[0] = parse_term( p[1] )


def p_error(p):
    raise UnitError( "Parsing Error %s" % (p) )
    #raise UnitError( "Parsing Error %s('%s')" % (p,p.value[0]))
    



def parse_expr(text):
    parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab')
    return parser.parse(text, lexer=units_expr_lexer.lexer)


