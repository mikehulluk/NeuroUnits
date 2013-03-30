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

from neurounits import ast
from neurounits.visitors import ASTVisitorBase


class DotVisitor(ASTVisitorBase):

    def __init__(self):
        import networkx as nx
        print 'DotWriter'
        self.g = nx.Graph()

    def VisitEqnSet(self, o, **kwargs):
        import networkx as nx

        for a in o.functiondefs:
            self.visit(a)

        for a in o.assignments:
            self.visit(a)

        for a in o.timederivatives:
            self.visit(a)


        nodelist = list( self.g )

        labeller = {
                ast.BuiltInFunction :       lambda n: "BuiltInFunc: %s" %n.funcname,
                ast.FunctionDef :           lambda n: "FuncDef: %s" %n.funcname,
                ast.FunctionDefParameter :  lambda n: "Param %s" %n.symbol,
                ast.AddOp :                 lambda n: "+",
                ast.SubOp :                 lambda n: "-",
                ast.MulOp :                 lambda n: "*",
                ast.DivOp :                 lambda n: "/",
                ast.ExpOp :                 lambda n: "**",

                ast.SuppliedValue :         lambda n: "Supplied: %s" %n.symbol,
                ast.ConstValue:             lambda n: "Const: %s "%n.value,
                ast.Parameter:              lambda n: "Param: %s" %n.symbol,
                ast.AssignedVariable:       lambda n: "Assigned: %s" %n.symbol,
                ast.StateVariable:          lambda n: "State: %s" %n.symbol,
                ast.SymbolicConstant:       lambda n: "SymConst: %s %s"%(n.symbol,n.value),


                ast.EqnTimeDerivative:      lambda n: "d/dt",
                #ast.EqnAssignment:          lambda n: ":=",
                ast.EqnAssignmentByRegime:          lambda n: ":=",

                ast.FunctionDefInstantiation: lambda n: "%s()"%(n.function_def.funcname),

                # Boolean Expressions:
                ast.InEquality:             lambda n: "<",
                ast.IfThenElse:             lambda n: "IfThenElse",
                ast.BoolAnd:                lambda n: "&&",
                ast.BoolOr:                 lambda n: "||",
                ast.BoolNot:                lambda n: "!",
                }

        def get_label(o):
            return labeller[type(o)](o)

        color_scheme = {
                ast.FunctionDef :           'b',
                ast.FunctionDefParameter :  'r',
                ast.AddOp :                 'orange',
                ast.SubOp :                 'orange',
                ast.MulOp :                 'orange',
                ast.DivOp :                 'orange',

                ast.SuppliedValue :         'green',
                ast.ConstValue :            'green',
                ast.Parameter :             'green',

                ast.AssignedVariable :             'purple',
                ast.StateVariable :             'purple',
                }


        # P.show()

    def VisitAndAddEdge(self, src, dst):
        self.visit(dst)
        self.g.add_edge(src, dst)

    # Function Definitions:

    def VisitFunctionDef(self, o, **kwargs):
        self.g.add_node(o)

        # Parameters:

        for p in o.parameters.values():
            self.VisitAndAddEdge(o, p)

        # RHS:
        self.VisitAndAddEdge(o, o.rhs)


    def VisitFunctionDefParameter(self, o, **kwargs):
        self.g.add_node(o)

    # Terminals:

    def VisitStateVariable(self, o, **kwargs):
        self.g.add_node(o)

    def VisitParameter(self, o, **kwargs):
        self.g.add_node(o)

    def VisitConstant(self, o, **kwargs):
        self.g.add_node(o)

    def VisitAssignedVariable(self, o, **kwargs):
        self.g.add_node(o)

    def VisitSuppliedValue(self, o, **kwargs):
        self.g.add_node(o)

    # AST Objects:

    def VisitEqnTimeDerivative(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitEqnAssignment(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitAddOp(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitSubOp(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitMulOp(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitDivOp(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitExpOp(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)

    def VisitBoolAnd(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitBoolOr(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)
        self.VisitAndAddEdge(o, o.rhs)

    def VisitBoolNot(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.lhs)

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        self.g.add_node(o)

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        self.g.add_node(o)

    def VisitIfThenElse(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.if_true_ast)
        self.VisitAndAddEdge(o, o.if_false_ast)
        self.VisitAndAddEdge(o, o.predicate)

    def VisitInEquality(self, o, **kwargs):
        self.g.add_node(o)
        self.VisitAndAddEdge(o, o.less_than)
        self.VisitAndAddEdge(o, o.greater_than)

    def VisitBuiltInFunction(self, o, **kwargs):
        self.g.add_node(o)

    def VisitSymbolicConstant(self, o, **kwargs):
        self.g.add_node(o)


