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
from neurounits.visitors import ASTVisitorBase,ASTActionerDefault
from neurounits import ast
from neurounits.visitors.common import ASTNodeLabels
from neurounits.units_misc import EnsureExisits
from neurounits.visitors.common import ActionerFormatStringsAsIDs
from neurounits.unit_errors import panic,UnitMismatchError
from neurounits.writers.writer_ast_to_str import StringWriterVisitor


class ASTVisitorCollectorAll(ASTActionerDefault):
    def __init__(self,eqnset,**kwargs):
        ASTActionerDefault.__init__(self,**kwargs)
        self.objects = set()
        self.Visit(eqnset)

    def ActionNode(self, o):
        self.objects.add(o)




class DimensionResolver(ASTVisitorBase):


    def EnsureEqualDimensions(self, args, reason=None):
        assigned_dimensions = [a for a in args if a.is_dimension_known()]

        # No dimensions known?
        if len(assigned_dimensions) == 0:
            return []

        u = assigned_dimensions[0]

        for au in assigned_dimensions[1:]:
            try:
                u.get_dimension().check_compatible( au.get_dimension() )
                u.get_dimension() == au.get_dimension()
            except UnitMismatchError, e:
                raise UnitMismatchError( unitA=u.get_dimension(), unitB=au.get_dimension(), objA=u, objB=au)
            #check_dimension_compatible(u, au)

        unassigned_dimensions = [a for a in args if not a.is_dimension_known() ]
        for au in unassigned_dimensions:
            print u, type(u)
            u.get_dimension()
            self.RegisterDimensionPropogation(obj=au, new_dimension=u.get_dimension(), reason=reason)
        return unassigned_dimensions











    # Visit each node, and try and propogate dimensions.
    # Each method should return a list of nodes resolved.

    def __init__(self, ast, obj_label_dict):
        self.ast = ast
        self.history = []
        self.obj_label_dict = obj_label_dict
        self.Initialise()

    def DumpUnitStateToHistoryAll(self):
        for obj, name in self.obj_label_dict.iteritems():
            if not isinstance(obj, ast.ASTExpressionObject):
                continue

            obj_dimensionality = obj.get_dimensionality() if obj.is_dimensionality_known() else "<Dimension Unknown>"
            obj_unit = obj.get_unitMH() if obj.is_unitMH_known() else "<Unit Unknown>"
            self.history.append(" %s -> Dim: %s Unit: %s"%(name, obj_dimensionality, obj_unit) )

    def DumpUnitStateToHistorySymbols(self):
        for obj, name in self.obj_label_dict.iteritems():
            if not isinstance(obj, ast.ASTExpressionObject):
                continue

            try:
                obj_dim = obj.get_dimension() if obj.is_dimension_known() else "<Dimension Unknown>"
                obj_unit = obj.get_unitMH() if obj.is_unit_known() else "<Unit Unknown>"
                self.history.append(" %s - %s - %s %s"%(name,obj.symbol, obj_dim, obj_unit) )
            except:
                pass

    def SummariseUnitState(self, title):
        if title is not None:
            self.history.append(title)

        self.history.append("Symbols:")
        self.DumpUnitStateToHistorySymbols()

        self.history.append("All:")
        self.DumpUnitStateToHistoryAll()
        self.history.append("")


    def Initialise(self):
        self.SummariseUnitState(title="Initially")


    def RegisterDimensionPropogation(self, obj, new_dimension, reason):
        obj.set_dimension(new_dimension)
        self.history.append("Setting Dimension: %s to %s because %s"%(self.obj_label_dict[obj],new_dimension,reason) )


    def VisitEqnSet(self, o, **kwargs):
        pass
    def VisitLibrary(self, o, **kwargs):
        pass


    def VisitOnEvent(self, o, **kwargs):
        return

    def VisitOnEventStateAssignment(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs] )

    def VisitIfThenElse(self, o, **kwargs):
        #assert False
        #print o.get_dimension()
        #print o.if_true_ast.is_dimensionality_known()
        #print o.if_false_ast.is_dimensionality_known()
        #print o.is_dimensionality_known()
        self.EnsureEqualDimensions([o, o.if_true_ast, o.if_false_ast] )

    def VisitInEquality(self, o ,**kwargs):
        self.EnsureEqualDimensions([o.less_than, o.greater_than] )

    def VisitBoolAnd(self, o, **kwargs):
        panic()

    def VisitBoolOr(self, o, **kwargs):
        panic()

    def VisitBoolNot(self, o, **kwargs):
        panic()




    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        return []

    def VisitParameter(self, o, **kwargs):
        return []

    def VisitConstant(self, o, **kwargs):
        return []

    def VisitAssignedVariable(self, o, **kwargs):
        return []

    def VisitSuppliedValue(self, o, **kwargs):
        return []

    def VisitSymbolicConstant(self, o, **kwargs):
        return []

    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        if len( [True for i in (o.lhs, o.rhs) if i.is_dimension_known()] ) != 1:
            return

        one_sec = self.ast.library_manager.backend.Unit(second=1)
        if o.lhs.is_dimension_known():
            self.RegisterDimensionPropogation( o.rhs, new_dimension= o.lhs.get_dimension()/one_sec, reason='TimeDerivative')
            return
        if o.rhs.is_dimension_known():
            self.RegisterDimensionPropogation( o.lhs, new_dimension= o.rhs.get_dimension()*one_sec, reason='TimeDerivative')
            return

    def VisitEqnAssignment(self, o, **kwargs):
        return self.EnsureEqualDimensions([o.lhs, o.rhs],reason='EqnAssignment')



    def VisitAddOp(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs], reason='AddOp')

    def VisitSubOp(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.lhs, o.rhs], reason='SubOp')

    def VisitMulOp(self, o, **kwargs):
        if len( [ True for i in (o, o.lhs,o.rhs) if i.is_dimension_known()] ) !=2:
            return

        if o.is_dimension_known():
            if o.lhs.is_dimension_known():
                self.RegisterDimensionPropogation( o.rhs, new_dimension= o.get_dimension()/o.lhs.get_dimension(), reason='MulOp')
            else:
                self.RegisterDimensionPropogation( o.lhs, new_dimension= o.get_dimension()/o.rhs.get_dimension(), reason='MulOp')
        else:
            self.RegisterDimensionPropogation( o, new_dimension= o.lhs.get_dimension()*o.rhs.get_dimension(), reason='MulOp')



    def VisitDivOp(self, o, **kwargs):
        # If we don't have 2 unknowns, we can't do much:
        if len( [ True for i in (o, o.lhs,o.rhs) if i.is_dimension_known()] ) !=2:
            return

        if o.is_dimension_known():
            if o.lhs.is_dimension_known():
                o.rhs.set_dimension( o.lhs.get_dimension() / o.get_dimension() )
            else:
                o.lhs.set_dimension( o.get_dimension() * o.rhs.get_dimension() )
        else:
            o.set_dimension( o.lhs.get_dimension() / o.rhs.get_dimension() )


    def VisitExpOp(self, o, **kwargs):
        if o.lhs.is_dimension_known():
            assert o.lhs.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False),  'LHS Expected to be dimensionless, actually %s'%(o.lhs.get_dimension())
        if o.is_dimension_known():
            assert o.get_dimension().is_dimensionless(allow_non_zero_power_of_ten=False)

        if not o.lhs.is_dimension_known():
            o.lhs.set_dimension( self.ast.backend.Unit() )
        if not o.is_dimension_known():
            o.set_dimension( self.ast.backend.Unit() )


    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.rhs])
        #print "Is func def rhs unit known", o.rhs.is_dimension_known()
        #print "Is func def unit known", o.is_dimension_known()
        #for p,v in self.parameters.iteritems():




    def VisitFunctionDefParameter(self, o, **kwargs):
        #self.EnsureEqualDimensions([o, o.rhs_ast])
        pass

    def VisitFunctionDefInstantiation(self, o, **kwargs):

        # Check the parameters tie up:
        for p in o.parameters.values():
            self.EnsureEqualDimensions([p.rhs_ast, p])
            self.EnsureEqualDimensions([p, p._function_def_parameter])
            self.EnsureEqualDimensions([p.rhs_ast, p._function_def_parameter])
            #self.EnsureEqualDimensions([p, p._function_def_parameter.rhs_ast])

        # powint and sqrt need to  be handled differently, since thier
        # dimensions depend on the input and output:
        if isinstance(o.function_def, ast.BuiltInFunction) and o.function_def.funcname in ['powint','sqrt']:
            
            if o.function_def.funcname == "powint":
                assert False
                p = o.parameters['x']
                n = int( o.parameters['n'].rhs_ast.value.magnitude )
                d = int( o.parameters['d'].rhs_ast.value.magnitude )
                if o.is_dimension_known() and not p.is_dimension_known():
                    odim = o.get_dimension()
                    assert odim.powerTen == 0
                    pdim = self.ast.backend.Unit(
                            meter=odim.meter*2,
                            second=odim.second*2,
                            ampere=odim.ampere*2,
                            kelvin=odim.kelvin*2,
                            mole=odim.mole*2,
                            candela=odim.candela*2,)
                    p.set_dimension(pdim)
                    assert False
                if p.is_dimension_known() and not o.is_dimension_known():
                    pdim = p.get_dimension()
                    assert pdim.powerTen == 0
                    odim = self.ast.backend.Unit(
                            meter=pdim.meter/2,
                            second=pdim.second/2,
                            ampere=pdim.ampere/2,
                            kelvin=pdim.kelvin/2,
                            mole=pdim.mole/2,
                            candela=pdim.candela/2,)
                    o.set_dimension(odim)
                    assert False


            elif o.function_def.funcname == "sqrt":
                p = o.parameters.values()[0]

                if o.is_dimension_known() and not p.is_dimension_known():
                    odim = o.get_dimension()
                    assert odim.powerTen == 0
                    pdim = self.ast.backend.Unit(
                            meter=odim.meter*2,
                            second=odim.second*2,
                            ampere=odim.ampere*2,
                            kelvin=odim.kelvin*2,
                            mole=odim.mole*2,
                            candela=odim.candela*2,)
                    p.set_dimension(pdim)
                    assert False
                if p.is_dimension_known() and not o.is_dimension_known():
                    pdim = p.get_dimension()
                    assert pdim.powerTen == 0
                    odim = self.ast.backend.Unit(
                            meter=pdim.meter/2,
                            second=pdim.second/2,
                            ampere=pdim.ampere/2,
                            kelvin=pdim.kelvin/2,
                            mole=pdim.mole/2,
                            candela=pdim.candela/2,)
                    o.set_dimension(odim)
                    assert False


            else:
                assert False


        else:
            self.EnsureEqualDimensions([o, o.function_def])



    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        self.EnsureEqualDimensions([o, o.get_function_def_parameter(), o.rhs_ast], reason="Parameter Instantiation" )


    def VisitBuiltInFunction(self, o, **kwargs):
        dimensionless_functions = [
                'sin','cos','tan',
                'sinh','cosh','tanh',
                'asin','acos','atan','atan2',
                'exp','ln','log2','log10', 
                'pow','ceil','fabs','floor', 
                ]
        if o.funcname in dimensionless_functions:
            return

        return 
        print 'Dealing with special'
        assert o.funcname in dimensionless_functions

        return
        raise NotImplementedError()






