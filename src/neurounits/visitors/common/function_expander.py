


from neurounits.visitors import ASTVisitorBase
import  neurounits.ast as ast
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing







class _FunctionCloner(ASTVisitorBase):

    def __init__(self, functiondef_instantiation):

        print '\n\n'
        self.functiondef_instantiation = functiondef_instantiation
        print 'Cloning function-def rhs:', repr(self.functiondef_instantiation)

        print 'Copying parameters:'
        self.params_old_to_new = {}
        for sym, param_obj in functiondef_instantiation.parameters.items():
            self.params_old_to_new[param_obj.get_function_def_parameter()] = param_obj.rhs_ast


        self.new_node = self.visit(self.functiondef_instantiation.function_def.rhs)


    def VisitFunctionDefBuiltInInstantiation(self, o):

        #if o.function_def.is_builtin():

        params_new = {}
        # Clone the parameter objects:
        for param_name, func_call_param in o.parameters.items():
            pnew = ast.FunctionDefParameterInstantiation(
                                        rhs_ast=self.visit(func_call_param.rhs_ast),
                                        symbol=func_call_param.symbol,
                                        function_def_parameter = func_call_param._function_def_parameter
                                        )
            params_new[param_name] = pnew

        return ast.FunctionDefBuiltInInstantiation( 
                    function_def = o.function_def,
                    parameters = params_new )

    def VisitFunctionDefUserInstantiation(self, o):
        print 'Function call:', repr(o)
        assert False, 'We shoudl not get here! we are doing depth first search'




    def VisitFunctionDefParameter(self, o ):
        print 'Searching:', o, 'in', self.params_old_to_new
        assert o in self.params_old_to_new
        return self.params_old_to_new[o]
        assert False

    def VisitAddOp(self, o):
        return ast.AddOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitSubOp(self, o):
        return ast.SubOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitMulOp(self, o):
        return ast.MulOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )

    def VisitDivOp(self, o):
        return ast.DivOp(
                self.visit(o.lhs),
                self.visit(o.rhs) )





class FunctionExpander(ASTActionerDefaultIgnoreMissing):

    def __init__(self, component):
        self.component = component
        super(FunctionExpander,self).__init__()
        
        # Lets go:
        self.visit(component)
        #print component._function_defs
        
        # And so no more attached functions:
        #from neurounits.units_misc import LookUpDict
        
        # Remove the functions from the body:
        component._function_defs.clear()
        
        
    

    def ActionNode(self, n, **kwargs):
        #print 'Skipping', n
        pass

    def ActionFunctionDefBuiltInInstantiation(self,n):
        return
    def ActionFunctionDefUserInstantiation(self,n):
#        if n.function_def.is_builtin():
#            return


        new_node = _FunctionCloner(n).new_node
        
        # Replace the node:
        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        ReplaceNode.replace_and_check(n, new_node, root=self.component)

        # Make sure all the units are still OK:
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self.component)


