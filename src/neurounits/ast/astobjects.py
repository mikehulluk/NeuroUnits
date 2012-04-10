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
from neurounits.units_misc import Chainmap



class ASTObject(object):        
    def is_resolved(self):
        return True
    pass



class EqnSet(ASTObject):

    #def __init__(self, name, assignments, timederivatives, funcdefs,constants, parameters, supplied_values,  unit_backend, builder, ):
    def __init__(self,):
        self._eqn_time_derivatives = {}
        self._eqn_assignment  = {}
        self._function_defs = {}

        self._parameters =  {}
        self._supplied_values =  {}
        self._constants ={}

        self.name = None
        
        self.summary_data = []

        self.on_events = []
    
        self._builder = None
    
    
    
    
    def getSymbol(self, sym):
        
        try:
            return Chainmap(self._function_defs,self._constants)[sym]
        except KeyError:
            raise ValueError("Library: %s does not contain symbol: %s"%(self.name, sym) )
        
        
    def get_working_dir(self):
        return self._builder.library_manager.working_dir + "/" + self.name + "/"
    
    def get_assignments(self):
        return self._eqn_assignment.values() 
    assignments = property(get_assignments)

    def get_timederivatives(self):
        return self._eqn_time_derivatives.values() 
    timederivatives = property(get_timederivatives)

    def get_functiondefs(self):
        return self._function_defs.values() 
    functiondefs = property(get_functiondefs)

    
    def get_terminal_obj(self, symbol):
        m = Chainmap( self.getParametersDict(),  
                      self.getSuppliedValuesDict(),  
                      self.getAssignedVariablesDict(), 
                      self.getStateVariablesDict(), 
                      self.getConstantsDict()  )
        return m[symbol]
    
    
    def getParameters(self):
        return self._parameters.values()
    def getConstants(self):
        return self._constants.values()
    constants = property(getConstants)
    def getSuppliedValues(self,):
        return self._supplied_values.values()
    
    
    def getSuppliedValuesDict(self):
        return self._supplied_values
    def getParametersDict(self):
        return self._parameters
    def getConstantsDict(self):
        return self._constants
    
    def getAssignedVariablesDict(self):
        return  dict( [(ass.lhs.symbol, ass.lhs)  for ass in self._eqn_assignment.values() ])
    def getStateVariablesDict(self):
        return dict([(td.lhs.symbol, td.lhs)  for td in self._eqn_time_derivatives.values() ])
    
    
    
    
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitEqnSet(self, **kwargs)









class ASTExpressionObject(ASTObject):
    def __init__(self, unitMH=None, dimension=None):
        
        self._unitMH = None #unitMH
        self._dimension = None #dimension
        
        if dimension:
            self.set_dimensionality(dimension)
        if unitMH:
            self.set_unitMH(unitMH)
        


    def is_unitMH_known(self):
        return self._unitMH is not None

    def get_unitMH(self):
        assert  self.is_unit_known()
        return self._unitMH

    def set_unitMH(self, u):
        
        if self.is_dimensionality_known():
            self.get_dimensionality().check_compatible(u)
        
        else:
            self.set_dimensionality( u.with_no_powerten() )
        assert not self.is_unitMH_known()
        self._unitMH = u
        
        
        
        #debug=False
        #if debug:
        #    try:
        #        l = "Symbol: %s"% self.symbol + " -> " + str(u) 
        #        if self.symbol is None:
        #            print "SymbolNone:", type(self)
        #        print l
        #    except:
        #        pass


        



    def is_dimensionality_known(self):
        return self._dimension is not None

    def get_dimensionality(self):
        assert  self.is_dimensionality_known()
        return self._dimension
    
    def set_dimensionality(self, dimension):
        assert not self.is_dimensionality_known()
        assert not self.is_unitMH_known()
        self._dimension = dimension
        
    

    def set_unit(self):
        assert False


    def is_unit_known(self):
        assert False
        return self._unit is not None

    def get_unit(self):
        assert False
        assert  self.is_unit_known()
        return self._unit






