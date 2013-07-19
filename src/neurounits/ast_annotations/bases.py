



class ASTTreeAnnotationManager(object):
    def __init__(self, ):
        pass



class ASTNodeAnnotationData():
    def __init__(self, mgr, node):
        self._node = node
        self._mgr = mgr
    
        self._data = {}
    
    def add(self, key, value):
        assert not key in self._data
        self._data[key] = value
        
    def __getattr__(self, key):
        return self._data[key]
    
    
    
    
    
    
    
class ASTTreeAnnotator(object):
    def annotate_ast(self):
        raise NotImplementedError()


