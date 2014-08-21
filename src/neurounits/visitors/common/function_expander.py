


from neurounits.visitors import ASTVisitorBase
import  neurounits.ast as ast
from neurounits.visitors.bases.base_actioner_default_ignoremissing import ASTActionerDefaultIgnoreMissing







class _FunctionCloner(ASTVisitorBase):

    def __init__(self, functiondef_instantiation):

        self.functiondef_instantiation = functiondef_instantiation
        self.params_old_to_new = {}
        for sym, param_obj in functiondef_instantiation.parameters.items():
            self.params_old_to_new[param_obj.get_function_def_parameter()] = param_obj.rhs_ast


        self.new_node = self.visit(self.functiondef_instantiation.function_def.rhs)


    def VisitFunctionDefBuiltInInstantiation(self, o):



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





    def VisitFunctionDefParameter(self, o ):
        assert o in self.params_old_to_new
        return self.params_old_to_new[o]

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

    def VisitConstant(self, o):
        return ast.ConstValue(value=o.value)

    def VisitIfThenElse(self, o):
        return ast.IfThenElse(
                predicate = self.visit(o.predicate),
                if_true_ast = self.visit(o.if_true_ast),
                if_false_ast = self.visit(o.if_false_ast) )

    def VisitInEquality(self, o):
        return ast.InEquality(
                lesser_than = self.visit(o.lesser_than),
                greater_than = self.visit(o.greater_than),
                )



class FunctionExpander(ASTActionerDefaultIgnoreMissing):

    def __init__(self, component):
        self.component = component
        super(FunctionExpander, self).__init__()

        self.visit(component)

        # And so no more attached functions:
        # Remove the functions from the body:
        component._function_defs.clear()




    def ActionNode(self, n, **kwargs):

        pass

    def ActionFunctionDefBuiltInInstantiation(self,n):
        return

    def ActionFunctionDefUserInstantiation(self, n):

        new_node = _FunctionCloner(n).new_node

        # Replace the node:
        from neurounits.visitors.common.ast_replace_node import ReplaceNode
        ReplaceNode.replace_and_check(n, new_node, root=self.component)

        # Make sure all the units are still OK:
        from neurounits.ast_builder.builder_visitor_propogate_dimensions import PropogateDimensions
        PropogateDimensions.propogate_dimensions(self.component)


