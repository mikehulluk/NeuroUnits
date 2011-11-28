import ply.yacc as yacc
import units_expr_lexer
from units_expr_lexer import tokens
from units_core import Unit, UnitError, Quantity
import re
from units_data import unit_long_LUT, std_func_LUT
from units_data import std_funcs

from units_data import constants

def p_parse_line(p):
    """parse_line : unit_expr 
                  | function_def 
                  | quantity_def
                  """
    p[0] = p[1]


def p_quantity_def1(p):
    """quantity_def : quantity_expr 
                    | quantity_expr COLON unit_expr"""
    if len(p) == 4:
        p[1] = p[1].converted_to_unit( p[3] )
    
    p[0] = p[1]



#LHS FUNCTION CALL DEFINITIONS
def p_function_definition(p):
    """function_def : ALPHATOKEN LBRACKET function_params RBRACKET EQUALS quantity_expr"""
    pass
def p_function_def_params(p):
    """function_params : ALPHATOKEN
                       | function_params COMMA ALPHATOKEN"""
    pass



# FUNCTION CALL DEFINITIONS INSIDE EXPRESSIONS:
def p_quantity_func_call_1(p):
    """quantity_factor :  ALPHATOKEN LBRACKET func_call_params RBRACKET """ 
    
    # We can't handle, multiple arguments yet:
    if not len(p[3])==1:
        p[0] = Quantity( -1.0, Unit() )
        return

    # Single argument case:
    functor = std_func_LUT[p[1]]
    p[0] = functor( p[3][0] ) 

def p_quantity_func_params1(p):
    """func_call_params : quantity_expr
                        | func_call_param 
                        | func_call_params COMMA func_call_param"""
    if len(p) == 2:
        p[0] = [p[1],]
    else:
        p[0] = p[1] + [ p[3] ]
        

def p_quantity_func_params_term(p):
    """func_call_param : ALPHATOKEN EQUALS quantity_expr"""
    return p[3]



def p_quantity_expr_1(p): 
    """quantity_expr : quantity_expr PLUS quantity_term"""
    #print p[1], p[2]
    p[0] = p[1] + p[3]

def p_quantity_expr_2(p): 
    """quantity_expr : quantity_expr MINUSMINUS quantity_term"""
    p[0] = p[1] - p[3]
def p_quantity_expr_3(p): 
    """quantity_expr : quantity_term"""
    p[0] = p[1] 

def p_quantity_term_1(p):
    """quantity_term :  quantity_term TIMES quantity_factor"""
    p[0] = p[1] * p[3]

def p_quantity_term_2(p):
    """quantity_term : quantity_term SLASH quantity_factor"""
    p[0] = p[1] / p[3]

def p_quantity_term_3(p):
    """quantity_term : quantity_factor"""
    p[0] = p[1] 

def p_quantity_factor_1(p):
    """quantity_factor : quantity """
    p[0] = p[1]
def p_quantity_factor_2(p):
    """quantity_factor : LBRACKET quantity_expr RBRACKET """
    p[0] = p[2]



# QUANTITY TERMS:
def p_quantity_0( p ):
    """quantity : magnitude"""
    p[0] = Quantity( p[1], Unit() )

def p_quantity_1( p ):
    """quantity : magnitude unit_expr """
    p[0] = Quantity( p[1], p[2] )

def p_quantity_2( p ):
    """quantity : magnitude WHITESPACE unit_expr"""
    p[0] = Quantity( p[1], p[3] )

def p_quantity_magnitude(p):
    """magnitude : FLOAT 
                 | INTEGER"""
    p[0] = p[1]


def p_quantity_constant(p):
    """ quantity : LCURLYBRACKET constant RCURLYBRACKET """
    p[0] = p[2]

def p_quantity_constant_2(p):
    """ constant : ALPHATOKEN """
    p[0] = constants[ p[1] ]


