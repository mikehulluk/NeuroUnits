

import os
import hashlib
import pickle
import trace




#def f2(a):
#    return a*a
#def my_func():
#    print 'Hello'
#    f2(3)



class HashManager(object):

    _file_hashes = {}

    @classmethod
    def get_filename_hash(cls, filename):
        if not os.path.exists(filename):
            return None
        if not filename in cls._file_hashes:
            with open(filename) as fobj:
                hashobj = hashlib.new('sha1')
                hashobj.update(fobj.read())
            cls._file_hashes[filename] = str(hashobj.hexdigest())
        return cls._file_hashes[filename]


class _CachedFileAccessData(object):

    def __init__(self, filename, linenumbers):
        self.filename = filename
        self.linenumbers = linenumbers
        self._cachedhashfile = HashManager.get_filename_hash(filename)
        self._cachedhashlines = self.current_line_hash()

    def current_line_hash(self):

        lines = self.get_file_lines()
        if lines is not None:
            hashobj = hashlib.new('sha1')
            hashobj.update('\n'.join(lines))
            return hashobj.hexdigest()
        else:
            return None

    def get_file_lines(self):
        with open(self.filename) as fobj:
            lines = fobj.readlines()

        res = []
        n_lines = len(lines)
        for linenumber in self.linenumbers:
            if not linenumber < n_lines:
                return None
            res.append(lines[linenumber])
        return res

    def is_clean(self):
        if self._cachedhashfile == HashManager.get_filename_hash(self.filename):
            return True
        if self._cachedhashlines is not None and \
           self._cachedhashlines == self.current_line_hash():
            return True

        return False

    def __str__(self):
        return '<CachedFileObject: (is_clean:%s) %s [%s->%s]>' % (self.is_clean(), self.filename, self._cachedhashfile, HashManager.get_filename_hash(self.filename))













class ComponentLibrary(object):

    _component_functors = {}
    _cache_dir = os.path.expanduser('~/.neurounits/component_cache/')
    if not os.path.exists(_cache_dir):
        os.makedirs(_cache_dir)

    @classmethod
    def register_component_functor(cls, component_name, component_functor, is_cachable=True):
        assert not component_name in cls._component_functors
        cls._component_functors[component_name] = (component_functor, is_cachable)

    @classmethod
    def instantiate_component(cls, component_name, **kwargs):
        (component_functor, is_cachable) = cls._component_functors[component_name]
        if not is_cachable:
            return component_functor(**kwargs)

        # 1. Serialise and take the hash of the kwargs:
        m = hashlib.md5()
        m.update(pickle.dumps(kwargs))
        kw_hash = m.hexdigest()

        # 2. Is there a file cached with that name?
        expected_filename = os.path.join(cls._cache_dir, '%s_%s.pickle' % (component_name, kw_hash))
        print expected_filename

        if os.path.exists(expected_filename):
            with open(expected_filename) as f:
                (trace_info, component) = pickle.load(f)

            # OK, have any of the lines changed??
            has_changed = False
            for t in trace_info:
                has_changed = not t.is_clean()
            if not has_changed:
                return component

        import sys
        trace_obj = trace.Trace(count=1, trace=0, countfuncs=0,
            ignoredirs=[sys.prefix, sys.exec_prefix])

        # Build the component:
        print 'Running functor'
        print
        component = trace_obj.runfunc(component_functor, **kwargs)
        print 'Done running functor'
        print

        # Lets have a look at what lines have been involved:
        _accessed_functions = {}
        for (filename, linenumber) in sorted(trace_obj.results().counts):
            if filename .startswith('/usr'):
                continue
            if filename.startswith('build/bdist.linux-x86_64/egg/'):
                continue
            if '.local/lib/python2.7/site-packages/' in filename:
                continue

            if not filename in _accessed_functions:
                _accessed_functions[filename] = []
            _accessed_functions[filename].append(linenumber)

        for filename, linenumbers in sorted(_accessed_functions.iteritems()):
            print filename, linenumbers

        cache_data = []
        for (filename, linenumbers) in _accessed_functions.iteritems():
            if filename == '<string>':
                print 'Unexpected filename=<string> found. Lines: (%s)' % ','.join(str(l) for l in linenumbers)
                continue

            cd = _CachedFileAccessData(filename=filename, linenumbers=linenumbers)
            cache_data.append(cd)

        # And lets save the results:
        with open(expected_filename, 'w') as f:
            pickle.dump((cache_data, component), f)

        # And return the result:
        return component
