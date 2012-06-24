#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------



import re
import ply.yacc as yacc
import ply


import units_expr_lexer
from neurounits.unit_errors import UnitError
from units_expr_lexer import UnitExprLexer
from neurounits.units_misc import  safe_dict_merge, EnsureExisits
from morphforge.core.misc import SeqUtils
from neurounits.librarymanager import LibraryManager

import neurounits.ast as ast


from neurounits.units_data_unitterms import UnitTermData





tokens = UnitExprLexer.tokens




def p_empty(p):
    """empty :"""
    pass


def p_whitespace_slurp2(p):
    """whiteslurp : empty
                  | WHITESPACE"""
    pass


def p_whitespace_slurp3(p):
    """white_or_newline_slurp : empty
                             | WHITESPACE
                             | NEWLINE
                             | white_or_newline_slurp WHITESPACE
                             | white_or_newline_slurp NEWLINE
                             """
    pass














def p_file_def1(p):
    """text_block : white_or_newline_slurp
                  | text_block block_type"""
    pass



def p_file_def2(p):
    """ block_type : eqnset_def
                   | library_def"""
    pass









def p_open_new_eqnset(p):
    """ open_eqnset : empty """
    p.parser.library_manager.start_eqnset_block()

def p_close_new_eqnset(p):
    """eqnset_def : eqnset_def_internal"""
    p.parser.library_manager.end_eqnset_block()

def p_eqnset_def1(p):
    """eqnset_def_internal : EQNSET open_eqnset WHITESPACE namespace LCURLYBRACKET eqnsetcontents white_or_newline_slurp RCURLYBRACKET white_or_newline_slurp SEMICOLON white_or_newline_slurp"""
    p.parser.library_manager.get_current_block_builder().set_name(p[4])

def p_complete_eqnset_line(p):
    """complete_eqnset_line : white_or_newline_slurp eqnsetlinecontents white_or_newline_slurp SEMICOLON """

def p_parse_eqnsetline1(p):
    """eqnsetcontents : white_or_newline_slurp
                      | complete_eqnset_line
                      | eqnsetcontents complete_eqnset_line """
    pass

def p_parse_eqnsetline2(p):
    """eqnsetlinecontents : IO_LINE"""
    p.parser.library_manager.get_current_block_builder().add_io_data(p[1])

def p_parse_eqnsetline2b(p):
    """eqnsetlinecontents   : ONEVENT_SYMBOL WHITESPACE event_def """
    pass

def p_parse_eqnsetline4(p):
    """eqnsetlinecontents   : import
                            | function_def
                            | assignment
                            | time_derivative """
    pass






# LIBRARY DEFINITIONS:
# ##########################

def p_open_new_library(p):
    """ open_library : empty """
    p.parser.library_manager.start_library_block()

def p_close_new_library(p):
    """library_def : library_def_internal"""
    p.parser.library_manager.end_library_block()

def p_library_def1(p):
    """library_def_internal : LIBRARY open_library WHITESPACE namespace LCURLYBRACKET librarycontents white_or_newline_slurp RCURLYBRACKET white_or_newline_slurp SEMICOLON white_or_newline_slurp"""
    p.parser.library_manager.get_current_block_builder().set_name(p[4])

def p_complete_library_line(p):
    """complete_library_line : white_or_newline_slurp librarylinecontents white_or_newline_slurp SEMICOLON """

def p_parse_libraryline1(p):
    """librarycontents : white_or_newline_slurp
                      | complete_library_line
                      | librarycontents complete_library_line """
    pass


def p_parse_libraryline4(p):
    """librarylinecontents  : import
                            | function_def
                            | assignment """
    pass




























def p_on_event_open_scope(p):
    """ open_event_def_scope : empty"""
    p.parser.library_manager.get_current_block_builder().open_event_def_scope()

def p_on_event_definition(p):
    """event_def : alphanumtoken LBRACKET function_def_params RBRACKET white_or_newline_slurp LCURLYBRACKET open_event_def_scope on_event_actions_blk RCURLYBRACKET """
    e = ast.OnEvent(name = p[1], parameters=p[3], actions=p[8] )
    p.parser.library_manager.get_current_block_builder().close_scope_and_create_onevent(e)

def p_on_event_actionsblk(p):
    """on_event_actions_blk : white_or_newline_slurp on_event_actions"""
    p[0] = p[2]



