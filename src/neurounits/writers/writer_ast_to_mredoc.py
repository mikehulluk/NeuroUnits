
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
from neurounits.visitors import ASTVisitorBase
import os
from ..units_misc import IterateDictValueByKeySorted
import string
from mredoc import Table, VerticalColTable, Figure, Image, SectionNewPage
from neurounits.ast.astobjects import SuppliedValue
from neurounits.ast.astobjects import Parameter, StateVariable
from neurounits.writers.writer_ast_to_simulatable_object import FunctorGenerator


import pylab


from mredoc import *
from neurounits.ast import BuiltInFunction







def get_prefered_dimensions():
    from .. import NeuroUnitParser
    prefered_dimension_dims = [
                 (NeuroUnitParser.Unit("S"), 'S'),
                 (NeuroUnitParser.Unit("V"), 'V'),
                 (NeuroUnitParser.Unit("A"), 'A'),
                 (NeuroUnitParser.Unit("S/m2"), 'S/m2'),
                 (NeuroUnitParser.Unit("A/m2"), 'A/m2'),

                 (NeuroUnitParser.Unit("mV"), 'mV'),
                 (NeuroUnitParser.Unit("ms"), 'ms'),
                 (NeuroUnitParser.Unit("ms-1"), 'ms^{-1}'),
                 (NeuroUnitParser.Unit("K"), 'K'),

                 ]
    return prefered_dimension_dims




def FormatDimensionality(dim):
    for unit,symbol in get_prefered_dimensions():
        if dim == unit:
            return symbol
    return dim.FormatLatex()