# UNIT EXPRESSIONS:
def p_unit_expr_1( p ):
    """unit_expr : unit_term_grp"""
    p[0] = p[1]

def p_unit_expr_2( p ):
    """unit_expr : unit_term_grp SLASHSLASH unit_term_grp"""
    p[0] = p[1] / p[3]

def p_unit_expr_3( p ):
    """unit_expr : parameterised_unit_term SLASHSLASH parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_4( p ):
    """unit_expr : unit_term_grp SLASHSLASH parameterised_unit_term"""
    p[0] = p[1] / p[3]

def p_unit_expr_5( p ):
    """unit_expr : parameterised_unit_term SLASHSLASH unit_term_grp"""
    p[0] = p[1] / p[3]

def p_unit_expr_6( p ):
    """unit_expr : parameterised_unit_term"""
    p[0] = p[1]



#Parameterised Unit Term
#########################

def p_paramterised_unit_term_1( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp RBRACKET"""
    p[0] = p[2]

def p_paramterised_unit_term_2( p ):
    """parameterised_unit_term : LBRACKET unit_term_grp SLASHSLASH unit_term_grp RBRACKET"""
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


def p_unit_term_3(p):
    """ unit_term : LCURLYBRACKET TILDE ALPHATOKEN RCURLYBRACKET """
    if p[3] in unit_long_LUT:
        p[0] = unit_long_LUT[p [3] ]
        return
    assert False

# Unpowered unit terms:
########################
def p_unit_term_unpowered_token(p):
    """unit_term_unpowered : ALPHATOKEN
    """
    from units_term_parsing import parse_term
    p[0] = parse_term( p[1] )





def p_error(p):
    raise UnitError( "Parsing Error %s" % (p) )
    
precedence = (
    ('left', 'SLASHSLASH'),
    ('left', 'TIMES', 'SLASH'),
    ('left', 'PLUS','MINUSMINUS'),
    ('left', 'WHITESPACE'),
)



def parse_expr(text, start_symbol, debug=False):

    # Some preprocessing:
    #######################
    
    assert text.find('--') == -1

    # Strip all unnessesary whitespace:
    s1 = re.compile(r'[ ]* ([()/*:+]) [ ]*',re.VERBOSE)
    text = re.sub(s1,r'\1',text)

    # '/' plays 2 roles. To simplify the grammar, turn '/' used to 
    # purely separate unit terms to '//'
    # Look for a '('* then either [a-zA-Z] or '~{' following the slash:
    s = re.compile(r"""/(?= [(]* (?:[a-zA-Z]) )""", re.VERBOSE)
    text = re.sub(s,'//',text)
    s = re.compile(r"""/(?= [(]* (?:{~) )""", re.VERBOSE)
    text = re.sub(s,'//',text)

    # Likewise, '-' plays 2 roles, as negative exponent as
    # as subtraction. Lets remap subtraction to '--', unless its followed
    # by a digit, in which case its part of that digit
    s = re.compile(r"""[ ]* [-](?=[^0-9]) [ ]*""", re.VERBOSE)
    text = re.sub(s,'--',text)


    #Remap function calls:
    for fncName, fncAliases, functor in std_funcs:
        for alias in fncAliases:
            r = re.compile(r"""\b %s [ ]* (?=[(])"""%alias, re.VERBOSE)
            text = re.sub(r, fncName, text)

    
    if debug:

        #import logging
        #logging.basicConfig(
        #    level = logging.DEBUG,
        #    filename = "parselog.txt",
        #    filemode = "w",
        #    format = "%(filename)10s:%(lineno)4d:%(message)s"
        #)
        #log = logging.getLogger()

        parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True,start=start_symbol   ) 
        return parser.parse(text, lexer=units_expr_lexer.lexer, debug=True, )
    else:
        parser = yacc.yacc(tabmodule='unit_expr_parser_parsetab', debug=True, start=start_symbol  ) 
        return parser.parse(text, lexer=units_expr_lexer.lexer,)