def p_on_event_actions1(p):
    """on_event_actions : empty"""
    p[0] = []
def p_on_event_actions2(p):
    """on_event_actions :  on_event_action"""
    p[0] = [p[1]]
def p_on_event_actions3(p):
    """on_event_actions :  on_event_actions on_event_action"""
    p[0] = p[1] + [p[2]]


def p_on_event_action0(p):
    """on_event_action : empty NEWLINE"""
    p[0] = None

def p_on_event_action1(p):
    """on_event_action : alphanumtoken  EQUALS rhs_term whiteslurp SEMICOLON"""
    lhs = p.parser.library_manager.get_current_block_builder().get_symbol_or_proxy(p[1])
    p[0] = ast.OnEventStateAssignment(lhs=lhs,rhs=p[3])


# Importing:
def p_import_statement1(p):
    """import : FROM WHITESPACE namespace WHITESPACE IMPORT WHITESPACE import_target_list"""
    p.parser.library_manager.get_current_block_builder().do_import(srclibrary = p[3], tokens=[(t,None) for t in  p[7] ])

def p_import_statement2(p):
    """import : FROM WHITESPACE namespace WHITESPACE IMPORT WHITESPACE localsymbol WHITESPACE AS WHITESPACE  localsymbol"""
    p.parser.library_manager.get_current_block_builder().do_import(srclibrary = p[3], tokens=[(p[7],p[11])] )



def p_import_target_list1(p):
    """import_target_list : localsymbol whiteslurp"""
    p[0] = [p[1]]

def p_import_target_list2(p):
    """import_target_list : import_target_list COMMA whiteslurp localsymbol whiteslurp"""
    p[0] = p[1] + [p[4]]







def p_assignment(p):
    """assignment : lhs_symbol EQUALS rhs_generic"""
    p.parser.library_manager.get_current_block_builder().add_assignment(
           lhs_name = p[1],
           rhs_ast = p[3] )

def p_time_derivative(p):
    """time_derivative : lhs_symbol PRIME EQUALS rhs_generic"""
    p.parser.library_manager.get_current_block_builder().add_timederivative(
           lhs_state_name = p[1],
           rhs_ast = p[4] )



# Symbol definitons:
# #################
def p_namespace(p):
    """namespace : alphanumtoken """
    p[0] = p[1]
def p_namespace2(p):
    """namespace : namespace DOT alphanumtoken"""
    p[0] = "%s.%s"%(p[1],p[3])

def p_localsymbol(p):
    """localsymbol : alphanumtoken """
    p[0] = p[1]

def p_externalsymbol(p):
    """externalsymbol : namespace DOT localsymbol """
    p[0] = "%s.%s"%(p[1],p[3])


def p_rhs_symbol(p):
    """rhs_symbol : localsymbol
                   | externalsymbol """
    p[0] = p[1]

def p_lhs_symbol(p):
    """lhs_symbol : localsymbol"""

    p[0] = p[1]





# Function definition:
########################
# Scope Control:
def p_function_definition_scope_open(p):
    """open_funcdef_scope : """
    p.parser.library_manager.get_current_block_builder().open_function_def_scope()

def p_function_definition(p):
    """function_def : lhs_symbol LBRACKET function_def_params RBRACKET EQUALS open_funcdef_scope rhs_generic """
    f = ast.FunctionDef( funcname=p[1], parameters=p[3], rhs=p[7] )
    p.parser.library_manager.get_current_block_builder().close_scope_and_create_function_def(f)
    p[0] = None

def p_function_def_param(p):
    """function_def_param : localsymbol
                          | localsymbol COLON unit_expr"""
    dimension = None if len(p) == 2 else p[3]
    #assert not dimension
    p[0] = {p[1]:ast.FunctionDefParameter(symbol=p[1], dimension=dimension) }


def p_function_def_params0(p):
    """function_def_params : whiteslurp"""
    p[0] = {}


def p_function_def_params1(p):
    """function_def_params : function_def_param whiteslurp"""
    p[0] = p[1]

def p_function_def_params2(p):
    """function_def_params : function_def_params COMMA whiteslurp function_def_param whiteslurp"""
    p[0] = safe_dict_merge( p[1], p[4] )




# Function calls:
###################
def p_quantity_func_call_l3(p):
    """rhs_term :  function_call_l3 """
    p[0] = p[1]

