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






latex_skeleton = r"""
\documentclass[11pt,a4paper]{article}
\usepackage{amsmath}
\usepackage[margin=0.5in]{geometry}
\begin{document}

\section{Summary of $eqnsetname}


\subsection{Constants}
$constants

\subsection{Parameters}
$parameters

\subsection{Supplied Values}
$supplied_values


\subsection{Assignments:}
$assignment_block

    
\subsection{State Variables:}
$state_variables



\subsection{Function Defs:}
$function_defs

\subsection{On Events:}
$onevent_block


\subsection{Verbatim}
\begin{verbatim}
$additional_verbatim
\end{verbatim}

\end{document}

"""


def get_prefered_dimensions():
    from .. import NeuroUnitParser
    prefered_dimension_dims = [
                 (NeuroUnitParser.Unit("S"), 'S'),
                 (NeuroUnitParser.Unit("V"), 'V'),
                 (NeuroUnitParser.Unit("S/m2"), 'S/m2'),
                 (NeuroUnitParser.Unit("A/m2"), 'A/m2'),
                 (NeuroUnitParser.Unit("A"), 'A'),
                 
                 #(NeuroUnitParser.Unit("mV"), 'mV'),
                 #(NeuroUnitParser.Unit("pS"), 'pS'),
                 #(NeuroUnitParser.Unit("s"), 's')
                 ]
    return prefered_dimension_dims




def FormatDimension(d ):
    assert d.powerTen==0
    return " < " + d.FormatLatex(inc_powerten=False) + " > "

    #from .. import NeuroUnitParser
    ##assert False
    #for udim,udimstr in get_prefered_dimensions():
    #    assert type(udim) == type(d), "Type: %s"%(type(d))
    #    if d==udim:
    #        assert False
    #        return r"\mathit{%s}"%(str(v) + r" \langle " + udimstr +r"  \rangle ")
    #print 'A',d
    #s = NeuroUnitParser.Unit("S/m2")
    #print 'B',s, type(s) 
    #print 'C'
    #assert False
    ## Otherwise, return the string:
    #return " < " + d.FormatLatex(inc_powerten=False) + " > "

    
    
#def FormatDimension(u):
#    return " < " + u.FormatLatex(inc_powerten=False) + " > "
    
    
def FormatConstant(c):
    
    if c.is_dimensionless(allow_non_zero_power_of_ten=False):
        return "%s"%str(c.magnitude)
 
    else:
        for udim,udimstr in get_prefered_dimensions():
            if c.is_compatible(udim):
                #print c, type(c)
                #assert False
                v = c.rescale(udim).magnitude
                return r"\mathit{%s}"%(str(v) + r" \langle " + udimstr +r"  \rangle ")
        return str(c)
   
def FormatVarname(c):
    return "\mathit{%s}"%c.replace("_","\\_")









def latex_string_replace(s):
    return s.replace("_","\_")





