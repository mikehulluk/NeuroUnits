
import ply.lex
from unit_errors import UnitError



class UnitExprLexer(object):
    tokens = [
        "INTEGER", 
        "FLOAT",
        "SLASH", 
        "SLASHSLASH",
        "WHITESPACE",
        "LBRACKET",
        "RBRACKET",
        "LCURLYBRACKET","RCURLYBRACKET",
        "ALPHATOKEN",
        "TIMES","PLUS","MINUSMINUS",
        "TILDE",
        "COMMA",
        "EQUALS",
        "EXCLAIMATION",
        "COLON",
        "NO_UNIT"
        ] 
    t_MINUSMINUS = r"""--"""

    def t_NO_UNIT(self, t):
        r"""NO_UNIT"""
        return t

    def t_FLOAT(self, t):
        r"""[-]?[0-9]+\.[0-9]*([eE][+-]?[0-9]+)?"""
        t.value = float(t.value)    
        return t

    def t_INTEGER(self, t):
        r"""[-]?[0-9]+"""
        t.value = int(t.value)    
        return t

    def t_ALPHATOKEN(self, t):
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

    # {xyz}  Builtin Constant 
    # {$xyz} Parameter/State
    # {@xyz} Parameter [for function call]
    # {~xyz} units

    def t_error(self, t):
        raise UnitError( "Illegal character '%s'" % t.value[0])

    
    def __init__(self):
        self.lexer = ply.lex.lex(module=self)
        
    def input(self, *args,**kwargs):
        return self.lexer.input(*args,**kwargs)
    
    def token(self, *args,**kwargs):
        return self.lexer.token(*args,**kwargs)
    