def p_quantity_func_call_l3_1(p):
    """function_call_l3 :  rhs_symbol LBRACKET func_call_params_l3 RBRACKET """
    p[0] = p.parser.library_manager.get_current_block_builder().create_function_call( p[1], p[3] )


# For function parameters, we create a dictionary mapping parameter name to value
def p_quantity_func_params_l3a(p):
    """func_call_params_l3 : rhs_term"""
    p[0] = { None: ast.FunctionDefParameterInstantiation( symbol = None, rhs_ast=p[1] ) }

def p_quantity_func_params_l3b(p):
    """func_call_params_l3 : func_call_param_l3"""
    p[0] = {p[1].symbol:p[1]}

def p_quantity_func_params_l3c(p):
    """func_call_params_l3 : func_call_params_l3 COMMA func_call_param_l3"""
    param_dict = p[1]
    new_param = p[3]
    assert not new_param.symbol in param_dict
    param_dict[new_param.symbol] = new_param
    p[0] = param_dict

def p_quantity_func_params_term_l3(p):
    """func_call_param_l3 : alphanumtoken EQUALS rhs_term"""
    p[0] = ast.FunctionDefParameterInstantiation( symbol = p[1], rhs_ast=p[3] )





def p_rhs_term4(p):
    """ rhs_term : MINUSMINUS rhs_term """
    backend = p.parser.library_manager.backend
    neg_one = ast.ConstValue( backend.Quantity( -1.0, backend.Unit() ) )
    p[0] = ast.MulOp(neg_one, p[2] )




def p_lhs(p):
    """rhs_generic : rhs_term"""
    p[0] = p[1]


def p_bool_term_a(p):
    """bool_term : rhs_term LESSTHAN rhs_term"""
    p[0] = ast.InEquality(  less_than = p[1],
                            greater_than = p[3] )
def p_bool_term_b(p):
    """bool_term : rhs_term GREATERTHAN rhs_term"""
    p[0] = ast.InEquality(  less_than = p[3],
                            greater_than = p[1] )

def p_bool_term1(p):
    """bool_term : bool_term AND bool_term"""
    p[0] = ast.BoolAnd(  lhs = p[1], rhs = p[3] )
def p_bool_term2(p):
    """bool_term : bool_term OR bool_term"""
    p[0] = ast.BoolOr(  lhs = p[1], rhs = p[3] )
def p_bool_term3(p):
    """bool_term : NOT bool_term"""
    p[0] = ast.BoolNot(  lhs = p[2] )

def p_bool_term4(p):
    """bool_term : LBRACKET bool_term RBRACKET"""
    p[0] = p[2]


def p_rhs_term_conditional(p):
    """rhs_term : LSQUAREBRACKET rhs_generic RSQUAREBRACKET IF LSQUAREBRACKET bool_term RSQUAREBRACKET ELSE LSQUAREBRACKET rhs_generic RSQUAREBRACKET"""
    p[0] = ast.IfThenElse(  predicate=p[6],
                        if_true_ast=p[2],
                        if_false_ast=p[10])

def p_rhs_term_params(p):
    """rhs_term : LBRACKET rhs_term RBRACKET"""
    p[0] = p[2]

def p_rhs_term_add(p):
    """rhs_term : rhs_term PLUS rhs_term"""
    p[0] = ast.AddOp( p[1], p[3] )

def p_rhs_term_sub(p):
    """rhs_term : rhs_term MINUSMINUS rhs_term"""
    p[0] = ast.SubOp( p[1], p[3] )

def p_rhs_term_mul(p):
    """rhs_term : rhs_term TIMES rhs_term"""
    p[0] = ast.MulOp( p[1], p[3] )

def p_rhs_term_exp(p):
    """rhs_term : rhs_term TIMESTIMES INTEGER"""
    p[0] = ast.ExpOp( p[1], p[3] )

def p_rhs_term_div(p):
    """rhs_term : rhs_term SLASH rhs_term"""
    p[0] = ast.DivOp( p[1], p[3] )












def p_rhs_term1(p):
    """ rhs_term : rhs_variable
                 | rhs_quantity_expr """
    p[0] = p[1]

def p_rhs_term2(p):
    """ rhs_term : quantity """
    p[0] = ast.ConstValue( p[1] )

def p_lhs_variable(p):
    """ rhs_variable : rhs_symbol"""
    p[0] = p.parser.library_manager.get_current_block_builder().get_symbol_or_proxy(p[1])