class LatexWriterVisitor(ASTVisitorBase):
    def __init__(self):
        print 'StringWriterVisitor'
        self.assignment_data = {}
        self.timederivative_data = {}
        self.parameter_data = {}
        self.constant_data = {}
        self.funcdef_data = {}
        
        self.suppliedvals_data = {}
        self.onevent_data = {}
        
        
        
        
        
        
        
    def buildLatex(self, ltx, output_filename,working_dir=None,):
        working_dir = working_dir or "/tmp"
        tex_file = working_dir + "/eqnset.tex"
        tex_pdf = working_dir + "/eqnset.pdf"
        # Write to disk and compile:
        with open(tex_file,'w') as f:
            f.write(ltx)
        os.system("pdflatex -output-directory %s %s"%(working_dir, tex_file))
        os.system("cp %s %s"%(tex_pdf,output_filename) )
        if not os.path.exists(output_filename):
            raise ValueError("Something went wrong building pdf")
        
        

    # AST Top Level:
    def VisitEqnSet(self, o,  output_filename,working_dir=None,additional_verbatim = None,**kwargs):
        print 'Building Latex:'
        print '----'
        
        for a in o.assignments:
            self.Visit(a)
        for a in o.timederivatives:
            self.Visit(a)
        for a in o.functiondefs:
            self.Visit(a)
        for a in o.on_events:
            self.Visit(a)

        self.eqnset = o
        
        # Build the Latex:
        ltx = self.getLatex(additional_verbatim=additional_verbatim)
        self.buildLatex( ltx, output_filename=output_filename,working_dir=working_dir)

        
    def getLatex(self,additional_verbatim ):
        
        assignments_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.assignment_data) ))
        timederivative_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.timederivative_data) ))
        constant_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.constant_data) ))
        funcdef_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.funcdef_data) ))
        
        parameters_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.parameter_data) ))
        supplied_values_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.suppliedvals_data) ))
        onevent_data = "  \\\\\n".join( list( IterateDictValueByKeySorted(self.onevent_data) ))




        tmpl = string.Template(latex_skeleton)
        
        def latexEqnBlock(s, environment='align*', options='',math_env=''): 
            s = s.replace("(", r"""\left(""").replace(")", r"""\right)""")
            return """%s\n\\begin{%s}%s\n%s\n\\end{%s}\n%s"""%(math_env,environment,options,s,environment,math_env)
        
        missing = "\\[ None  \\]"
        ltx = tmpl.substitute( {'assignment_block':     latexEqnBlock( assignments_data)    if assignments_data else missing,
                                'state_variables':      latexEqnBlock( timederivative_data) if timederivative_data else missing,
                                'constants':            latexEqnBlock( constant_data)       if constant_data else missing,
                                'function_defs':        latexEqnBlock( funcdef_data)        if funcdef_data else missing,
                                'parameters':           latexEqnBlock( parameters_data)        if parameters_data else missing,
                                'supplied_values':      latexEqnBlock( supplied_values_data)   if supplied_values_data else missing,
                                'onevent_block':        latexEqnBlock(onevent_data,'array',options='{ccc}',math_env='$$')   if onevent_data else missing,
                                'additional_verbatim': additional_verbatim if additional_verbatim else "",
                                'eqnsetname' :          latex_string_replace(self.eqnset.name)
                                } )
        return ltx


        
        
        
        
        
    def VisitOnEvent(self, o, **kwargs):
        for a in o.actions:
            self.Visit(a)

        actions = r"\\[6mm]".join( [self.Visit(a) for a in o.actions] )
        actions = r'\begin{array}{rll}' + actions + r"\end{array}"
        s = r"OnEvent: %s(%s) & \rightarrow  & %s"%(o.name, ",".join(o.parameters.keys()), actions )
        self.onevent_data[o.name] = s
        

    def VisitOnEventStateAssignment(self, o, **kwargs):
        rhs = self.Visit(o.rhs)
        lhs = FormatVarname(o.lhs.symbol)
        s = r"""\boldsymbol{%s} &= %s & %s""" % (lhs, rhs, FormatDimension(o.lhs.get_dimension()) )
        return s
        
        
        
    def VisitEqnAssignment(self, o, **kwargs):
        rhs = self.Visit(o.rhs)
        lhs = FormatVarname(o.lhs.symbol)
        s = r"""\boldsymbol{%s} &= %s & %s""" % (lhs, rhs, FormatDimension(o.lhs.get_dimension()) )
        self.assignment_data[o.lhs.symbol] = s
        
    def VisitEqnTimeDerivative(self, o, **kwargs):
        rhs = self.Visit(o.rhs)
        lhs = FormatVarname(o.lhs.symbol)
        s = r"""\frac{d}{dt}\boldsymbol{%s} &= %s & %s""" % (lhs, rhs, FormatDimension(o.lhs.get_dimension()),  )
        self.timederivative_data[o.lhs.symbol] = s


    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        s = "%s(%s) \\rightarrow %s"%(o.funcname, ",".join(o.parameters.keys()), self.Visit(o.rhs))
        self.funcdef_data[o.funcname] = s

    def VisitFunctionDefParameter(self, o, **kwargs):
        return FormatVarname(o.symbol)

    def VisitBuiltInFunction(self, o, **kwargs):
        return "\textrm{%s}"%o.funcname
    
    
    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return FormatVarname( o.symbol )
    
    def VisitParameter(self, o, **kwargs):
        self.parameter_data[o.symbol] = r"""\boldsymbol{%s} &  %s"""%(FormatVarname(o.symbol), FormatDimension(o.get_dimension()) )
        return FormatVarname(o.symbol)
    
    def VisitConstant(self, o, **kwargs):
        return FormatConstant(o.value)

    def VisitAssignedVariable(self, o, **kwargs):
        return FormatVarname( o.symbol )

    def VisitSuppliedValue(self, o, **kwargs):
        self.suppliedvals_data[o.symbol] = r"""\boldsymbol{%s} & %s"""%(FormatVarname(o.symbol), FormatDimension(o.get_dimension() ) )
        return FormatVarname(o.symbol)

    def VisitSymbolicConstant(self, o, **kwargs):
        self.constant_data[o.symbol] = r"""\boldsymbol{%s} & %s"""%(FormatVarname(o.symbol),FormatConstant(o.value) )
        return FormatVarname(o.symbol)


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
        raise NotImplementedError()
        return "[%s] if [%s] else [%s]" %(self.Visit(o.if_true_ast),
                                           self.Visit(o.predicate),
                                           self.Visit(o.if_false_ast) )
    def VisitInEquality(self,o,**kwargs):
        raise NotImplementedError()
        return "[%s < %s]" %(self.Visit(o.less_than),self.Visit(o.greater_than) )

