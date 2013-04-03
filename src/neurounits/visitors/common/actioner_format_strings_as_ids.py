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

from neurounits.visitors import ASTActionerDefault


class ActionerFormatStringsAsIDs(ASTActionerDefault):

    def __init__(self, identifier_dict):
        ASTActionerDefault.__init__(self)

        self.format_strings = {}
        self.IDs = identifier_dict

    def tofile(self, filename):

        d = []
        for (k, v) in self.format_strings.iteritems():
            d.append((self.IDs[k], v))
        d.sort()

        # Write to a file:
        with open(filename, 'w') as f:
            for (k, v) in d:
                f.write('%s %s\n' % (k.ljust(6), v))

    # AST Top Level:
    def ActionEqnSet(self, o, **kwargs):
        funcdefs = ','.join(self.IDs[f] for f in o.functiondefs)
        timederivatives = ','.join(self.IDs[f] for f in
                                   o.timederivatives)
        assignments = ','.join(self.IDs[f] for f in o.assignments)
        symbolicconstants = ','.join(self.IDs[f] for f in
                o.symbolicconstants)

        data = (assignments, timederivatives, funcdefs,
                symbolicconstants)
        s = '<EqnSet: Assignments: [%s] TimeDerivatives:[%s], FunctionDefs:[%s], SymbolicConstants:[%s]' \
            % data
        self.format_strings[o] = s

    def ActionLibrary(self, o, **kwargs):
        funcdefs = ','.join(self.IDs[f] for f in o.functiondefs)
        symbolicconstants = ','.join(self.IDs[f] for f in
                o.symbolicconstants)

        data = (funcdefs, symbolicconstants)
        s = '<EqnSet: FunctionDefs:[%s], SymbolicConstants:[%s]' % data
        self.format_strings[o] = s

    # Function Definitions:
    def ActionOnEvent(self, o, **kwargs):
        pStr = ','.join(['%s=%s' % (p, self.IDs[v]) for (p, v) in
                        o.parameters.iteritems()])
        actions = ','.join([self.IDs[a] for a in o.actions])
        self.format_strings[o] = \
            'OnEvent: Name:%s Params:%s Actions: [%s]' % (o.name, pStr,
                actions)

    def ActionOnEventStateAssignment(self, o, **kwargs):
        self.format_strings[o] = "OnEventStateAssignment: '%s' = %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs])

    # Function Definitions:
    def ActionFunctionDef(self, o, **kwargs):
        pStr =','.join(['%s=%s' % (p,self.IDs[v]) for (p, v) in o.parameters.iteritems()])
        self.format_strings[o] = 'FunctionDef: Name:%s Params:%s RHS: %s' % (o.funcname, pStr, self.IDs[o.rhs])

    def ActionFunctionDefParameter(self, o, **kwargs):
        self.format_strings[o] = "FunctionDefParam: '(%s)' " \
            % (o.symbol, )

    def ActionBuiltInFunction(self, o, **kwargs):
        pStr = ','.join(['%s=%s' % (p, self.IDs[v]) for (p, v) in
                        o.parameters.iteritems()])
        self.format_strings[o] = "BuiltinFunction: '%s' Params:%s " \
            % (o.funcname, pStr)

    # Terminals:
    def ActionStateVariable(self, o, **kwargs):
        self.format_strings[o] = "StateVariable '%s'" % o.symbol

    def ActionParameter(self, o, **kwargs):
        self.format_strings[o] = "Parameter '%s'" % o.symbol

    def ActionConstant(self, o, **kwargs):
        self.format_strings[o] = "Constant '%s'" % o.value

    def ActionAssignedVariable(self, o, **kwargs):
        self.format_strings[o] = "AssignedVariable '%s'" % o.symbol

    def ActionSuppliedValue(self, o, **kwargs):
        self.format_strings[o] = "SuppliedVariable '%s'" % o.symbol

    def ActionSymbolicConstant(self, o, **kwargs):
        self.format_strings[o] = "SymbolicConstant '%s' (%s)" \
            % (o.symbol, o.value)

    # AST Objects:
    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        self.format_strings[o] = 'Time Derivative: d/dt (%s) = %s' \
            % (self.IDs[o.lhs], self.IDs[o.rhs_map])

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        self.format_strings[o] = "Assignment: '%s' = %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs_map])

    # AST Nodes:
    def ActionAddOp(self, o, **kwargs):
        self.format_strings[o] = "BinaryOp: '%s' + %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionSubOp(self, o, **kwargs):
        self.format_strings[o] = "BinaryOp: '%s' - %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionMulOp(self, o, **kwargs):
        self.format_strings[o] = "BinaryOp: '%s' * %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionDivOp(self, o, **kwargs):
        self.format_strings[o] = "BinaryOp: '%s' / %s" \
            % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionExpOp(self, o, **kwargs):
        self.format_strings[o] = "BinaryOp: '%s' ** %d" \
            % (self.IDs[o.lhs], o.rhs)

    def ActionBoolAnd(self, o, **kwargs):
        return '(%s && %s)' % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionBoolOr(self, o, **kwargs):
        return '(%s || %s)' % (self.IDs[o.lhs], self.IDs[o.rhs])

    def ActionBoolNot(self, o, **kwargs):
        return '(! %s)' % self.IDs[o.lhs]

    def ActionFunctionDefInstantiation(self, o, **kwargs):
        pStr = ','.join(['%s=%s' % (p, self.IDs[v]) for (p, v) in
                        o.parameters.iteritems()])
        self.format_strings[o] = \
            'FunctionInstantiation: Func:%s Params:%s ' \
            % (self.IDs[o.function_def], pStr)

    def ActionFunctionDefInstantiationParater(self, o, **kwargs):
        self.format_strings[o] = \
            "FunctionInstantiationParam: '(%s)' = %s" % (o.symbol,
                self.IDs[o.rhs_ast])


    def ActionIfThenElse(self,o, **kwargs):
        return "[%s] if [%s] else [%s]" %(self.IDs[o.if_true_ast],
                                           self.IDs[o.predicate],
                                           self.IDs[o.if_false_ast] )
    def ActionInEquality(self, o, **kwargs):
        return '[%s < %s]' % (self.IDs[o.less_than],self.IDs[o.greater_than])

