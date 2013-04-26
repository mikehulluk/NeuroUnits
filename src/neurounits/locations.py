


import os 
import itertools
import glob


class Locations(object):
    @classmethod
    def get_package_root(cls):
        return os.path.abspath( os.path.join( os.path.dirname(__file__), '../../' ) )
        
    
    
    @classmethod    
    def get_default_9ml_locations(cls):
        locs = [ cls.get_package_root() + '/src/test_data/l4-9ml/std/*.9ml'  ]
        assert locs
        print locs
        
        src_files = sorted(list(itertools.chain( * [glob.glob(l) for l in locs] )))
        assert src_files
        return src_files
        

    class Test(object):
        
        
        
        @classmethod
        def get_nuts_filenames(cls):
            p = os.path.join( Locations.get_package_root(), "src/test_data/" ) 
            return [
                p + 'thesis_l1.nuts',
                p + 'valid_l1.nuts',
            ]
            
            
