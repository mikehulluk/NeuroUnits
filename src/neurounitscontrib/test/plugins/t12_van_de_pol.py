
from neurounits.test import TestingPluginBase


from neurounits import NutsIO
import glob


class TestRunLorenz(TestingPluginBase):
    
    def __init__(self,):
        self.results = None
    
    def get_name(self, ):
        return 'Test van de Pol'
        
    def print_results(self,):
        print 'Results:'
        
        
    def run(self, args):
        print 'Running Van de pol system'    
