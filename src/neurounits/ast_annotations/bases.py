



class ASTTreeAnnotationManager(object):
    def __init__(self, ):
        pass



class ASTNodeAnnotationData():
    def __init__(self, node):
        self._node = node
        self._mgr = None
    
        self._data = {}
    
    def __str__(self):
        return "<ASTNodeAnnotationData: %s >" % str(self._data) 
    
    def add(self, key, value):
        assert not key in self._data
        self._data[key] = value
        
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value
        
    
    
    
    
    
    
class ASTTreeAnnotator(object):
    def annotate_ast(self):
        raise NotImplementedError()


