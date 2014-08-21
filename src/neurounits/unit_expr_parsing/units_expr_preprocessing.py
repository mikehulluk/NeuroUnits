#!/usr/bin/python
# -*- coding: utf-8 -*-

from units_expr_parsetypes import ParseTypes

import re


def join_lines_and_add_semicolons(text):
    # (This is a bit hacky)
    text = '\n'.join([l.split('#')[0] for l in text.split('\n')])
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
    if parse_type in [ ParseTypes.N6_9MLFile]:
        text= join_lines_and_add_semicolons(text)
    else:
        text = text.strip()

    return text

