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


import scipy
import scipy.integrate
from neurounits.units_misc import safe_dict_merge

import numpy as np
#import quantities as pq  
from neurounits.writers.writer_ast_to_latex import FormatDimension
from neurounits.visitors.common import VisitorFindDirectSymbolDependance
#from neurounits.eqnset_ast.astobjects import AssignedVariable
        
from neurounits import ast


class EqnSimulator(object):
    def __init__(self, ast):        
        
        self.ast = ast
        # Generate Evaluator:
        self.fObj = FunctorGenerator()
        self.fObj.Visit(ast)
        
        
        # Set the variable order:
        self.timederivatives = list(ast.timederivatives)
        self.timederivatives_evaluators = [ self.fObj.timederivative_evaluators[td.lhs.symbol] for td in self.timederivatives ]
    
        self.state_variable_working_units = [ td.lhs.get_unit() for td in self.timederivatives ]
    
    def __call__(self, time_data, params, state0In):
        if len(self.ast.timederivatives) == 0:
            return  
        
        state0_with_units = [ state0In[td.lhs.symbol] for td in self.timederivatives ]
        state0 = [ state.rescale(s_unit) for (state,s_unit) in zip( state0_with_units, self.state_variable_working_units ) ]
        

        def rebuild_kw_dict(raw_state_data, params, t0):
            y = [ self.ast.backend.Quantity(x,y) for (x,y) in zip(raw_state_data,self.state_variable_working_units)]
            kw_states = dict(zip([td.lhs.symbol for td in self.timederivatives] ,y))
            kw = safe_dict_merge(kw_states, params)
            kw['t'] = self.ast.backend.Quantity( float(t0), self.ast.backend.Unit(second=1) )
            return kw


        def evaluate_gradient(y, t0):
            
            # Create a dictionary containing the current states and
            # the parameters:
            kw = rebuild_kw_dict(raw_state_data=y, params=params,t0=t0)

            # Evaluate each gradient:
            dys = []
            for ev, working_unit in zip(self.timederivatives_evaluators, self.state_variable_working_units): 
                #grad = self.ast.backend.quantity_magnitude_in_unit( ev(**kw), (working_unit *self.ast.backend.Unit(second=-1) ) )
                grad = ev(**kw).rescale( working_unit *self.ast.backend.Unit(second=-1) ) 
                dys.append(grad)
            return dys
            
            
            
        # Sanity Check:
        for a,ev in self.fObj.assignment_evaluators.iteritems():
            x = state0In
            x.update(params)
            x['t'] = self.ast.backend.Quantity(0.0,self.ast.backend.Unit(second=1) )
            ev(**state0In)
            
        # ACTION!
        evaluate_gradient(state0, 0.0)
        
        
        # Evaluate:       
        y = scipy.integrate.odeint( evaluate_gradient, state0, t=time_data )
        
        # Add the units back to the states:
        res = {}
        res['t'] = time_data, self.ast.backend.Unit(second=1)
        for i,(td,unit) in enumerate( zip(self.timederivatives,self.state_variable_working_units ) ):
            res[td.lhs.symbol] = ( y[:,i], unit )
        

    
        # Re-evaluate the assignments:
        print 'Re-evaluating assignments'
        nAssignments =len(self.fObj.assignment_evaluators)
        ass_data = [ list() for i in range(nAssignments)]

        ass_units = [None for i in range(nAssignments)]
        ass_names = [None for i in range(nAssignments)]
        for t in time_data:
            state_data = y[t,:]
            kw = rebuild_kw_dict( raw_state_data=state_data,params=params,t0=t ) 


            for i,(a,afunctor) in enumerate(self.fObj.assignment_evaluators.iteritems()):


                aVal = afunctor(**kw)
               
                if ass_units[i] is None:
                    ass_units[i]= aVal.units
                if ass_names[i] is None:
                    ass_names[i]= a
            
                aValRaw = aVal.rescale(ass_units[i]) 
                
                    #@classmethod
                    #def quantity_magnitude_in_unit(cls, quantity, unit):
                    #    return quantity.converted_to_unit(unit)
                

                ass_data[i].append( aValRaw )

        for i,(name,unit) in enumerate(zip(ass_names,ass_units)):
            d = np.array(ass_data[i])
            res[name] = d,unit
            print 'Ass;',name
                
        return res
        
        
        
    

    
def SimulateEquations(ast,):
    evaluator = EqnSimulator(ast)
    
    import pylab
    
    nPlots = len(ast.summary_data)
    f = pylab.figure()
    
    for i,s in enumerate(ast.summary_data):
        
        res = evaluator(state0In=s.y0, params=s.params,time_data=s.t)
       
        ax = f.add_subplot(nPlots,1,i)
        x,xunit = res[s.x]
        y,yunit = res[s.y]
         
        ax.plot( x,y, 'r')
        FormatUnit
        ax.set_xlabel("%s (Unit: %s)"%(s.x, FormatUnit(xunit) ))
        ax.set_ylabel("%s (Unit: %s)"%(s.y, FormatUnit(yunit) ))
        