class LatexEqnWriterN(ASTVisitorBase):

    def FormatTerminalSymbol(self, symbol):
        symbol_components = symbol.split("_")
        subscripts = symbol_components[1:]

        if subscripts:
            symbol = "%s_{%s}"%( symbol_components[0], ",".join(subscripts) )


        return r"""\boldsymbol{%s}"""%symbol.replace("alpha",r"\alpha").replace("beta",r"\beta").replace("inf",r"\infty").replace("tau",r"\tau")
        return r"""\boldsymbol{%s}"""%symbol



    def FormatInlineConstant(self, val):
        if val.is_dimensionless(allow_non_zero_power_of_ten=False):
            return str(val.magnitude)
        elif val.is_dimensionless(allow_non_zero_power_of_ten=True):
            return "%fe%d"%(str(val.magnitude), val.unit.powerTen)

        else:
            dim_str = FormatDimensionality(val.unit)
            return r"\langle %s ~ \mathrm{%s} \rangle"% (str(val.magnitude), dim_str )




    # High Level Display:
    def VisitEqnAssignment(self, o, **kwargs):
        return Equation("%s&=%s"%( self.Visit(o.lhs), self.Visit(o.rhs) ) )


    def VisitEqnTimeDerivative(self, o, **kwargs):
        return Equation(r"""\frac{d}{dt}%s &= %s""" % (self.Visit(o.lhs), self.Visit(o.rhs),))

    def VisitOnEvent(self, o, **kwargs):
        ev_name = o.name.replace("_","\\_")
                
        tr = "%s(%s) \\rightarrow "%(ev_name, ",".join(o.parameters.keys()) ) #
        evts = "\\begin{cases}" + r"\\".join( [self.Visit(a) for a in o.actions] ) + "\\end{cases}"
        return  Equation( tr + evts )

    def VisitOnEventStateAssignment(self, o, **kwargs):
        return "%s = %s"%(self.Visit(o.lhs),self.Visit(o.rhs) )

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        return  Equation("%s(%s) \\rightarrow %s"%(o.funcname, ",".join(o.parameters.keys()), self.Visit(o.rhs)) )

    def VisitFunctionDefParameter(self, o, **kwargs):
        return "\mathit{%s}"%o.symbol.replace("_","\\_")


    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitParameter(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitConstant(self, o, **kwargs):
        return self.FormatInlineConstant(o.value)

    def VisitAssignedVariable(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitSuppliedValue(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)

    def VisitSymbolicConstant(self, o, **kwargs):
        return self.FormatTerminalSymbol(o.symbol)


    # AST Nodes:
    def VisitAddOp(self, o, **kwargs):
        return '(%s + %s)'%( self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitSubOp(self, o, **kwargs):
        return '(%s - %s)'%( self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitMulOp(self, o, **kwargs):
        return '%s \cdot %s'%( self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitDivOp(self, o, **kwargs):
        return '\dfrac{%s}{%s}'%( self.Visit(o.lhs), self.Visit(o.rhs) )

    def VisitExpOp(self, o, **kwargs):
        return '%s ^{ %s }'%( self.Visit(o.lhs), o.rhs )


    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
        return '(%s && %s)'%( self.Visit(o.lhs), self.Visit(o.rhs) )
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
        return '(%s || %s)'%( self.Visit(o.lhs), self.Visit(o.rhs) )
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()
        return '(! %s)'%( self.Visit(o.lhs) )


    def VisitFunctionDefInstantiation(self, o, **kwargs):
        p = [ self.Visit(p) for p in o.parameters.values() ]
        return "\\textrm{%s}(%s)"%(o.function_def.funcname, ",".join(p))

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        rhs = self.Visit(o.rhs_ast)
        if o.symbol is not None:
            return "%s=%s"%(o.symbol, rhs)
        else:
            return "%s"%( rhs)


    def VisitIfThenElse(self,o,**kwargs):
        s_if_true = self.Visit(o.if_true_ast)
        s_if_false = self.Visit(o.if_false_ast)
        s_predicate = self.Visit(o.predicate)
        return r""" \begin{cases} %s & if %s \\ %s & otherwise \end{cases}"""%(s_if_true, s_predicate, s_if_false)

    def VisitInEquality(self,o,**kwargs):
        return "%s < %s" %(self.Visit(o.less_than),self.Visit(o.greater_than) )







def build_figures(eqnset):
    plots = {}
    # Find all assignments only dependant on 1 supplied values and parameters:
    for a in eqnset.assignedvalues:
        all_deps = eqnset.getSymbolDependancicesIndirect(a,include_ass_in_output=False)
        deps_sup = [ d for d in all_deps if isinstance(d, SuppliedValue)]
        deps_params = [ d for d in all_deps if isinstance(d, Parameter)]
        deps_state = [ d for d in all_deps if isinstance(d, StateVariable)]
        assert len(deps_sup + deps_params + deps_state) == len(all_deps)

        # Ignore anything deopendant on state variables:
        if len(deps_state) != 0:
            continue

        # We can't be dependant on parameters:
        if len(deps_params) != 0:
            continue

        if len(deps_sup) == 1:
            sup = deps_sup[0]
            meta = eqnset.getSymbolMetadata(sup)
            if not meta: continue
            print meta
            if not 'mf' in meta or not 'role' in meta['mf']:
                continue
            role = meta['mf']['role']
            print role

            if role != 'MEMBRANEVOLTAGE':
                continue
            print "sup.symbol", sup.symbol

            F = FunctorGenerator()
            F.Visit(eqnset)

            f = F.assignment_evaluators[a.symbol]


            try:
                print f
                vVals = [-80, -70, -60, -40, -20, 0, 20, 40]
                vVals = range(-80, 50, 10)
                oUnit = None
                fOut = []
                for v in vVals:
                    from neurounits.neurounitparser import NeuroUnitParser
                    vUnit = NeuroUnitParser.QuantitySimple("%f mV"%v)
                    vRes = f(V=vUnit, v=vUnit)
                    if oUnit is None:
                        oUnit = vRes.unit
                    assert vRes.unit == oUnit
                    fOut.append(vRes.magnitude)
            except ZeroDivisionError:
                color='r'
                f = pylab.figure( figsize=(2,2))
                ax = f.add_subplot(1,1,1)
                ax.plot(vVals, vVals,color=color)
                f.suptitle("ERROR PLOTTING: Graph of %s"%a.symbol)
                ax.set_xlabel("Membrane Voltage (mV)")
                ax.set_ylabel("%s (%s)"%(a.symbol, oUnit) )
                plots[a.symbol] = f

            else:
                color="b"
                f = pylab.figure(figsize=(2,2))
                ax = f.add_subplot(1,1,1)
                ax.plot(vVals, fOut,)
                f.suptitle("Graph of %s"%a.symbol)
                ax.set_xlabel("Membrane Voltage (mV)")
                ax.set_ylabel("%s ($%s$)"%(a.symbol, FormatDimensionality(oUnit))  )
                plots[a.symbol] = f


    # Build figure groups based on the first term:
    if len(plots) <=3:
        imgs= [ ImageMPL(f) for f in sorted(plots.values())]
        F = Figure( *imgs, caption="jkl")
        return [F]


    ps = []
    states = set( [ k.split("_")[0] for k in plots.keys() ] )
    for s in states:
        vs = [(k,v) for (k,v) in plots.iteritems() if k.split("_")[0] == s ]
        imgs= [ ImageMPL(f[1]) for f in sorted(vs)]
        F = Figure( *imgs, caption="State:%s"%s)
        ps.append(F)

    return ps







class MRedocWriterVisitor(ASTVisitorBase):

    @classmethod
    def build(self, eqnset):
        writer = MRedocWriterVisitor()
        return writer.Visit(eqnset)


    def VisitLibraryManager(self, library_manager):
        local_redocs = []
        for block in library_manager.eqnsets + library_manager.libraries:
            redoc = MRedocWriterVisitor.build(block)
            local_redocs.append( redoc)

        title = "LibraryManager Context"
        if library_manager.name:
            title += ": %s"%library_manager.name
        if library_manager.src_text:
            p = Section('Source', VerbatimBlock(library_manager.src_text))
            local_redocs = [p] + local_redocs

        d = SectionNewPage(title, local_redocs)
        return d



    def VisitEqnSet(self, eqnset):

        format_dim = lambda o: "$%s$"%FormatDimensionality( o.get_dimension() ) if not o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False) else  "-"

        f = LatexEqnWriterN() #FormatTerminalSymbol(self, symbol):
        symbol_format = lambda s:f.FormatTerminalSymbol(s)

        dep_string_indir = lambda s: ",".join( [symbol_format(o.symbol) for o in sorted( set(eqnset.getSymbolDependancicesIndirect(s, include_ass_in_output=False)), key=lambda s:s.symbol ) ] )

        meta_format = lambda s: eqnset.getSymbolMetadata(s) or "-"


        terminal_symbols = VerticalColTable("Symbol  | Type      | Value | Dimensions | Dependancies | Metadata",
                                            ["$%s$     | Param | -     | %s         | -            | %s  " % (symbol_format(p.symbol), format_dim(p), meta_format(p)) for p in eqnset.parameters] +
                                            ["$%s$     | Supp  | -     | %s         | -            | %s  " % (symbol_format(s.symbol), format_dim(s),meta_format(s) )  for s in eqnset.suppliedvalues] +
                                            ["$%s$     | Const | %s    | %s         | -            | -   " % (symbol_format(s.symbol), s.value, format_dim(s),    ) for s in eqnset.symbolicconstants] +
                                            ["$%s$     | Assd  | -     | %s         | $\{%s\}$     | %s  " % (symbol_format(a.symbol), format_dim(a), dep_string_indir(a), meta_format(a)   ) for a in eqnset.assignedvalues] +
                                            ["$%s$     | State | -     | %s         | $\{%s\}$     | %s  " % (symbol_format(s.symbol), format_dim(s), dep_string_indir(s), meta_format(s)  ) for s in eqnset.states]
                                            )




        plts = build_figures( eqnset)

        return SectionNewPage("Eqnset Summary: %s"%eqnset.name,
                    Section("Assignments",
                       EquationBlock( *[LatexEqnWriterN().Visit(a) for a in sorted( eqnset.assignments, key=lambda a:a.lhs.symbol)])),
                    Section("State Variable Evolution",
                       EquationBlock( *[LatexEqnWriterN().Visit(a) for a in eqnset.timederivatives])),
                    Section("Function Definitions",
                       EquationBlock( *[LatexEqnWriterN().Visit(a) for a in eqnset.functiondefs if not isinstance(a, BuiltInFunction)])),
                    Section("Symbols", terminal_symbols),
                    Section("Imports"),
                    Section("Events",
                       EquationBlock( *[LatexEqnWriterN().Visit(a) for a in eqnset.onevents])),
                    Section("Plots", *plts ),
                    )

    def VisitLibrary(self, library):

        format_dim = lambda o: "$%s$"%FormatDimensionality( o.get_dimension() ) if not o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False) else  "-"

        #symbol_format = lambda s:s

        #dep_string_indir = lambda s: ",".join( [symbol_format(o.symbol) for o in sorted( set(eqnset.getSymbolDependancicesIndirect(s, include_ass_in_output=False)), key=lambda s:s.symbol ) ] )

        #meta_format = lambda s: eqnset.getSymbolMetadata(s) or "-"
        #plts = build_figures( eqnset)


        terminal_symbols = VerticalColTable("Symbol  | Type      | Value | Dimensions | Dependancies | Metadata",
                                            ["%s     | Constant  | %s    | %s         | -            | -   " % (s.symbol, s.value, format_dim(s),    ) for s in eqnset.symbolicconstants]
                                            )





        return SectionNewPage("Library Summary: %s"%library.name,
                    Section("Imports"),
                    Section("Function Definitions",
                       EquationBlock( *[LatexEqnWriterN().Visit(a) for a in eqnset.functiondefs if not isinstance(a, BuiltInFunction)])),
                    Section("Symbols", terminal_symbols),
                    )


