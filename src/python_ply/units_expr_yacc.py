#import re
import ply.yacc as yacc
import units_expr_lexer
from units_expr_lexer import tokens
from units_core import Unit, UnitError, Quantity
#from units_core import UnitError, Quantity
#from units_core import Unit

def p_expr_0a(p): 
    """expr : WHITESPACE expr"""
    p[0] =p[2]

def p_expr_1(p): 
    """expr : expr PLUS term"""
    p[0] = p[1] + p[2]

def p_expr_2(p): 
    """expr : expr MINUS term"""
    p[0] = p[1] - p[2]
def p_expr_3(p): 
    """expr : term"""
    p[0] = p[1] 

def p_term_1(p):
    """term :  term times factor"""
    p[0] = p[1] * p[3]

def p_term_2(p):
    """term : term slash factor"""
    p[0] = p[1] / p[3]

def p_term_3(p):
    """term : factor"""
    p[0] = p[1] 

def p_factor_1(p):
    """factor : quantity_term """
    p[0] = p[1]
def p_factor_2(p):
    """factor : l_bracket expr r_bracket """
    p[0] = p[2]



# QUANTITY TERMS:
def p_quantity_term_0( p ):
    """quantity_term : FLOAT 
                     | INTEGER """
    p[0] = Quantity( p[1], Unit() )

def p_quantity_term_1( p ):
    """quantity_term : FLOAT unit_expr
                     | INTEGER unit_expr"""
    p[0] = Quantity( p[1], p[2] )

# QUANTITY TERMS:
def p_quantity_term_2( p ):
    """quantity_term : FLOAT WHITESPACE unit_expr
                     | INTEGER WHITESPACE unit_expr"""
    p[0] = Quantity( p[1], p[3] )


# USE TO CATCH A problem with parsing, we can't match terms like '3cm/2, 
# since the resolution of '/' needs to look ahead:
def p_quantity_term_3( p ):
    """quantity_term :    FLOAT unit_term_grp slash quantity_term
                        | INTEGER unit_term_grp slash quantity_term
    """
    p[0] = Quantity( p[1], p[2] ) / p[4]





# UNIT EXPRESSIONS:
def p_unit_expr_1( p ):
    """unit_expr : unit_term_grp"""
    p[0] = p[1]

def p_unit_expr_2( p ):
    """unit_expr : unit_term_grp slash unit_term_grp"""
    p[0] = p[1] / p[3]

def p_unit_expr_3( p ):
    """unit_expr : parameterised_unit_term slash parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_4( p ):
    """unit_expr : unit_term_grp slash parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_5( p ):
    """unit_expr : parameterised_unit_term slash unit_term_grp"""
    p[0] = p[1] / p[3]

def p_unit_expr_6( p ):
    """unit_expr : parameterised_unit_term"""
    p[0] = p[1]



#Parameterised Unit Term
#########################

def p_paramterised_unit_term_1( p ):
    """parameterised_unit_term : l_bracket unit_term_grp r_bracket"""
    p[0] = p[2]

def p_paramterised_unit_term_2( p ):
    """parameterised_unit_term : l_bracket unit_term_grp slash unit_term_grp r_bracket"""
    p[0] = p[2] / p[4]




# Unit term Group
#################

def p_unit_term_grp_1(p):
    """unit_term_grp : unit_term"""
    p[0] = p[1]

def p_unit_term_grp_2(p):
    """unit_term_grp : unit_term_grp WHITESPACE unit_term"""
    p[0] = p[1] * p[3]




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
    """unit_term_unpowered : ALPHATOKEN
    """
    from units_term_parsing import parse_term
    p[0] = parse_term( p[1] )



def p_lbracket_clean(p):
    """ l_bracket :    LBRACKET
                     | LBRACKET WHITESPACE 
                     """
    pass

def p_rbracket_clean(p):
    """ r_bracket :    RBRACKET
                     | RBRACKET WHITESPACE 
    """
    pass

def p_times_clean(p):
    """ times :    TIMES
                 | TIMES WHITESPACE 
    """
    pass

def p_slash_clean(p):
    """ slash :    SLASH
                 | SLASH WHITESPACE 
    """
    pass



def p_error(p):
    raise UnitError( "Parsing Error %s" % (p) )
    
precedence = (
    ('left', 'TIMES', 'SLASH'),
    ('left', 'PLUS','MINUS'),
    ('left', 'WHITESPACE'),
)


def parse_expr(text):
    import logging
    logging.basicConfig(
        level = logging.DEBUG,
        filename = "parselog.txt",
        filemode = "w",
        format = "%(filename)10s:%(lineno)4d:%(message)s"
    )
    log = logging.getLogger()

    parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True  ) 
    return parser.parse(text, lexer=units_expr_lexer.lexer, debug=True, )

    parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True ) 
    return parser.parse(text, lexer=units_expr_lexer.lexer)


