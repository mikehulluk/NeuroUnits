



from neurounits.ast_annotations.bases import ASTNodeAnnotationData, ASTTreeAnnotationManager, ASTTreeAnnotator 
from neurounits.Zdev.fixed_point_annotations import VarAnnot, ASTDataAnnotator, CalculateInternalStoragePerNode




class NodeRangeAnnotator(ASTTreeAnnotator):
    def __init__(self, manual_range_annotations):
        self._manual_range_annotations = manual_range_annotations
    
    def annotate_ast(self, ninemlcomponent ):
        anns = ASTDataAnnotator( ninemlcomponent, annotations_in = self._manual_range_annotations)
        
        
        import neurounits.ast as ast
        # Copy accross:
        for ast_node in ninemlcomponent.all_ast_nodes():
            
            print ast_node
            
            if ast_node in anns.annotations:
                ast_node.annotations.add('node-range', anns.annotations[ast_node] )
        
        print anns
        
        
        raise NotImplementedError()


class NodeFixedPointFormatAnnotator(ASTTreeAnnotator):
    
    annotator_dependancies = [NodeRangeAnnotator] 
    
    def __init__(self):
        pass
    
    def annotate_ast(self):
        raise NotImplementedError()
    