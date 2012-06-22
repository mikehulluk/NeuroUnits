from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing
from neurounits.visitors.bases.base_actioner import SingleVisitPredicate
from neurounits.visitors.bases.base_visitor import ASTVisitorBase
from neurounits.unit_errors import panic
from neurounits.tools.nmodl.neuron_constants import NeuronSuppliedValues
from neurounits.visitors.common.ast_symbol_dependancies import VisitorFindDirectSymbolDependance
from neurounits.ast.astobjects import AssignedVariable, StateVariable,\
    SymbolicConstant, SuppliedValue, InEquality, Parameter
import string



class ModFileString(object):
    @classmethod
    def DeclareSymbol(self, p,build_parameters):
        unit = build_parameters.symbol_units[p]
        return "%s    ? (Units: %s %s )"%(p.symbol, unit.powerTen, str(type(unit)) )


class ParameterWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionParameter(self, n, modfilecontents,  build_parameters, **kwargs):
        modfilecontents.section_PARAMETER.append( ModFileString.DeclareSymbol(n,build_parameters) )


class StateWriter(ASTActionerDefaultIgnoreMissing):

    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ])

    def ActionStateVariable(self, n, modfilecontents,  build_parameters, **kwargs):
        modfilecontents.section_STATE.append( ModFileString.DeclareSymbol(n,build_parameters) )

    def ActionEqnTimeDerivative(self, n, modfilecontents, build_parameters, **kwargs):
        s = CStringWriter.Build(n, build_parameters=build_parameters, expand_assignments=False)
        modfilecontents.section_DERIVATIVE.append( s )

    def ActionEqnSet(self, n, modfilecontents,  build_parameters, **kwargs):

        # A slightly hacky way of writing out the initial conditions:
        # TODO: FIX THIS!

        for ic in n.initial_conditions:
            o1 = n.get_terminal_obj(ic.symbol)
            o2 = n.get_terminal_obj(ic.value)
            print "o1", ic.symbol, build_parameters.symbol_units[o1]
            print "o2", ic.value, build_parameters.symbol_units[o2]
            assert build_parameters.symbol_units[o1] == build_parameters.symbol_units[o2]

            s = "%s = %s"%(ic.symbol, ic.value)
            modfilecontents.section_INITIAL.append( s )





class SuppliedValuesWriter(ASTActionerDefaultIgnoreMissing):



    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def ActionSuppliedValue(self, n, modfilecontents, build_parameters,  **kwargs):
        #from neuron_constants import NeuronSuppliedValues

        # Sanity Check;
        assert n in build_parameters.supplied_values,  " Can't find %s in supplied values[%s]"%(n.symbol,  ",".join([s.symbol for s in build_parameters.supplied_values]) )

        what = build_parameters.supplied_values[n]

        if what == NeuronSuppliedValues.MembraneVoltage:
            modfilecontents.section_ASSIGNED.append( 'v (millivolt)')
        elif what == NeuronSuppliedValues.Temperature:
            modfilecontents.section_ASSIGNED.append( 'celsius (degC)')
        else:
            assert False





class ConstantWriter(ASTActionerDefaultIgnoreMissing):

    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])




def unique( seq ):
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add( item )
            yield item



class AssignmentWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self,action_predicates=[ SingleVisitPredicate() ])

    def VisitEqnSet(self, eqnset, modfilecontents,  build_parameters, **kwargs):
        self.assigment_statements = {}
        ASTActionerDefaultIgnoreMissing.VisitEqnSet(self,eqnset,modfilecontents=modfilecontents, build_parameters=build_parameters, **kwargs)


        # The order of writing out assignments is important. There are 3 phases,
        # 1. Initialisation
        # 2. Pre-State Solving
        # 3. Post-State Solving

        # At this stage, we assume that there are no assignments dependant on states depending on
        # further assignments. This can be resolved, but I have not done so here....


        # 1. Initialisation:
        # We perform all assignments in order:
        assignments_ordered = VisitorFindDirectSymbolDependance.get_assignment_dependancy_ordering( eqnset)
        for ass in assignments_ordered:
            modfilecontents.section_INITIAL.append( self.assigment_statements[ass] )

        # 2. Find which assignments are used by the states:

        required_assignments = []
        dependancies = VisitorFindDirectSymbolDependance()
        dependancies.VisitEqnSet(eqnset)

        for s in eqnset.timederivatives:
            ass_deps = [d for d in dependancies.dependancies[s] if not isinstance(d, StateVariable) ]
            required_assignments.extend( ass_deps)


        all_deps = []
        for i in required_assignments:
            a = VisitorFindDirectSymbolDependance().get_assignment_dependancy_ordering_recursive(eqnset=eqnset, ass=i)
            all_deps.extend(a)
            all_deps.append(i)

        for ass in unique(all_deps):
            unexpected_deps = [d for d in dependancies.dependancies[ass] if not isinstance(d, (AssignedVariable, SymbolicConstant, SuppliedValue, Parameter)) ]
            print unexpected_deps
            print 'Unexpected:', [s.symbol for s in unexpected_deps]

            assert not unexpected_deps, "Resolution of dependances in Neurounits can't support assignments need by timeerivatives which are dependanct on state variables (%s)"%(unexpected_deps)
            modfilecontents.section_BREAKPOINT_pre_solve.append( self.assigment_statements[ass] )



        # 3. Find the dependancies of the current variables:
        all_deps = []
        for c in build_parameters.currents:
            a = VisitorFindDirectSymbolDependance().get_assignment_dependancy_ordering_recursive(eqnset=eqnset, ass=c)
            all_deps.extend(a)
            all_deps.append(c)


        for ass in unique(all_deps):
            modfilecontents.section_BREAKPOINT_post_solve.append( self.assigment_statements[ass] )





    def ActionEqnAssignment(self, n, modfilecontents,  build_parameters, **kwargs):
        s = CStringWriter.Build(n, build_parameters=build_parameters, expand_assignments=False)
        self.assigment_statements[n.lhs] = s



    def ActionAssignedVariable(self, n, modfilecontents, build_parameters,  **kwargs):
        modfilecontents.section_ASSIGNED.append( ModFileString.DeclareSymbol(n,build_parameters)   )







class FunctionWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self,):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionFunctionDef(self, o, modfilecontents,  build_parameters,**kwargs):
        if o.funcname in ['exp','sin','fabs','pow']:
            return False

        func_def_tmpl = """
            FUNCTION $func_name ($func_params) $func_unit
            {
                $func_name = $result_string
            }"""

        func_def = string.Template(func_def_tmpl).substitute( {'func_name' :  o.funcname.replace(".","__"),
                                                               'func_params' : ",".join( [ p.symbol for p in o.parameters.values()] ),
                                                               'result_string' : CStringWriter.Build(o.rhs, build_parameters=build_parameters, expand_assignments=False  ),
                                                               'func_unit' : "",
                                                                }  )
        modfilecontents.section_FUNCTIONS.append(func_def)




class OnEventWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self,):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionOnEvent(self, o, modfilecontents, build_parameters,  **kwargs):
        if o != build_parameters.event_function:
            return

        # No Arguments:
        assert len( o.parameters ) == 0
        tmpl = """NET_RECEIVE( weight ) \n {    $contents \n}"""

        contents = "\n".join( [ "" + self.ActionOnEventAssignment(a, modfilecontents=modfilecontents, build_parameters=build_parameters, **kwargs ) for a in o.actions ] )
        txt = string.Template( tmpl).substitute( contents=contents)
        modfilecontents.section_NETRECEIVES.append(txt)

    def ActionOnEventAssignment(self, o, modfilecontents, build_parameters, **kwargs):
        return CStringWriter.Build(o, build_parameters=build_parameters, expand_assignments=False)







class NeuronBlockWriter(object):
    def __init__(self,  eqnset,  build_parameters,  modfilecontents):
        from neuron_constants import MechanismType#,NEURONMappings
        # Heading
        if build_parameters.mechanismtype == MechanismType.Point:
            modfilecontents.section_NEURON.append("POINT_PROCESS %s"%build_parameters.suffix )
        elif build_parameters.mechanismtype == MechanismType.Distributed:
            modfilecontents.section_NEURON.append("SUFFIX %s"%build_parameters.suffix )
        else:
            assert False


        #current_unit_in_nrn = NEURONMappings.current_units[build_parameters.mechanismtype]
        # Currents:
        for currentSymbol, neuronCurrentObj in build_parameters.currents.iteritems():
            modfilecontents.section_NEURON.append("NONSPECIFIC_CURRENT %s"%currentSymbol.symbol )
            #modfilecontents.section_ASSIGNED.append("%s (%s)"%(currentSymbol.symbol, current_unit_in_nrn ) )




class NeuronInterfaceWriter(ASTActionerDefaultIgnoreMissing):
    def __init__(self, ):
        ASTActionerDefaultIgnoreMissing.__init__(self, action_predicates=[ SingleVisitPredicate() ] )

    def ActionAssignedVariable(self, n, modfilecontents,build_parameters, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )

    def ActionStateVariable(self, n, modfilecontents, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )

    def ActionParameter(self, n, modfilecontents, **kwargs):
        modfilecontents.section_NEURON.append("RANGE %s"%(n.symbol) )














