
from units_wrapper import ParseUnitString,ParseExprString
from units_core import UnitError
import re

def iterate_valid_lines(filename):
    f = open(filename)
    for line in f.readlines():
        line = re.sub('#.*','',line.strip())
        if not line:
            continue
        yield line
    f.close()



def test_valid_units():
    print 'Testing Valid Units'
    for line in iterate_valid_lines("../testing/valid_units.txt"):
        result = ParseUnitString(line)
        print line.ljust(30), '->', result

    print

def test_valid_exprs():
    print 'Testing Valid Expressions'
    for line in iterate_valid_lines("../testing/valid_expressions.txt"):
        #print "LINE:",line
        #print
        result = ParseExprString(line)
        print line.ljust(30), '->', result



# Make the default parser, otherwise ply has a whinge
import units_expr_yacc
units_expr_yacc.parse_expr("mV", start_symbol='parse_line', debug=True )


test_valid_units()
test_valid_exprs()

