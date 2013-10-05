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

from neurounits.visitors import ASTVisitorBase

from neurounits.ast.astobjects import SuppliedValue
from neurounits.ast.astobjects import Parameter, StateVariable, TimeVariable
from neurounits.ast import AnalogReducePort
#from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator

import quantities as pq
import numpy as np

from neurounits.ast import FunctionDefBuiltIn

try:
    from mredoc import VerticalColTable, Figure, SectionNewPage, Section, EquationBlock, VerbatimBlock, Equation, Image, HierachyScope
except ImportError:
    print "Problem importing mredoc - you won't be able to make summary documents"





def get_prefered_dimensions():
    from neurounits import NeuroUnitParser
    prefered_dimension_dims = [
        (NeuroUnitParser.Unit('S'), 'S'),
        (NeuroUnitParser.Unit('V'), 'V'),
        (NeuroUnitParser.Unit('A'), 'A'),
        (NeuroUnitParser.Unit('S/m2'), 'S/m2'),
        (NeuroUnitParser.Unit('A/m2'), 'A/m2'),
        (NeuroUnitParser.Unit('mV'), 'mV'),
        (NeuroUnitParser.Unit('ms'), 'ms'),
        (NeuroUnitParser.Unit('ms-1'), 'ms^{-1}'),
        (NeuroUnitParser.Unit('K'), 'K'),
        ]

    return prefered_dimension_dims


def FormatDimensionality(dim):
    for (unit, symbol) in get_prefered_dimensions():
        if dim == unit:
            return symbol
    return dim.FormatLatex()




def include_id_in_overbrace(func):
    def new_func(self, o, *args,**kwargs):
        res = func(self, o, *args, **kwargs)
        return r'\overbrace{%s}^{ID:%s/%s, US:%s (M/M:%s/%s)}' % (res, 
                id(o), 
                o.annotations.get('node-id','??'), 
                o.annotations['fixed-point-format'].upscale,
                o.annotations['node-value-range'].min,
                o.annotations['node-value-range'].max,
                ) 
    return new_func

