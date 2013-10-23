


import os 
import itertools
import glob
import pkg_resources

class Locations(object):
    
    @classmethod    
    def get_default_9ml_locations(cls):
        src_loc = 'data/test_data/l4-9ml/std/'
        fnames = pkg_resources.resource_listdir('neurounits', src_loc)
        fnames = [os.path.join(src_loc, f) for f in fnames]
        fnames = [fname for fname in fnames if fname.endswith('.9ml')]
        if not fnames:
            raise RuntimeError("Can't find any 9ml test files, perhaps the something in wring in packaging")
        return fnames
        

        
    class Test(object):
        @classmethod
        def get_nuts_fileobjs(cls):

            fobjs = [
                pkg_resources.resource_stream('neurounits', 'data/test_data/thesis_l1.nuts'),
                pkg_resources.resource_stream('neurounits', 'data/test_data/valid_l1.nuts')
                ]
            return fobjs
