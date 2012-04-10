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




class UnitResolver(ASTVisitorBase):


    def EnsureEqualUnits(self, args, reason=None):
        assigned_units = [a for a in args if a.is_unit_known()]
        
        # No units known?
        if len(assigned_units) == 0:
            return []
        
        u = assigned_units[0]
        for au in assigned_units[1:]:
            try:
                u.get_unit().check_compatible( au.get_unit() )
            except UnitMismatchError, e:
                raise UnitMismatchError( unitA=u.get_unit(), unitB=au.get_unit(), objA=u, objB=au) 
            #check_unit_compatible(u, au)

        unassigned_units = [a for a in args if not a.is_unit_known() ]
        for au in unassigned_units:
            self.RegisterUnitPropogation(obj=au, new_unit=u.get_unit(), reason=reason)
        return unassigned_units











    # Visit each node, and try and propogate units.
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
            obj_unit = obj.get_unit() if obj.is_unitMH_known() else "<Unit Unknown>"
            self.history.append(" %s -> Dim: %s Unit: %s"%(name, obj_dimensionality, obj_unit) )

    def DumpUnitStateToHistorySymbols(self):
        for obj, name in self.obj_label_dict.iteritems():
            if not isinstance(obj, ast.ASTExpressionObject):
                continue
            
            try:
                obj_unit = obj.get_unit() if obj.is_unit_known() else "<Unit Unknown>"
                self.history.append(" %s - %s - %s"%(name,obj.symbol,obj_unit) )
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


    def RegisterUnitPropogation(self, obj, new_unit, reason):
        obj.set_unit(new_unit)
        self.history.append("Setting Unit: %s to %s because %s"%(self.obj_label_dict[obj],new_unit,reason) ) 


    def VisitEqnSet(self, o, **kwargs):
        pass


    def VisitOnEvent(self, o, **kwargs):
        return

    def VisitOnEventStateAssignment(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.lhs, o.rhs] )

    def VisitIfThenElse(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.if_true_lhs, o.if_false_lhs] )

    def VisitInEquality(self, o ,**kwargs):
        self.EnsureEqualUnits([o, o.less_than, o.greater_than] )
         
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
        if len( [True for i in (o.lhs, o.rhs) if i.is_unit_known()] ) != 1:
            return

        one_sec = self.ast.backend.Unit(second=1) 
        if o.lhs.is_unit_known():
            self.RegisterUnitPropogation( o.rhs, new_unit= o.lhs.get_unit()/one_sec, reason='TimeDerivative')
            return
        if o.rhs.is_unit_known():
            self.RegisterUnitPropogation( o.lhs, new_unit= o.rhs.get_unit()*one_sec, reason='TimeDerivative')
            return

    def VisitEqnAssignment(self, o, **kwargs):
        return self.EnsureEqualUnits([o.lhs, o.rhs],reason='EqnAssignment')



    def VisitAddOp(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.lhs, o.rhs], reason='AddOp')

    def VisitSubOp(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.lhs, o.rhs], reason='SubOp')

    def VisitMulOp(self, o, **kwargs):
        if len( [ True for i in (o, o.lhs,o.rhs) if i.is_unit_known()] ) !=2:
            return 
        
        if o.is_unit_known():
            if o.lhs.is_unit_known():
                self.RegisterUnitPropogation( o.rhs, new_unit= o.get_unit()/o.lhs.get_unit(), reason='MulOp')
            else:
                self.RegisterUnitPropogation( o.lhs, new_unit= o.get_unit()/o.rhs.get_unit(), reason='MulOp')
        else:
            self.RegisterUnitPropogation( o, new_unit= o.lhs.get_unit()*o.rhs.get_unit(), reason='MulOp')



    def VisitDivOp(self, o, **kwargs):
        # If we don't have 2 unknowns, we can't do much:
        if len( [ True for i in (o, o.lhs,o.rhs) if i.is_unit_known()] ) !=2:
            return 
        
        if o.is_unit_known():
            if o.lhs.is_unit_known():
                o.rhs.set_unit( o.lhs.get_unit() / o.get_unit() )
            else:
                o.lhs.set_unit( o.get_unit() * o.rhs.get_unit() )
        else:
            o.set_unit( o.lhs.get_unit() / o.rhs.get_unit() )


    def VisitExpOp(self, o, **kwargs):
        if o.lhs.is_unit_known():
            assert o.lhs.is_dimensionless(),  'LHS Expected to be dimensionless, actually %s'%(o.lhs.get_unit()) 
        if o.is_unit_known():
            assert o.is_dimensionless()
        
        if not o.lhs.is_unit_known():
            o.lhs.set_unit( self.ast.backend.Unit() )
        if not o.is_unit_known():
            o.set_unit( self.ast.backend.Unit() )

                
    # Function Definitions:
    def VisitFunctionDef(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.rhs])
        
    def VisitFunctionDefParameter(self, o, **kwargs):
        pass
        
    def VisitFunctionDefInstantiation(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.function_def])
        

    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        self.EnsureEqualUnits([o, o.get_function_def_parameter(), o.rhs_ast], reason="Parameter Instantiation" )


    def VisitBuiltInFunction(self, o, **kwargs):
        assert o.funcname=='exp'
        
        return
        raise NotImplementedError()






class PropogateUnits(object):
    @classmethod
    def propogate_units(cls, eqnset):
    
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
        symbols_with_unit = [ s for s in all_symbols if isinstance(s, ast.ASTExpressionObject)]


        # Action, lets walk over the tree and try and resolve the units:
        try:
            uR = UnitResolver(ast = eqnset, obj_label_dict=labels)
            
            while True:
                nUnresolvedPre = len( [ s for s in symbols_with_unit if not s.is_unit_known() ] )
                res_symbols = [ uR.Visit(s) for s in all_symbols ]
                nUnresolvedPost = len( [ s for s in symbols_with_unit if not s.is_unit_known() ] )
    
                if nUnresolvedPre == nUnresolvedPost:
                    break
                
        except UnitMismatchError, e:
            
            print 'Error with: '
            print ' - ', labels[e.objA], "Unit:", e.objA.get_unit()
            print ' - ', labels[e.objB], "Unit:", e.objB.get_unit()
            print
            s1 = StringWriterVisitor().Visit(e.objA)
            s2 = StringWriterVisitor().Visit(e.objB)
            print 'S1:', s1
            print 'S2:',  s2
            assert False
            raise
            
            
            
        uR.SummariseUnitState(title="Finally")
        
        # Print the History:
        with open(wd+'UnitsResolutionHistory','w') as f:
            f.writelines("\n".join(uR.history) )

        
        
        # Look for unresolved symbols:
        symbols_without_unit = [ s for s in all_symbols if isinstance(s, ast.ASTExpressionObject) and not s.is_unit_known()]
        if symbols_without_unit:
            print 'Unable to resolve the units of the following symbols:'
            for s in symbols_without_unit:
                try:
                    print s
                    print s.symbol
                except:
                    pass 
            assert False