class PropogateDimensions(object):
    @classmethod
    def propogate_dimensions(cls, eqnset):

        wd =   eqnset.get_working_dir()
        print 'OutDir:', wd
        EnsureExisits(wd)

        labels = ASTNodeLabels()
        labels.Visit(eqnset)
        labels = labels.id_dict

        # Generate a summary file of the ID's
        idStrings  = ActionerFormatStringsAsIDs(labels)
        idStrings.Visit(eqnset)
        idStrings.tofile(wd+'ID_Definitions.txt')

        all_symbols = ASTVisitorCollectorAll( eqnset).objects
        obj_with_dimension = [ s for s in all_symbols if isinstance(s, ast.ASTExpressionObject)]


        # Action, lets walk over the tree and try and resolve the dimensions:
        try:
            uR = DimensionResolver(ast = eqnset, obj_label_dict=labels)

            while True:
                nUnresolvedPre = len( [ s for s in obj_with_dimension if not s.is_dimension_known() ] )
                res_symbols = [ uR.Visit(s) for s in all_symbols ]
                nUnresolvedPost = len( [ s for s in obj_with_dimension if not s.is_dimension_known() ] )

                if nUnresolvedPre == nUnresolvedPost:
                    break

        except UnitMismatchError, e:

            print 'Error with: '
            print ' - ', labels[e.objA], "Unit:", e.objA.get_dimension()
            print ' - ', labels[e.objB], "Unit:", e.objB.get_dimension()
            print
            s1 = StringWriterVisitor().Visit(e.objA)
            s2 = StringWriterVisitor().Visit(e.objB)
            print 'S1:', s1
            print 'S2:',  s2
            #assert False
            raise



        uR.SummariseUnitState(title="Finally")

        # Print the History:
        with open(wd+'UnitsResolutionHistory','w') as f:
            f.writelines("\n".join(uR.history) )



        # Look for unresolved symbols:
        symbols_without_dimension = [ s for s in all_symbols if isinstance(s, ast.ASTExpressionObject) and not s.is_dimension_known()]
        if symbols_without_dimension:
            print 'Unable to resolve the dimensions of the following symbols:'
            for s in symbols_without_dimension:
                try:
                    print '\tObj:', type(s),s,
                    print '\t  -', 
                    print '\t', s.symbol
                except:
                    pass
                    print
            print
            assert False