class CStringWriter(ASTVisitorBase):

    def __init__(self, build_parameters, expand_assignments):
        ASTVisitorBase.__init__(self,)
        self.build_parameters = build_parameters
        self.expand_assignments =expand_assignments


    @classmethod
    def Build (self, lhs, build_parameters, expand_assignments):
        c = CStringWriter(build_parameters = build_parameters,expand_assignments=expand_assignments)
        return c.visit(lhs)

    def VisitIfThenElse(self, o, **kwargs):
        assert isinstance( o.predicate, InEquality), "Only simple if supported"
        return """ifthenelse( %s, %s, %s, %s)"""%( 
                self.visit(o.predicate.less_than),
                self.visit(o.predicate.greater_than),
                self.visit(o.if_true_ast), 
                self.visit(o.if_false_ast) )
        #raise NotImplementedError()
    def VisitInEquality(self, o,**kwargs):
        return "%s < %s"%( self.visit(o.less_than), self.visit(o.greater_than))

    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()

    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        panic()

    def VisitBuiltInFunction(self, o, **kwargs):
        raise NotImplementedError()

    def VisitFunctionDefParameter(self, o, **kwargs):
        return self.GetTerminal(o)


    def GetTerminal(self, n):

        symbol = n.symbol
        if n in self.build_parameters.supplied_values:
            if self.build_parameters.supplied_values[n] is NeuronSuppliedValues.MembraneVoltage:
                symbol = 'v'

        # Term should be in base SI units:
        print n.symbol, type(n)
        #print "Symbols:", [ s.symbol for s in self.build_parameters.symbol_units.keys() ]

        if n.get_dimensionality() == self.build_parameters.symbol_units[n]:
            return symbol

        else:
            multiplier = "(%e)"% 10**self.build_parameters.symbol_units[n].powerTen
            return "%s * %s"%(multiplier, symbol)


    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return self.GetTerminal(o)
    def VisitParameter(self, o, **kwargs):
        return self.GetTerminal(o)
    def VisitAssignedVariable(self, o, **kwargs):
        if not self.expand_assignments:
            return self.GetTerminal(o)
        else:
            return self.visit( o.assignment_rhs )

    def VisitSuppliedValue(self, o, **kwargs):
        return self.GetTerminal(o)


    def VisitConstant(self, o, **kwargs):
        return "%e"% o.value.float_in_si()

    def VisitSymbolicConstant(self,o , **kwargs):
        return "%e"%o.value.float_in_si()



    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        # NEURON has a dt in 'ms', so we need to scale from SI.
        return "%s' = (0.001)* %s %s" %( lhs, multiplier, rhs_si )


    def VisitEqnAssignment(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        return "%s = %s %s" %( lhs, multiplier, rhs_si )


    def VisitOnEventStateAssignment(self, o, **kwargs):
        rhs_si =  self.visit(o.rhs)
        lhs =  o.lhs.symbol

        # Check for non-SI assignments to the lhs
        multiplier = ""
        if o.lhs.get_dimensionality() != self.build_parameters.symbol_units[o.lhs]:
            multiplier = "(%e)*"% 10**(-1*self.build_parameters.symbol_units[o.lhs].powerTen)

        return "%s = %s %s" %( lhs, multiplier, rhs_si )



    def VisitAddOp(self, o, **kwargs):
        return "( %s + %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitSubOp(self, o,  **kwargs):
        return "( %s - %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitMulOp(self, o, **kwargs):
        return "( %s * %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitDivOp(self, o, **kwargs):
        return "( %s / %s )"%( self.visit(o.lhs,**kwargs), self.visit(o.rhs, **kwargs) )

    def VisitExpOp(self, o, **kwargs):
        return "((%s)^%s )"%( self.visit(o.lhs,**kwargs), o.rhs )

    def VisitFunctionDefInstantiation(self, o, **kwargs):
        import neurounits
        if type(o.function_def) == neurounits.ast.astobjects.BuiltInFunction:

            if o.function_def.funcname == "pow":
                p0_rhs = self.visit(o.parameters['base'].rhs_ast)
                p1_rhs = self.visit(o.parameters['exp'].rhs_ast)
                r = "%s(%s,%s)"%( o.function_def.funcname, p0_rhs, p1_rhs  )
                return r

            else:
                assert len(o.parameters) == 1
                p0_rhs = self.visit(o.parameters.values()[0].rhs_ast)
                r = "%s(%s)"%( o.function_def.funcname, p0_rhs )
                return r
        elif type(o.function_def) == neurounits.ast.astobjects.FunctionDef:
            #params = ",".join( self.visit(p.rhs_ast,varnames=varnames, varunits=varunits,**kwargs) for p in o.parameters.values()  )
            #func_call = "%s(%s)"%( varnames[o.function_def].raw_name, params)
            print 'T',  [ type(p.rhs_ast) for p in o.parameters.values()]
            params = ",".join( self.visit(p.rhs_ast) for p in o.parameters.values()  )
            func_call = "%s(%s)"%( o.function_def.funcname.replace(".","__"), params)
            return func_call
        else:
            panic()
    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        panic()
























