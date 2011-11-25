
import units_expr_yacc
def ParseUnitString(text):
    return units_expr_yacc.parse_expr(text)

