#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------


class UnitError(ValueError):

    pass


class DuplicateKeyError(RuntimeError):

    def __init__(self, key):
        self.key = key

    def __repr__(self):
        return 'Duplicate Key Found: %s' % str(self.key)



class InternalError(RuntimeError):

    pass


def panic():
    raise InternalError()


class UnitMismatchError(ValueError):
    def __init__(self, unitA, unitB, objA=None, objB=None,):
        self.unitA = unitA
        self.unitB = unitB
        self.objA = objA
        self.objB = objB

    def __str__(self):

        objA_name = str(self.objA)
        objB_name = str(self.objB)
        return 'Unit Imcompatibility: (%s) <-> (%s) [%s %s]' % (self.unitA, self.unitB, objA_name, objB_name)








class ParsingError(RuntimeError):

    pass


class NeuroUnitParsingError(ValueError):

    pass

class NeuroUnitParsingErrorEOF(NeuroUnitParsingError):

    def __repr__(self, ):
        return '<NeuroUnitParsingErrorEOF: ** Unexpected end-of-file found>'


class NeuroUnitParsingErrorUnexpectedToken(NeuroUnitParsingError):
    def __init__(self, bad_token ):
        self.bad_token = bad_token

        # These get set after construction, higher up the exception stack:
        self.original_text = None
        self.parsed_text = None

    def __str__(self,):
        d1 = 'NeuroUnitParsingErrorUnexpectedToken: ** Unexpcted token found'
        d2 = '\n\nOriginal text:\n==================\n%s\n=====================\n'  % self.original_text
        d3 = 'Preprocessed text:\n==================\n%s\n=====================\n'  % self.parsed_text

        d4 = 'Unexpected Token Found:  %s' % (self.bad_token)

        lines_context = 3
        lines = self.parsed_text.split('\n')
        bad_line_no = self.bad_token.lineno -1


        pre_parsed_lines = lines[ max(bad_line_no-lines_context,0): bad_line_no ]
        post_parsed_lines = lines[ bad_line_no : min(bad_line_no+lines_context,len(lines)-1) ]
        parsed_line = lines[bad_line_no]


        D6 = '\nError here'
        D7 = '\n================='
        D9 =  ''.join(['\n    |%s' %l for l in pre_parsed_lines])
        D10 = '\n -> |' + parsed_line
        D12 =  ''.join(['\n    |%s' %l for l in post_parsed_lines])
        D13 = '\n================='



        col_pos = self.bad_token.lexpos
        char_str = self.parsed_text
        def clip_to_str(k):
            return min( max(k,0), len(char_str)-1)
        line_char_context = 30
        col_pos_pre_start = clip_to_str( col_pos-line_char_context )
        col_pos_post_end = clip_to_str( col_pos+line_char_context )

        pre_str = '...' + char_str[col_pos_pre_start:col_pos]
        post_str = char_str[col_pos+1:col_pos_post_end] + '...'

        E1 = 'Specifically:'
        E2 = 'Chars: %d' % col_pos
        E3 = pre_str + char_str[col_pos] + post_str
        E4 = ' ' * len(pre_str) + '^' + ' ' * len(post_str)
        


        print self.bad_token.__dict__



        'OK!'
        D = ''.join([D6,D7,D9,D10,D12, D13])
        E = ''.join(['\n%s'%s for s in (E1,E2,E3,E4)])

        return d1 + d2 + d3 + d4 + '\n\n\n' + D +'\n' + E  + '\nOVER' + ','.join( self.bad_token.__dict__.keys() )



class InvalidUnitTermError(ValueError):
    pass





class ASTMissingAnnotationError(RuntimeError):
    def __init__(self, node, annotation):
        super(ASTMissingAnnotationError, self).__init__()
        self.node = node
        self.annotation = annotation
    def __repr__(self, ):
        return "Annotation: '%s' not found for  %s (type: %s)" % (self.annotation, self.node, type(self.node) )
    def __str__(self, ):
        return repr(self)
