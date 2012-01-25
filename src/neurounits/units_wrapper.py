
import units_expr_yacc

class NeuroUnitParser(object):

    @classmethod
    def Unit(cls, text, debug=False):    
        return units_expr_yacc.parse_expr(text, start_symbol='unit_expr' )
        
    @classmethod
    def Expr(cls, text, debug=False):    
        return units_expr_yacc.parse_expr(text, start_symbol='quantity_def' )
