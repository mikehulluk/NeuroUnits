from neurounits.visitors.bases.base_visitor import ASTVisitorBase












class CFFIEqnEvaluator(ASTVisitorBase):
    
    
    def __init__(self, component):
        self.timederivative_functors = {}
        self.assignment_functors = {}
        self.node_functors = {}
        
        
        
    