# Boolean Expressions:
class IfThenElse(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitIfThenElse(self, **kwargs)

    def __init__(self, predicate, if_true_ast, if_false_ast,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.predicate = predicate
        self.if_true_ast = if_true_ast
        self.if_false_ast = if_false_ast


# Boolean Objects:
####################
class InEquality(object):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitInEquality(self, **kwargs)

    def __init__(self, less_than, greater_than,**kwargs):
        self.less_than = less_than
        self.greater_than = greater_than

class BoolAnd(object):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitBoolAnd(self, **kwargs)

    def __init__(self, lhs, rhs,**kwargs):
        self.lhs = lhs
        self.rhs = rhs

class BoolOr(object):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitBoolOr(self, **kwargs)

    def __init__(self, lhs, rhs,**kwargs):
        self.lhs = lhs
        self.rhs = rhs

class BoolNot(object):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitBoolNot(self, **kwargs)

    def __init__(self, lhs,**kwargs):
        self.lhs = lhs






class AssignedVariable(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitAssignedVariable(self, **kwargs)

    def __init__(self, symbol,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol = symbol
        self.assignment_rhs = None

class SuppliedValue(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitSuppliedValue(self, **kwargs)

    def __init__(self, symbol,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol = symbol

class StateVariable(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitStateVariable(self, **kwargs)

    def __init__(self,symbol, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol = symbol

class Parameter(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitParameter(self, **kwargs)

    def __init__(self, symbol, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol = symbol

class ConstValue(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitConstant(self, **kwargs)

    def __init__(self,value,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.value = value
        self.set_unit(value.units)



class EqnTimeDerivative(ASTObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitEqnTimeDerivative(self, **kwargs)

    def __init__(self,lhs,rhs,**kwargs):
        self.lhs = lhs
        self.rhs = rhs

class EqnAssignment(ASTObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitEqnAssignment(self, **kwargs)

    def __init__(self,lhs,rhs,**kwargs):
        self.lhs = lhs
        self.rhs = rhs
        pass



class SymbolicConstant(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitSymbolicConstant(self, **kwargs)
    def __init__(self,symbol, value,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol = symbol
        self.value = value
        self.set_unitMH( value.units )
    def __repr__(self):
        return "<SymbolicConstant: %s = %s>" %(self.symbol, self.value)



class BuiltInFunction(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitBuiltInFunction(self, **kwargs)
    
    def __init__(self, funcname, parameters, unitMH, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.funcname = funcname
        self.parameters = parameters
        self.set_unitMH( unitMH )
        

class FunctionDef(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitFunctionDef(self, **kwargs)

    def __init__(self, funcname, parameters, rhs, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.funcname = funcname
        self.parameters=parameters
        self.rhs = rhs

class FunctionDefParameter(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitFunctionDefParameter(self, **kwargs)

    def __init__(self, symbol=None, **kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.symbol=symbol







class FunctionDefInstantiation(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitFunctionDefInstantiation(self, **kwargs)

    def __init__(self, parameters, function_def,**kwargs):
        ASTExpressionObject.__init__(self, **kwargs)
        self.function_def = function_def
        self.parameters = parameters

class FunctionDefParameterInstantiation(ASTExpressionObject):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitFunctionDefInstantiationParater(self, **kwargs)
    def __init__(self, rhs_ast, symbol, **kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.symbol=symbol
        self.rhs_ast = rhs_ast
        self._function_def_parameter = None

    def set_function_def_parameter(self, param):
        assert self._function_def_parameter is None
        self._function_def_parameter = param
        
    def get_function_def_parameter(self):
        assert self._function_def_parameter is not None
        return self._function_def_parameter






















class BinaryOp(ASTExpressionObject):

    def __init__(self,lhs,rhs,**kwargs):
        ASTExpressionObject.__init__(self,**kwargs)
        self.lhs=lhs
        self.rhs=rhs


class AddOp(BinaryOp):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitAddOp(self, **kwargs)
        
class SubOp(BinaryOp):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitSubOp(self, **kwargs)

class MulOp(BinaryOp):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitMulOp(self, **kwargs)

class DivOp(BinaryOp):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitDivOp(self, **kwargs)

class ExpOp(BinaryOp):
    def AcceptVisitor(self, v, **kwargs):
        return v.VisitExpOp(self, **kwargs)