def p_lhs_unit_expr(p):
    """ rhs_quantity_expr : LCURLYBRACKET quantity RCURLYBRACKET"""
    p[0] = ast.ConstValue( p[2] )




# Alphanumeric tokes:
def p_lhs_variable_name1(p):
    """alphanumtoken : ALPHATOKEN"""
    p[0] = p[1]
def p_lhs_variable_name2(p):
    """alphanumtoken : alphanumtoken ALPHATOKEN"""
    p[0] = p[1] + p[2]
def p_lhs_variable_name3(p):
    """alphanumtoken : alphanumtoken INTEGER"""
    p[0] = p[1] + str(p[2])









# Quantity Expressions:
##########################
def p_quantity_expr_1(p):
    """quantity_expr : quantity_expr PLUS quantity_term"""
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


def p_quantity_nounits(p):
    """ quantity : NO_UNIT LCURLYBRACKET quantity_expr COLON unit_expr RCURLYBRACKET """
    p[0] = p[3]
    print 'ERROR, not implemented yet'







# QUANTITY TERMS:
# ###############
def p_quantity_0( p ):
    """quantity : magnitude"""
    backend = p.parser.library_manager.backend
    p[0] = backend.Quantity( p[1], backend.Unit() )

def p_quantity_1( p ):
    """quantity : magnitude unit_expr """
    backend = p.parser.library_manager.backend
    p[0] = backend.Quantity( p[1], p[2] )

def p_quantity_2( p ):
    """quantity : magnitude WHITESPACE unit_expr"""
    backend = p.parser.library_manager.backend
    p[0] = backend.Quantity( p[1], p[3] )


def p_quantity_magnitude(p):
    """magnitude : FLOAT
                 | INTEGER"""
    p[0] = float(p[1])




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

# Allow empty unit
def p_unit_expr_7( p ):
    """unit_expr : LBRACKET RBRACKET"""
    backend = p.parser.library_manager.backend
    p[0] = backend.Unit()


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
    p[0] = p[1] ** ( int(p[2]) )


def p_unit_term_3(p):
    """ unit_term_unpowered : LCURLYBRACKET TILDE ALPHATOKEN RCURLYBRACKET """

    backend = p.parser.library_manager.backend
    unit_long_LUT = UnitTermData.getUnitLUTLong(backend=backend)

    if p[3] in unit_long_LUT:
        p[0] = unit_long_LUT[p [3] ]
    else:
        #print p[3]
        assert False

# Unpowered unit terms:
########################
def p_unit_term_unpowered_token(p):
    """unit_term_unpowered : ALPHATOKEN """
    import neurounits.unit_term_parsing as unit_term_parsing
    p[0] = unit_term_parsing.parse_term( p[1], backend=p.parser.library_manager.backend )





def p_error(p):


    if p is None:
        raise NeuroUnitParsingError("Unexpected end of file encountered")
    else:
        pass
    try:
        line = p.lexer.lexer.lexdata.split("\n")[p.lexer.lexer.lineno]

        o = p.lexer.lexer.lexpos
        line1 = p.lexer.lexer.lexdata[o-10: o+10]
        line2 = p.lexer.lexer.lexdata[o-3: o+3]

        print 'Offending Line:', line1
        print 'Offending Line:', line2
    except:
        pass
    raise UnitError( "Parsing Error %s" % (p) )

precedence = (


    ('left', 'WHITESPACE'),
    ('left', 'PLUS','MINUSMINUS'),

    ('left', 'TIMES', 'SLASH'),
    ('left', 'TIMESTIMES'),
    ('left', 'SLASHSLASH'),

    ('right', 'NOT'),
    ('left', 'AND'),
    ('left', 'OR'),
)











class ParseTypes(object):
    L1_Unit = "L1_Unit"
    L2_QuantitySimple = "L2_QuantitySimple"
    L3_QuantityExpr = "L3_QuantityExpr"
    L4_EqnSet = "L4_EqnSet"
    L5_Library = "L5_Library"
    L6_TextBlock = "L6_TextBlock"


class ParseDetails(object):
    start_symbols = {
        ParseTypes.L1_Unit :            'unit_expr',
        ParseTypes.L2_QuantitySimple :  'quantity_expr',
        ParseTypes.L3_QuantityExpr :    'rhs_generic',
        ParseTypes.L4_EqnSet :          'eqnset',
        ParseTypes.L5_Library :         "library_set",
        ParseTypes.L6_TextBlock :       'text_block',
            }



