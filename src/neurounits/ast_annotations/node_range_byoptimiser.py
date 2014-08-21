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
from collections import defaultdict

import random
import sys
import math
from mako.template import Template
import numpy as np
import scipy
import scipy.optimize

from cffi import FFI

from neurounits.ast_annotations.bases import ASTTreeAnnotator
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits import ast
from neurounits.visitors.bases.base_actioner_default import ASTActionerDefault
from neurounits.visitors.common.ast_symbol_dependancies_new import VisitorSymbolDependance
from neurounits.ast_annotations.common import _NodeRangeFloat



class CriticalPointFinder(ASTActionerDefault):

    def __init__(self, component):
        self.critical_points = defaultdict(set)
        super(CriticalPointFinder, self).__init__()
        self.visit(component)

    def ActionNode(self, n):
        pass

    def ActionInEquality(self, n):
        if isinstance(n.lesser_than, ast.ASTConstNode) and isinstance(n.greater_than, ast.ASTSymbolNode):
            self.critical_points[n.greater_than].add(n.lesser_than.value.float_in_si())
            return
        if isinstance(n.greater_than, ast.ASTConstNode) and isinstance(n.lesser_than, ast.ASTSymbolNode):
            self.critical_points[n.lesser_than].add(n.greater_than.value.float_in_si())
            return


























