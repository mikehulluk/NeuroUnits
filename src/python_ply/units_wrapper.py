
import units_expr_yacc
def ParseUnitString(text, debug=False):
    return units_expr_yacc.parse_expr(text, start_symbol='unit_expr' )

import units_expr_yacc
def ParseExprString(text, debug=False):
    return units_expr_yacc.parse_expr(text, start_symbol='quantity_def' )