from collections import namedtuple
RE = namedtuple('RE', ["frm","to"])


regexes_slashes = {
        "SlashAlpha_To_DoubleSlash":      RE(to=r"//", frm=r"""/(?= [(]* (?:[a-zA-Z]) ([^(]|$) )"""),  # For unit expressions: convert mA/cm2 to mA//cm2. Looks for a bracket (or end of line), so '6 mA/log(10)' is OK
        "SlashCurlyTilde_To_DoubleSlash": RE(to=r"//", frm=r"""/(?= [(]* (?:[{][~]) )"""),    # For unit expressions: convert mA/{~milliamp} to mA//{~milliamp}


         # "{3 mV{~mjlk}/{~asd}}" -> {3 mV{~mjlk}/{~asd}}"
        "CurlyBracketUnitWithSlash":      RE(to=r"\g<pre>//\g<post>", frm=r""" (?P<pre> [{]  [-]?[0-9]+(\.[0-9]*([eE][+-]?[0-9]+)?)? \s* ( ([{][~] [a-zA-Z]* [}])|([a-zA-Z]*)\d* )* \s* ) / (?P<post> (\s* ([{][~] [a-zA-Z]* [}])|([a-zA-Z]*)\d* \s* )*  [}] )""", ),
        "CurlyBracketUnitAddSpace1":      RE(to=r" \1", frm=r"(?:[^/])({~[a-zA-Z]*})""", ),
        "CurlyBracketUnitAddSpace2":      RE(to=r"} ", frm=r"""}(?:[a-zA-Z])""", ),
        }


regexes_by_parsetype_slashes = {
        ParseTypes.L1_Unit:         [ regexes_slashes["SlashAlpha_To_DoubleSlash"], regexes_slashes["SlashCurlyTilde_To_DoubleSlash"], ],
        ParseTypes.L2_QuantitySimple:     [ regexes_slashes["SlashAlpha_To_DoubleSlash"], regexes_slashes["SlashCurlyTilde_To_DoubleSlash"], ],
        ParseTypes.L3_QuantityExpr:   [ regexes_slashes["CurlyBracketUnitWithSlash"], regexes_slashes["CurlyBracketUnitAddSpace1"], regexes_slashes["CurlyBracketUnitAddSpace2"]  ],
        ParseTypes.L4_EqnSet:   [ regexes_slashes["CurlyBracketUnitWithSlash"], regexes_slashes["CurlyBracketUnitAddSpace1"], regexes_slashes["CurlyBracketUnitAddSpace2"], ],
        ParseTypes.L5_Library:   [ regexes_slashes["CurlyBracketUnitWithSlash"], regexes_slashes["CurlyBracketUnitAddSpace1"], regexes_slashes["CurlyBracketUnitAddSpace2"], ],
        ParseTypes.L6_TextBlock:   [ regexes_slashes["CurlyBracketUnitWithSlash"], regexes_slashes["CurlyBracketUnitAddSpace1"], regexes_slashes["CurlyBracketUnitAddSpace2"], ],
        }


def apply_all_regexes(text, parsetype,regexes_by_parsetype):
    for r in regexes_by_parsetype[parsetype]:
        text = apply_regex(r,text)
    return text


def apply_regex(r, text):
    regex = re.compile(r.frm,re.VERBOSE)
    return re.sub(regex, r.to, text)













#unit_library_manager

