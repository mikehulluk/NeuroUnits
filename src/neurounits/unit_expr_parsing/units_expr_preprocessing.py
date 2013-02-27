


from units_expr_parsetypes import ParseTypes

import re
from collections import namedtuple




RE = namedtuple('RE', ['frm', 'to'])



if_stmt_regex1 =  RE(frm=r"\s*\b(if|then|else)\b\s*", to=r"""\1""")
if_stmt_regexes = [if_stmt_regex1]
logical_regex_not = RE(frm=r"\s*\bnot\b\s*", to=r"""!""")
logical_regex_and = RE(frm=r"\s*\band\b\s*", to=r"""&""")
logical_regex_or = RE(frm=r"\s*\bor\b\s*", to=r"""|""")
logic_regexes = [logical_regex_not, logical_regex_and, logical_regex_or]

complex_regexes = if_stmt_regexes + logic_regexes

def apply_regex(r, text):
    regex = re.compile(r.frm, re.VERBOSE)
    return re.sub(regex, r.to, text)








def join_lines_and_add_semicolons(text):
    # (This is a bit hacky)
    text  = "\n".join([ l.split("#")[0] for l in text.split("\n") ])
    lines = []
    for l in text.split('\n'):
        if len(lines) != 0 and lines[-1].endswith('\\'):
            assert l
            lines[-1] = (lines[-1])[:-1] + l

        else:
            l = l.strip()
            if not l:
                continue
            if not l[-1] in ('{', ';'):
                l = l + ';'
            lines.append(l)

    text = '\n'.join(lines)

    return text





def preprocess_string(src_text, parse_type):
    text = src_text

    # Add semicolons and join lines with a trailing \
    if parse_type in [ParseTypes.L4_EqnSet, ParseTypes.L5_Library, ParseTypes.L6_TextBlock]:
        text= join_lines_and_add_semicolons(text)
    else:
        text = text.strip()


    # Trim whitespace around: if, then, else, and replace and or not with symbols '& | !'
    complex_regexes = if_stmt_regexes + logic_regexes
    for reg in complex_regexes:
        text = apply_regex(reg, text)

    # Replace all essential whitespace with '$$'
    rws = re.compile(r'''(?<=[0-9])[\t ]+(?=[0-9])''')
    if rws.search(text):
        assert False, 'Found two numbers separated by whitespace'

    rws = re.compile(r'''(?<=[a-zA-Z0-9])[\t ]+(?=[a-zA-Z])''')
    text = rws.sub(r'''$$''', text)

    # Replace all remaining whitespace, then replace '$$' with a space:
    text = text.replace(' ','')
    text = text.replace('$$',' ')


    return text