class LatexEqnWriterN(ASTVisitorBase):

    def FormatTerminalSymbol(self, symbol):
        symbol_components = symbol.split('_')
        subscripts = symbol_components[1:]

        if subscripts:
            symbol = '%s_{%s}' % (symbol_components[0],
                                  ','.join(subscripts))

        return r"""\boldsymbol{%s}""" % symbol.replace('alpha',
                r"\alpha").replace('beta', r"\beta").replace('inf',
                r"\infty").replace('tau', r"\tau")
        return r"""\boldsymbol{%s}""" % symbol

    def FormatInlineConstant(self, val):
        if val.is_dimensionless(allow_non_zero_power_of_ten=False):
            return str(val.magnitude)
        elif val.is_dimensionless(allow_non_zero_power_of_ten=True):
            return '%fe%d' % (str(val.magnitude), val.unit.powerTen)
        else:

            dim_str = FormatDimensionality(val.unit)
            return r"\langle %s ~ \mathrm{%s} \rangle" \
                % (str(val.magnitude), dim_str)



    def VisitEqnAssignmentByRegime(self, o, **kwargs):
        return Equation('%s&=%s' % (self.visit(o.lhs),
                        self.visit(o.rhs_map)))

    def VisitTimeDerivativeByRegime(self, o, **kwargs):
        return Equation(r"""\frac{d}{dt}%s &= %s""" % (self.visit(o.lhs), self.visit(o.rhs_map)) )

    def VisitRegimeDispatchMap(self, o, **kwargs):
        if len(o.rhs_map) == 1:
            return self.visit(o.rhs_map.values()[0])
        else:
            case_lines = [ '%s & if %s'%(reg, self.visit(rhs)) for (reg,rhs) in o.rhs_map.items() ]
            return r""" \begin{cases} %s \end{cases}""" % ( r'\\'.join(case_lines))






    def VisitAutoRegressiveModel(self, o, **kwargs):
        return 'AUTOREGRESSIVE_NODE'


    def VisitOnEvent(self, o, **kwargs):
        ev_name = o.symbol.replace('_', '\\_')

        tr = '%s(%s) \\rightarrow ' % (ev_name,
                ','.join(o.parameters.keys()))  #
        evts = '\\begin{cases}' + '\\\\'.join([self.visit(a) for a in
                o.actions]) + '\\end{cases}'
        return Equation(tr + evts)

    def VisitOnEventStateAssignment(self, o, **kwargs):
        return '%s = %s' % (self.visit(o.lhs), self.visit(o.rhs))


    def VisitFunctionDefUser(self, o, **kwargs):
        return Equation('%s(%s) \\rightarrow %s' % (o.funcname,
                        ','.join(o.parameters.keys()),
                        self.visit(o.rhs)))

    def VisitFunctionDefParameter(self, o, **kwargs):
        return "\mathit{%s}" % o.symbol.replace('_', '\\_')


    @include_id_in_overbrace
    def VisitStateVariable(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitParameter(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    @include_id_in_overbrace
    def VisitConstant(self, o, **kwargs):
        return self.FormatInlineConstant(o.value)

    def VisitConstantZero(self, o, **kwargs):
        from neurounits.units_backends.mh import MMQuantity
        return self.FormatInlineConstant( MMQuantity(0, o.get_dimension()) )

    def VisitAssignedVariable(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitSuppliedValue(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)
    def VisitTimeVariable(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    @include_id_in_overbrace
    def VisitSymbolicConstant(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitAnalogReducePort(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    @include_id_in_overbrace
    def VisitAddOp(self, o, **kwargs):
        return '(%s + %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    @include_id_in_overbrace
    def VisitSubOp(self, o, **kwargs):
        return '(%s - %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    @include_id_in_overbrace
    def VisitMulOp(self, o, **kwargs):
        return '%s \cdot %s' % (self.visit(o.lhs), self.visit(o.rhs))

    @include_id_in_overbrace
    def VisitDivOp(self, o, **kwargs):
        return '\dfrac{%s}{%s}' % (self.visit(o.lhs), self.visit(o.rhs))

    @include_id_in_overbrace
    def VisitExpOp(self, o, **kwargs):
        return '%s ^{ %s }' % (self.visit(o.lhs), o.rhs)

    def VisitBoolAnd(self, o, **kwargs):
        return '(%s AND %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitBoolOr(self, o, **kwargs):
        return '(%s OR %s)' % (self.visit(o.lhs), self.visit(o.rhs))

    def VisitBoolNot(self, o, **kwargs):
        return '(NOT %s)' % self.visit(o.lhs)

    def VisitFunctionDefUserInstantiation(self, o, **kwargs):
        p = [self.visit(p) for p in o.parameters.values()]
        return '\\textrm{%s}(%s)' % (o.function_def.funcname.replace("_",r"\_"), ','.join(p))

    @include_id_in_overbrace
    def VisitFunctionDefBuiltInInstantiation(self, o, **kwargs):
        p = [self.visit(p) for p in o.parameters.values()]
        return '\\textrm{%s}(%s)' % (o.function_def.funcname.replace("_",r"\_"), ','.join(p))

    def VisitRandomVariable(self, o, **kwargs):
        return 'RANDOMVARIBLE'


    def VisitFunctionDefInstantiationParameter(self, o, **kwargs):
        rhs = self.visit(o.rhs_ast)
        if o.symbol is not None:
            return '%s=%s' % (o.symbol, rhs)
        else:
            return '%s' % rhs

    def VisitIfThenElse(self, o, **kwargs):
        s_if_true = self.visit(o.if_true_ast)
        s_if_false = self.visit(o.if_false_ast)
        s_predicate = self.visit(o.predicate)
        return r""" \begin{cases} %s & if %s \\ %s & otherwise \end{cases}""" \
            % (s_if_true, s_predicate, s_if_false)

    def VisitInEquality(self, o, **kwargs):
        return '%s < %s' % (self.visit(o.lesser_than),
                            self.visit(o.greater_than))


def build_figures(component):
    plots = {}

    # Find all assignments only dependant on 1 supplied values and parameters:

    for a in component.assignedvalues:
        all_deps = component.getSymbolDependancicesIndirect(a,
                include_ass_in_output=False)
        deps_sup = [d for d in all_deps if isinstance(d, (SuppliedValue,TimeVariable))]
        deps_params = [d for d in all_deps if isinstance(d, Parameter)]
        deps_state = [d for d in all_deps if isinstance(d,
                      StateVariable)]
        deps_reduce_ports = [d for d in all_deps if isinstance(d, AnalogReducePort)]
        assert len(deps_sup + deps_params + deps_state + deps_reduce_ports) == len(all_deps)

        # Ignore anything deopendant on state variables:

        if len(deps_state) != 0:
            continue

        # We can't be dependant on parameters:

        if len(deps_params) != 0:
            continue

        if len(deps_sup) == 1:
            sup = deps_sup[0]
            meta = component.getSymbolMetadata(sup)
            if not meta:
                continue

            print meta


            if not 'mf' in meta or not 'role' in meta['mf']:
                continue
            role = meta['mf']['role']


            if role != 'MEMBRANEVOLTAGE':
                continue

            F = FunctorGenerator()
            F.visit(component)

            f = F.assignment_evaluators[a.symbol]

            try:
                vVals = [-80, -70, -60, -40, -20, 0, 20, 40]
                vVals = np.linspace(-80, 50, 22) #* pq.milli * pq.volt
                oUnit = None
                fOut = []
                for v in vVals:
                    from neurounits.neurounitparser import NeuroUnitParser
                    vUnit = NeuroUnitParser.QuantitySimple('%f mV' % v)
                    vRes = f(V=vUnit, v=vUnit)
                    if oUnit is None:
                        oUnit = vRes.unit
                    assert vRes.unit == oUnit
                    fOut.append(vRes.magnitude)
            except ZeroDivisionError:
                color = 'r'
                import pylab
                f = pylab.figure(figsize=(2, 2))
                ax = f.add_subplot(1, 1, 1)
                ax.plot(vVals, vVals, color=color)
                f.suptitle('ERROR PLOTTING: Graph of %s against %s ' % (a.symbol, 'V' ))
                ax.set_xlabel('Membrane Voltage (mV)')
                ax.set_ylabel('%s (%s)' % (a.symbol, oUnit))
                ax.grid('on')
                plots[a.symbol] = f
            else:

                color = 'b'
                import pylab
                f = pylab.figure(figsize=(2, 2))
                ax = f.add_subplot(1, 1, 1)
                ax.plot(vVals, fOut, color=color)
                f.suptitle('Graph of %s against V' % a.symbol)
                ax.set_xlabel('Membrane Voltage (mV)')
                dim = FormatDimensionality(oUnit)
                ax.set_ylabel('%s (%s)' % (a.symbol, '$%s$'%dim if dim.strip() else ''))
                ax.grid('on')
                plots[a.symbol] = f

    # Build figure groups based on the first term:

    if len(plots) <= 3:
        imgs = [Image(f) for f in sorted(plots.values())]
        F = Figure(caption='Plots for channel', *imgs)
        return [F]


    states = set([k.split('_')[0] for k in plots.keys()])

    img_sets = []
    for s in states:
        vs = [(k, v) for (k, v) in plots.iteritems() if k.split('_')[0] == s]
        imgs = [Image(f[1]) for f in sorted(vs)]
        img_sets.append((imgs, s))




    ps = [ Figure(caption='State:%s' % state, *imgs) for (imgs, state) in img_sets]
    return ps







class MRedocWriterVisitor(ASTVisitorBase):

    @classmethod
    def build(self, obj):
        writer = MRedocWriterVisitor()
        return writer.visit(obj)


    def VisitLibraryManager(self, library_manager):
        local_redocs = []
        for block in library_manager.components + library_manager.libraries:
            redoc = MRedocWriterVisitor.build(block)
            local_redocs.append(redoc)

        title = 'LibraryManager Context'
        if library_manager.name:
            title += ': %s' % library_manager.name
        if library_manager.src_text:
            p = Section('Source',
                        VerbatimBlock(library_manager.src_text))
            local_redocs = [p] + local_redocs


        # Check here;
        d = Section(title, local_redocs)
        return d


    def VisitInterface(self, interface, **kwargs):
        connections = VerticalColTable("Symbol  | Type    | Value  | Dimensions | Dependancies | Metadata",
                                      ["$%s$    | -       | -      | -          | -            | -       " % (p.symbol,) for p in interface.connections]  
                                      )
        
        return HierachyScope(
            "Summary of '%s'" % interface.name,
            Section('Connections', 
                connections
                )
            )



    def VisitNineMLComponent(self, component):

        format_dim = lambda o: ('$%s$'
                                % FormatDimensionality(o.get_dimension()) if not o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False) else '-'
                                )

        f = LatexEqnWriterN()  # FormatTerminalSymbol(self, symbol):
        symbol_format = lambda s: f.FormatTerminalSymbol(s)

        dep_string_indir = lambda s: ','.join([symbol_format(o.symbol)
                for o in
                sorted(set(component.getSymbolDependancicesIndirect(s,
                include_ass_in_output=False)), key=lambda s: s.symbol)])

        meta_format = lambda s: component.getSymbolMetadata(s) or '-'


        terminal_symbols = VerticalColTable("Symbol  | Type      | Value | Dimensions | Dependancies | Metadata",
                                            ["$%s$     | Param | -     | %s         | -            | %s  " % (symbol_format(p.symbol), format_dim(p), meta_format(p)) for p in component.parameters] +
                                            ["$%s$     | Supp  | -     | %s         | -            | %s  " % (symbol_format(s.symbol), format_dim(s),meta_format(s) )  for s in component.suppliedvalues] +
                                            ["$%s$     | Const | %s    | %s         | -            | -   " % (symbol_format(s.symbol), s.value, format_dim(s),    ) for s in component.symbolicconstants] +
                                            ["$%s$     | Assd  | -     | %s         | $\{%s\}$     | %s  " % (symbol_format(a.symbol), format_dim(a), dep_string_indir(a), meta_format(a)   ) for a in component.assignedvalues] +
                                            ["$%s$     | State | -     | %s         | $\{%s\}$     | %s  " % (symbol_format(s.symbol), format_dim(s), dep_string_indir(s), meta_format(s)  ) for s in component.state_variables]
                                            )

        terminal_symbols = Section('TODO')

        plts = build_figures( component)
        return HierachyScope(
            "Summary of '%s'" % component.name,
            Section('Assignments',
                    EquationBlock(*[LatexEqnWriterN().visit(a) for a in
                    sorted(component.assignments, key=lambda a: \
                    a.lhs.symbol)])),
            Section('State Variable Evolution',
                    EquationBlock(*[LatexEqnWriterN().visit(a) for a in
                    component.timederivatives])),
            Section('Function Definitions',
                    EquationBlock(*[LatexEqnWriterN().visit(a) for a in
                    component.functiondefs if not isinstance(a,
                    FunctionDefBuiltIn)])),
            Section('Symbols', terminal_symbols),
            Section('Imports'),
            #Section('Events',
            #        EquationBlock(*[LatexEqnWriterN().visit(a) for a in
            #        component.onevents])),
            Section('Plots', *plts),
            )

    def VisitLibrary(self, library):

        format_dim = lambda o: "$%s$"%FormatDimensionality( o.get_dimension() ) if not o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False) else  "-"

        # symbol_format = lambda s:s

        # dep_string_indir = lambda s: ",".join( [symbol_format(o.symbol) for o in sorted( set(component.getSymbolDependancicesIndirect(s, include_ass_in_output=False)), key=lambda s:s.symbol ) ] )

        # meta_format = lambda s: component.getSymbolMetadata(s) or "-"
        # plts = build_figures( component)

        return SectionNewPage('Library Summary: %s' % library.name,
                              Section('Imports'),
                              Section('Function Definitions',
                              EquationBlock(*[LatexEqnWriterN().visit(a) for a in library.functiondefs if not isinstance(a, FunctionDefBuiltIn)])),
                              #Section('Symbols', terminal_symbols)
                              )


