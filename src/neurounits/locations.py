


import os 



class Locations(object):
    @classmethod
    def get_package_root(cls):
        return os.path.abspath( os.path.join( os.path.dirname(__file__), '../../' ) )
        
    
    @classmethod    
    def get_default_9ml_locations(cls):
        locs = [ get_package_root(cls) + 'test_data/l4-9ml/*.9ml'  ]
        
        src_files = itertools.chain( * [glob.glob(l) for l in locs] )
        return src_files
        
