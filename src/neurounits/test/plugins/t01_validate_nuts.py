
from neurounits.test import TestingPluginBase


from neurounits import NutsIO
import glob


class TestNutsFiles(TestingPluginBase):
    
    def __init__(self,):
        self.results = None
    
    def get_name(self, ):
        return 'Test NUTS'
        
    def print_results(self,):
        good_res, bad_res, error_res = self.results
        print 'Good:'
        for res in good_res:
            print res
        
        print 'Bad:'
        for res in bad_res:
            print res
        
        print 'Error:'
        for res in error_res:
            print res
        
        
    def run(self, args):
        assert self.results == None
        
        
        pass
        src_dir = '/home/michael/hw/NeuroUnits/src/test_data/'
        files = glob.glob(src_dir + '/*.nuts')
        
        good_results = []
        bad_results = []
        error_results = []
        for fname in files:
            try:
                res = NutsIO.validate(fname)
                good_results.append((fname, res)) 
            except Exception, e:
                print 'Exception Raised'
                error_results.append((fname, e))
        
        
        
        self.results = good_results, bad_results, error_results
        self.print_results()
            
            
