
import ply.lex
from units_core import UnitError

tokens = [
    "INTEGER", "FLOAT",
    "SLASH", 
    "WHITESPACE", "EOL",
    "LBRACKET","RBRACKET",
    "ALPHATOKEN",
    "TIMES","PLUS","MINUS"
        ] 

def t_FLOAT(t):
    #r"""[0-9]+\.[0-9]?\([eE][+-]?[0-9]+\)?"""
    r"""[0-9]+\.[0-9]?"""
    t.value = float(t.value)    
    return t

def t_INTEGER(t):
    r"""[+-]?[0-9]+"""
    t.value = int(t.value)    
    return t

t_ALPHATOKEN = r"""[a-zA-Z]+"""
t_SLASH = r"""/"""
t_WHITESPACE = r"""[ \t]+"""
t_EOL = r"""\n"""
t_LBRACKET = r"""\("""
t_RBRACKET = r"""\)"""

t_TIMES = r"""\*"""
t_PLUS = r"""\+"""
t_MINUS = r"""\*"""


def t_error(t):
    raise UnitError( "Illegal character '%s'" % t.value[0])


lexer = ply.lex.lex()
