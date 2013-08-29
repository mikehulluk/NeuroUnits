



class ASTTreeAnnotationManager(object):
    def __init__(self, ):
        self._annotators = {}

    def add_annotator(self, name, annotator):
        assert not name in self._annotators
        self._annotators[name] = annotator


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
    def add_overwrite(self, key, value):
        self._data[key] = value

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data


    def get_summary_str(self):
        if not self._data:
            return ''
        return '[Anns: ' + str(self._data) + ']'


    def get(self, *args, **kwargs):
        return self._data.get(*args, **kwargs)





class ASTTreeAnnotator(object):
    def annotate_ast(self, component):
        raise NotImplementedError()