def parse_expr(text, parse_type, start_symbol=None, debug=False, backend=None, working_dir=None, options=None,library_manager=None, name=None):

    original_text = text

    # Some initial preprocessing
    # (This is a bit hacky)
    if parse_type in [ParseTypes.L4_EqnSet, ParseTypes.L5_Library, ParseTypes.L6_TextBlock]:
        text  = "\n".join([ l.split("#")[0] for l in text.split("\n") ])
        lines = []
        for l in text.split("\n"):
            if len(lines)!=0 and lines[-1].endswith('\\'):
                assert l
                lines[-1] = lines[-1][:-1] + l

            else:
                l = l.strip()
                if not l:
                    continue
                if not l[-1] in ('{',';'):
                    l = l +";"
                lines.append(l)

        text = "\n".join( lines )
    else:
        text = text.strip()




    if library_manager is None and ParseTypes is not ParseTypes.L1_Unit:
        library_manager = LibraryManager(backend=backend, working_dir=working_dir, options=options, name=name, src_text=original_text )
    pRes, library_manager = parse_eqn_block(text, parse_type=parse_type, debug=debug, library_manager=library_manager)


    if parse_type==ParseTypes.L3_QuantityExpr:
        from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator
        F = FunctorGenerator()
        ev = F.visit(pRes)
        pRes = ev()




    ret = { ParseTypes.L1_Unit:             lambda: pRes,
            ParseTypes.L2_QuantitySimple:   lambda: pRes,
            ParseTypes.L3_QuantityExpr:     lambda: pRes,
            ParseTypes.L4_EqnSet:           lambda: SeqUtils.expect_single(library_manager.eqnsets),
            ParseTypes.L5_Library:          lambda: SeqUtils.expect_single(library_manager.libraries),
            ParseTypes.L6_TextBlock:        lambda: library_manager,
             }

    return ret[parse_type]()







class ParserMgr():

    parsers = {}

    @classmethod
    def build_parser( cls, start_symbol, debug):
        #lexer = units_expr_lexer.UnitExprLexer()
        tables_loc =  EnsureExisits("/tmp/nu/yacc/parse_eqn_block")
        parser = yacc.yacc( debug=debug, start=start_symbol,  tabmodule="neurounits_parsing_parse_eqn_block", outputdir=tables_loc,optimize=1, errorlog=ply.yacc.NullLogger()  )

        #with open("/tmp/neurounits_grammar.txt",'w') as f:
        #    for p in parser.productions:
        #        f.write( "%s\n"%p)



        return parser

    @classmethod
    def get_parser( cls, start_symbol, debug ):
        k = (start_symbol, debug)
        if not k in cls.parsers:
            cls.parsers[k] = cls.build_parser(start_symbol=start_symbol, debug=debug)
        import copy
        return copy.copy( cls.parsers[k] )






def parse_eqn_block(text_eqn, parse_type, debug, library_manager):



    start_symbol = ParseDetails.start_symbols[parse_type]
    # Some preprocessing:
    #######################

    assert not "--" in text_eqn
    assert not "//" in text_eqn

    # Strip all unnessesary whitespace:
    s1 = re.compile(r'[ ]* ([()/*:+{}=]) [ ]*',re.VERBOSE)
    text_eqn = re.sub(s1,r'\1',text_eqn)


    # '/' plays 2 roles. To simplify the grammar, turn '/' used to
    # purely separate unit terms to '//'
    # The syntax of this depends on the context of what we are parsing.
    assert not "//" in text_eqn
    text_eqn = apply_all_regexes(text_eqn, parse_type, regexes_by_parsetype_slashes)


    # Likewise, '-' plays 2 roles, as negative exponent as
    # as subtraction. Lets remap subtraction to '--', unless its followed
    # by a digit, in which case its part of that digit
    s = re.compile(r"""[ ]* [-](?=[^0-9]) [ ]*""", re.VERBOSE)
    text_eqn = re.sub(s,'--',text_eqn)

    print 'Post-Processing:'
    print text_eqn





    #debug=False
    lexer = units_expr_lexer.UnitExprLexer()
    parser = ParserMgr.get_parser( start_symbol=start_symbol, debug=debug)
    parser.library_manager = library_manager

    #assert parser.library_manager is library_manager

    # 'A': When loading QuantityExpr or Functions, we might use
    # stdlib functions. Therefore; we we need a 'block_builder':
    if parse_type in [ ParseTypes.L3_QuantityExpr]: #, ParseTypes.Function]:
        parser.library_manager.start_eqnset_block()
        parser.library_manager.get_current_block_builder().set_name("anon")



    #assert parser.library_manager is library_manager




    # TODO: I think this can be removed.
    parser.src_text = text_eqn
    parser.library_manager.src_text = text_eqn





    #assert parser.library_manager is library_manager

    pRes = parser.parse(text_eqn, lexer=lexer, debug=debug)

    #assert parser.library_manager is library_manager

    # Close the block we opened in 'A'
    if parse_type in [ ParseTypes.L3_QuantityExpr]:
        parser.library_manager.end_eqnset_block()

    #assert parser.library_manager is library_manager


    return pRes, parser.library_manager