class CFloatEval(ASTVisitorBase):
    def __init__(self, the_component):
        self.component = the_component
        super(CFloatEval, self).__init__()



    def VisitAssignedVariable(self, o, **kwargs):
        return self.visit(self.component.assignedvariable_to_assignment(o).rhs_map)

    def VisitRegimeDispatchMap(self, o, **kwargs):
        assert len(o.rhs_map) == 1
        return self.visit(o.rhs_map.values()[0])

    def VisitAddOp(self, o, **kwargs):
        return '((%s) + (%s))' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitSubOp(self, o, **kwargs):
        return '((%s) - (%s))' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitMulOp(self, o, **kwargs):
        return '((%s) * (%s))' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitDivOp(self, o, **kwargs):
        return '((%s) / (%s))' % (self.visit(o.lhs), self.visit(o.rhs))



    def VisitOnEventStateAssignment(self, o, **kwargs):
        return self.visit(o.rhs)

    def VisitSymbolicConstant(self, o, **kwargs):
        return '%g' % o.value.float_in_si()


    def VisitIfThenElse(self, o, **kwargs):
        return "( (%s) ? (%s) : (%s) )" %(
                            self.visit(o.predicate),
                            self.visit(o.if_true_ast),
                            self.visit(o.if_false_ast))

    def VisitInEquality(self, o, **kwargs):
        return "( (%s) < (%s) )" % (
                            self.visit(o.lesser_than),
                            self.visit(o.greater_than)
                                    )

    def VisitBoolAnd(self, o, **kwargs):
        return "((%s)&&(%s))" % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitBoolOr(self, o, **kwargs):
        return "((%s)||(%s))" % (self.visit(o.lhs), self.visit(o.rhs))


    def VisitBoolNot(self, o, **kwargs):
        return "(!(%s))" % self.visit(o.lhs)

    def VisitFunctionDefUser(self, o, **kwargs):
        raise NotImplementedError()

    def VisitStateVariable(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitAutoRegressiveModel(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitParameter(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitConstant(self, o, **kwargs):
        return "%g" % (o.value.float_in_si() )

    def VisitSuppliedValue(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitTimeVariable(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)

    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return self.visit(o.rhs_map)



    def VisitExpOp(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        if o.function_def.funcname == '__exp__':
            return 'exp(%s)' % self.visit(o.parameters.values()[0])
        assert False

    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        return self.visit(o.rhs_ast)

    def VisitRandomVariable(self, n, **kwargs):
        return 'input_data->%s' %  n.annotations['_range-finding-c-var-name']

    def VisitRandomVariableParameter(self, o, **kwargs):
        print self, o
        assert False, 'Added August 2014'

    def VisitOnEventDefParameter(self, o):
        return 'input_data->%s' %  o.annotations['_range-finding-c-var-name']

    def VisitInEventPortParameter(self, o):
        assert False
        return 'input_data->%s' %  o.annotations['_range-finding-c-var-name']














class NodeEvaluatorCCode(ASTActionerDefault):

    def __init__(self, component):
        self.node_code = {}
        self.component = component
        super(NodeEvaluatorCCode, self).__init__(component=component)

    def ActionNode(self, n, **kwargs):
        pass

    def BuildEvalFunc(self, n):
        if n in self.node_code:
            return
        name = n.annotations['_range-finding-c-func-name']
        code = CFloatEval(the_component=self.component).visit(n)
        assert not n in self.node_code
        self.node_code[n] = (name, code)

    def ActionIfThenElse(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionInEquality(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionFunctionDefUser(self, o, **kwargs):
        assert False

    def ActionFunctionDefBuiltIn(self, o, **kwargs):
        pass

    def ActionStateVariable(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionParameter(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionConstantZero(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionAssignedVariable(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionSuppliedValue(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionTimeVariable(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionAnalogReducePort(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionTimeDerivativeByRegime(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionRegimeDispatchMap(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionEqnAssignmentByRegime(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionAddOp(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionSubOp(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionMulOp(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionDivOp(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionExpOp(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionFunctionDefUserInstantiation(self, o, **kwargs):
        assert False
        return self.BuildEvalFunc(o)

    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionOnEventDefParameter(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionAnalogVisitor(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionEmitEventParameter(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionOutEventPortParameter(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionRandomVariable(self, o, **kwargs):
        return self.BuildEvalFunc(o)

    def ActionAutoRegressiveModel(self, o, **kwargs):
        return self.BuildEvalFunc(o)


input_ds_tmpl = Template("""
typedef struct  {
    %for sym in list(component.all_input_terminals) + list(component.random_variable_nodes) + list(component.autoregressive_model_nodes):
    double ${sym.annotations['_range-finding-c-var-name']};
    %endfor

    %for tr  in component.eventtransitions:
    %for param in tr.parameters:
        double ${param.annotations['_range-finding-c-var-name']};
    %endfor
    %endfor

    %for rtgraph in component.rt_graphs:
    enum Regime_${rtgraph.name} { ${ ','.join([(r.name if r.name is not None else 'None') for r in rtgraph.regimes]) } } regime_${rtgraph.name};
    %endfor
} InputData;
""")


class NodeRangeCCodeNodeNamer(ASTTreeAnnotator, ASTActionerDefault):

    def annotate_ast(self, component):
        self.visit(component)

    def ActionNode(self, n):
        pass

    def set_var_name(self, n, name):
        n.annotations['_range-finding-c-var-name'] = name

    def set_func_name(self, n, name=None):
        if name is None:
            name = 'eval_node_%s_%s' % (type(n).__name__, id(n))
        n.annotations['_range-finding-c-func-name'] = name

    def ActionRandomVariable(self, o, **kwargs):
        self.set_var_name(o, name='rv_%s' % str(id(o)))
        self.set_func_name(o)

    def ActionAutoRegressiveModel(self, o, **kwargs):
        self.set_var_name(o, name='rv_%s' % str(id(o)))
        self.set_func_name(o)

    def _ActionSymbolTerminal(self, o):
        self.set_var_name(o, name=o.symbol)
        self.set_func_name(o)

    def ActionStateVariable(self, o):
        self._ActionSymbolTerminal(o)

    def ActionAssignedVariable(self, o):
        self._ActionSymbolTerminal(o)

    def ActionSuppliedValue(self, o):
        self._ActionSymbolTerminal(o)

    def ActionTimeVariable(self, o):
        self._ActionSymbolTerminal(o)

    def ActionParameter(self, o):
        self._ActionSymbolTerminal(o)

    def ActionInEquality(self, n, **kwargs):
        self.set_func_name(n)

    def ActionIfThenElse(self, n, **kwargs):
        self.set_func_name(n)

    def ActionAddOp(self, o, **kwargs):
        self.set_func_name(o)

    def ActionSubOp(self, o, **kwargs):
        self.set_func_name(o)

    def ActionMulOp(self, o, **kwargs):
        self.set_func_name(o)

    def ActionDivOp(self, o, **kwargs):
        self.set_func_name(o)

    def ActionFunctionDefInstantiationParameter(self, o, **kwargs):
        self.set_func_name(o)

    def ActionFunctionDefBuiltInInstantiation(self, o, **kwargs):
        self.set_func_name(o)

    def ActionRegimeDispatchMap(self, o, **kwargs):
        self.set_func_name(o)

    def ActionTimeDerivativeByRegime(self, o):
        self.set_func_name(o)

    def ActionEqnAssignmentByRegime(self, o):
        self.set_func_name(o)

    def ActionRandomVariableParameter(self, o):
        self.set_func_name(o)

    def ActionOnEventDefParameter(self, o):
        self.set_var_name(o, name=o.symbol + '_%s' % str(id(o)))
        self.set_func_name(o)

    def ActionInEventPortParameter(self, o):
        self.set_var_name(o, name=o.symbol + '_%s' % str(id(o)))
        self.set_func_name(o)

    # Types we can skip:
    def ActionSymbolicConstant(self, o):
        pass

    def ActionConstant(self, o):
        pass

    def ActionRegime(self, o):
        pass


class NodeRangeByOptimiser(ASTVisitorBase, ASTTreeAnnotator):
    def __init__(self, var_annots_ranges):
        self.var_annots_ranges = var_annots_ranges
        super(NodeRangeByOptimiser, self).__init__()




    @classmethod
    def find_minmax_for_node(self, node, component, cffi_top, cffi_code_obj, critical_points):
            print '.',
            sys.stdout.flush()
            deps = VisitorSymbolDependance(component)._get_dependancies(
                                                            node=node,
                                                            expand_assignments=True,
                                                            include_random_variables=True,
                                                            include_supplied_values=True,
                                                            include_symbolic_constants=False,
                                                            include_parameters=True,
                                                            include_analog_input_ports=True,
                                                            include_inevent_parameters=True,
                                                            include_time=True
                                                            )

            inputdata = cffi_top.new('InputData*')

            depnames = [dep.annotations['_range-finding-c-var-name'] for dep in deps]
            ass_var_fun_name = node.annotations['_range-finding-c-func-name']
            func = getattr(cffi_code_obj, ass_var_fun_name)


            def eval_func_min(p):
                for i,depname in enumerate(depnames):
                    setattr(inputdata, depname, p[i])
                res = func(inputdata)
                return res

            def eval_func_max(p):
                return -eval_func_min(p)


            upper_bounds = np.array( [ dep.annotations['node-value-range'].max for dep in deps] )
            lower_bounds = np.array( [ dep.annotations['node-value-range'].min for dep in deps] )
            bounds = [ (lower_bounds[i],upper_bounds[i]) for i in range(len(deps)) ]


            def get_sample_pts(node):
                # By default, lets check the extremes and the midpoints:
                min = dep.annotations['node-value-range'].min
                max = dep.annotations['node-value-range'].max
                samples = [min, max]

                if node in critical_points:
                    samples = sorted( set(critical_points[node]) | set(samples) )

                mid_pts = []
                for i in range(len(samples)-1):
                    mid_pts.append( (samples[i]+samples[i+1]) /2. )

                samples = sorted(samples + mid_pts)
                return samples


            samples = [ get_sample_pts(node) for node in deps]

            res_min = res_max = None


            n_trials = 50
            for i in range(n_trials):




                x0 = [ random.choice(s) for s in samples]

                method = 'TNC'
                tol = 1e-15
                local_res_min_param = scipy.optimize.minimize(eval_func_min, x0, method=method, bounds=bounds, tol=tol)
                local_res_max_param = scipy.optimize.minimize(eval_func_max, x0, method=method, bounds=bounds, tol=tol)

                local_res_min = eval_func_min( local_res_min_param.x)
                local_res_max = eval_func_min( local_res_max_param.x)


                if (res_min is None or local_res_min < res_min) and not math.isnan(local_res_min):
                    res_min = local_res_min
                if (res_max is None or local_res_max > res_max) and not math.isnan(local_res_max):
                    res_max = local_res_max





            int(res_min)
            int(res_max)

            return res_min, res_max



    def annotate_ast(self, component, **kwargs):

        # 0. Ensure all the state-variables have ranges:
        for sv in list(component.state_variables) + list(component.suppliedvalues) + [component._time_node] + list(component.parameters):
            assert sv.symbol in self.var_annots_ranges, 'Range-annotation missing for variable: %s' % sv.symbol
            ann_in = self.var_annots_ranges[sv.symbol]
            sv.annotations['node-value-range'] = _NodeRangeFloat(min_=ann_in.min.float_in_si(), max_=ann_in.max.float_in_si() )

        # 0b. And transitions trigger by events:
        for tr in component.eventtransitions:
            for p in tr.parameters:
                lookup_name = "%s::%s" % (tr.port.symbol, p.symbol)
                ann_in = self.var_annots_ranges[lookup_name]
                p.annotations['node-value-range'] = _NodeRangeFloat(min_=ann_in.min.float_in_si(), max_=ann_in.max.float_in_si() )


        # ... which allows us to work out the mins and maxs for the event port:
        for in_evt_port in component.input_event_port_lut:
            trs = [tr for tr in component.eventtransitions if tr.port==in_evt_port]

            for param in in_evt_port.parameters:

                trs_param = [ tr.parameters.get_single_obj_by(symbol=param.symbol) for tr in trs]
                node_min = min([ p.annotations['node-value-range'].min for p in trs_param ] )
                node_max = max([ p.annotations['node-value-range'].max for p in trs_param ])

                param.annotations['node-value-range'] = _NodeRangeFloat(min_=node_min, max_=node_max )




        # Random variables:
        for rv in component.random_variable_nodes:
            assert rv.functionname == 'uniform'
            min_param = rv.parameters.get_single_obj_by(name='min')
            max_param = rv.parameters.get_single_obj_by(name='max')
            print 'Params', min_param.rhs_ast, max_param.rhs_ast
            min_val = min_param.rhs_ast.value.float_in_si()
            max_val = max_param.rhs_ast.value.float_in_si()
            rv.annotations['node-value-range'] = _NodeRangeFloat(
                    min_= min_val,
                    max_= max_val,
                    )
            min_param.annotations['node-value-range'] = _NodeRangeFloat(min_=min_val, max_=min_val)
            max_param.annotations['node-value-range'] = _NodeRangeFloat(min_=max_val, max_=max_val)

        # And the autoregressive model nodes (HACK!):
        for ar in component.autoregressive_model_nodes:
            ar.annotations['node-value-range'] = _NodeRangeFloat(
                    min_= -1,
                    max_= +1,
                    )



        # Calculate all constants:
        constant_nodes = [node for node in  component.all_ast_nodes() if isinstance(node, ast.ASTConstNode) ]
        for const_node in constant_nodes:
            val = const_node.value.float_in_si()
            const_node.annotations['node-value-range'] = _NodeRangeFloat(min_=val, max_=val)



        # 0b. Ensure that each node has a name for accessing the data-structure and
        # for calling the evaluation function:
        component.annotate_ast( NodeRangeCCodeNodeNamer() )




        # 1. Build the Python/C Library:
        # =================================

        # A. Build a structure for the data:
        input_ds = input_ds_tmpl.render(component = component)


        # B. Build evalutation functions for each node:
        node_evaluator_c_code = NodeEvaluatorCCode(component)
        func_prototypes = []
        func_defs = []
        for node, (node_name, node_code) in node_evaluator_c_code.node_code.items():
            func_sig = "double %s(InputData* input_data)" % (node_name)
            func_prototypes.append( func_sig + ';' )
            func_defs.append( func_sig + '{ return %s; }' % (node_code)  )


        # C. Prototype and compile...
        
        ffi = FFI()

        ffi.cdef(input_ds)

        for func_proto in func_prototypes:
            ffi.cdef(func_proto)

        code =  '\n'.join( [input_ds] + func_defs)

        print 'Compiling C-Code to find intermediate nodes:'
        with open('cffi_debug.c.log','w') as f:
            f.write(code)

        C = ffi.verify(code)
        print 'OK'

        # 2. Evaluate for each node:




        # Find the critical points of the equations:
        critical_points = CriticalPointFinder(component).critical_points


        print 'Evaluating all nodes in AST tree to find limits:'

        print 'Assignmnemts:',
        for ass_var in component.assignedvalues:
            func_min,func_max = NodeRangeByOptimiser.find_minmax_for_node(node=ass_var, component=component, cffi_top=ffi, cffi_code_obj=C,critical_points=critical_points)
            ass_var.annotations['node-value-range'] = _NodeRangeFloat(min_=func_min, max_=func_max)


        required_nodes_types = (ast.IfThenElse, ast.InEquality,
                                ast.AddOp, ast.SubOp, ast.MulOp, ast.DivOp,
                                ast.FunctionDefParameterInstantiation, ast.FunctionDefBuiltInInstantiation,
                                ast.EqnRegimeDispatchMap,

                                )

        print 'Internal nodes:',
        ranges_nodes = [n for n in component.all_ast_nodes() if isinstance(n, required_nodes_types) ]
        for node in ranges_nodes:

            func_min,func_max = NodeRangeByOptimiser.find_minmax_for_node(node=node, component=component, cffi_top=ffi, cffi_code_obj=C,critical_points=critical_points)
            node.annotations['node-value-range'] = _NodeRangeFloat(min_=func_min, max_=func_max)

