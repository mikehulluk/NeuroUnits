
import ply.lex
from units_core import UnitError

tokens = [
    "INTEGER", "FLOAT",
    "SLASH", "SLASHSLASH",
    "WHITESPACE",
    "LBRACKET","RBRACKET",
    "LCURLYBRACKET","RCURLYBRACKET",
    "ALPHATOKEN",
    "TIMES","PLUS","MINUSMINUS",
    "TILDE",
    "COMMA",
    "EQUALS",
    "EXCLAIMATION",
    "COLON",
    ] 
t_MINUSMINUS = r"""--"""

def t_FLOAT(t):
    r"""[-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?"""
    t.value = float(t.value)    
    return t

def t_INTEGER(t):
    r"""[-]?[0-9]+"""
    t.value = int(t.value)    
    return t

def t_ALPHATOKEN(t):
    r"""[a-zA-Z_]+"""
    return t



t_SLASHSLASH = r"""//"""
t_SLASH = r"""/"""
t_WHITESPACE = r"""[ \t]+"""
t_LBRACKET = r"""\("""
t_RBRACKET = r"""\)"""
t_LCURLYBRACKET = r"""\{"""
t_RCURLYBRACKET = r"""\}"""

t_EXCLAIMATION = r"""!"""
t_TILDE = r"""~"""
t_TIMES = r"""\*"""
t_PLUS = r"""\+"""

t_COMMA = r""","""
t_COLON = r""":"""
t_EQUALS = r"""="""

# {xyz}  Builtin Constant or Parameter
# {@xyz} Parameter [for function call]
# {~xyz} units
# {!xyz} function_call

def t_error(t):
    raise UnitError( "Illegal character '%s'" % t.value[0])


lexer = ply.lex.lex()
