
#import sys
#sys.path.append("../python_ply/")

#from neurounits.units_wrapper import ParseUnitString,ParseExprString
from neurounits import NeuroUnitParser
import re

def iterate_valid_lines(filename):
    with open(filename) as f:
        for line in f.readlines():
            line = re.sub('#.*','',line.strip())
            if line:
                yield line



def test_valid_units():
    print 'Testing Valid Units'
    for line in iterate_valid_lines("../test_data/validunits.txt"):
        result = NeuroUnitParser.Unit(line)
        print line.ljust(30), '->', result

    print

def test_valid_exprs():
    print 'Testing Valid Expressions'
    for line in iterate_valid_lines("../test_data/validexpressions.txt"):
        result = NeuroUnitParser.Expr(line)
        print line.ljust(30), '->', result



# Make the default parser, otherwise ply has a whinge
#from neurounits import units_expr_yacc
#units_expr_yacc.parse_expr("mV", start_symbol='parse_line', debug=True )


test_valid_units()
test_valid_exprs()