class FunctorGenerator(ASTVisitorBase):
    
    def __init__(self):
        self.ast = None
        
        self.assignment_evaluators = {}
        self.timederivative_evaluators = {}
        
        
    def VisitEqnSet(self, o, **kwargs):
        self.ast = o
        
        
        deps = VisitorFindDirectSymbolDependance()
        deps.Visit(o)
        
        
        
        self.assignee_to_assigment ={}
        for a in o.assignments:
            self.assignee_to_assigment[a.lhs] = a    
        
        
        
        
        assignment_deps =  deps.dependancies        
        resolved = set()
        
        def resolve(assignment):
            if assignment in resolved:
                return 
            
            if type(assignment) != ast.AssignedVariable:
                #print 'Skipping', assignment
                return 
            for dep in assignment_deps[assignment]:
                resolve(dep)
            self.Visit(self.assignee_to_assigment[assignment])
            resolved.add(assignment)
            
            
        for a in o.assignments:
            resolve(a.lhs)
        
        for a in o.assignments:
            self.Visit(a)
        
        for a in o.timederivatives:
            self.Visit(a)
            
            
    
    def VisitEqnAssignment(self, o, **kwargs):
        
        self.assignment_evaluators[o.lhs.symbol]  = self.Visit(o.rhs)
        #print o.rhs 
        #print 'Executing!'

        
    # AST Objects:
    def VisitEqnTimeDerivative(self, o, **kwargs):
        self.timederivative_evaluators[o.lhs.symbol]  = self.Visit(o.rhs) 




    def VisitIfThenElse(self, o, **kwargs):
        raise NotImplementedError()
    def VisitInEquality(self, o ,**kwargs):
        raise NotImplementedError()
    def VisitBoolAnd(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolOr(self, o, **kwargs):
        raise NotImplementedError()
    def VisitBoolNot(self, o, **kwargs):
        raise NotImplementedError()
    # Function Definitions:
    #def VisitFunctionDef(self, o, **kwargs):
    #    raise NotImplementedError()
    
    
    def VisitBuiltInFunction(self, o, **kwargs):
        def eFunc(**kwargs):
            if o.funcname == 'exp':
                from neurounits.units_backends.default import ParsingBackend
                return ParsingBackend.Quantity( float( np.exp( ( kwargs.values()[0] ).dimensionless() ) ), ParsingBackend.Unit() )
        return eFunc
        
    


    def VisitSymbolicConstant(self, o, **kwargs):
        def eFunc(**kwargs):
            return o.value
        return eFunc

    # Terminals:
    def VisitStateVariable(self, o, **kwargs):
        
        def eFunc2(**kw):
            return kw[ o.symbol ]
        return eFunc2
        

    def VisitParameter(self, o, **kwargs):
        def eFunc(**kwargs):
            return kwargs[ o.symbol ]
        return eFunc
        

    def VisitConstant(self, o, **kwargs):
        
        def eFunc(**kw):
            return o.value
        return eFunc
    
    
    def VisitSuppliedValue(self, o, **kwargs):
        def eFunc(**kwargs):
            return kwargs[ o.symbol ]
        return eFunc    
    

    def VisitAssignedVariable(self, o, **kwargs):
        #print 'Visiting', o.symbol
        # We are at an assignment. We resolve this by looking up the 
        # Right hand side of the assigned variable:
        assignment_rhs = self.assignment_evaluators[o.symbol]
        def eFunc(**kwargs):
            return assignment_rhs(**kwargs)
        return eFunc
    




    
        
    def VisitAddOp(self, o, **kwargs):
        f_lhs = self.Visit(o.lhs)
        f_rhs = self.Visit(o.rhs)
        def eFunc(**kwargs):
            return f_lhs(**kwargs) + f_rhs(**kwargs)
        return eFunc
        
    def VisitSubOp(self, o, **kwargs):
        f_lhs = self.Visit(o.lhs)
        f_rhs = self.Visit(o.rhs)
        def eFunc(**kwargs):
            return f_lhs(**kwargs) - f_rhs(**kwargs)
        return eFunc
        
    def VisitMulOp(self, o, **kwargs):
        f_lhs = self.Visit(o.lhs)
        f_rhs = self.Visit(o.rhs)
        def eFunc(**kwargs):
            #print type(o.lhs)
            #print type(o.rhs)
            
            f_lhs(**kwargs)
            f_rhs(**kwargs)
            return f_lhs(**kwargs) * f_rhs(**kwargs)
        return eFunc

    def VisitDivOp(self, o, **kwargs):
        f_lhs = self.Visit(o.lhs)
        f_rhs = self.Visit(o.rhs)
        def eFunc(**kwargs):
            return f_lhs(**kwargs) / f_rhs(**kwargs)
        return eFunc

    def VisitExpOp(self, o, **kwargs):
        f_lhs = self.Visit(o.lhs)
        def eFunc(**kwargs):
            return f_lhs(**kwargs) ** o.rhs
        return eFunc


    def VisitFunctionDefInstantiation(self, o, **kwargs):
        
        # Param Functors:
        param_functors = {}
        for p in o.parameters:
            param_functors[p] = self.Visit( o.parameters[p] )
        func_call_functor = self.Visit(o.function_def)
        def eFunc(**kwargs):
            func_params = dict( [(p,func(**kwargs) ) for p,func in param_functors.iteritems() ] )
            return func_call_functor(**func_params)
        return eFunc
    
    def VisitFunctionDefInstantiationParater(self, o, **kwargs):
        f_rhs = self.Visit(o.rhs_ast)
        def eFunc(**kwargs):
            return f_rhs(**kwargs) 
        return eFunc


            
    def VisitFunctionDef(self, o, **kwargs):
        f_rhs = self.Visit(o.rhs)
        def eFunc(**kwargs):
            return f_rhs(**kwargs) 
        return eFunc
        
        
    def VisitFunctionDefParameter(self, o, **kwargs):
        def eFunc(**kwargs):
            return kwargs[ o.symbol ]
        return eFunc
                
    

        
        
