

import neurounits
#import sys
import numpy as np
#import itertools

import pylab
import glob
#import warnings



def test():
     src_files = sorted( glob.glob("/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/std/*.9ml" ))


     library_manager = neurounits.NeuroUnitParser.Parse9MLFiles( src_files)
     general_neuron_with_step_inj = library_manager.get('general_neuron_with_step_inj')

     # Old version:
     res = general_neuron_with_step_inj.simulate(
                times = np.arange(0, 0.1,0.00001),
                )


     res.auto_plot()





if __name__=='__main__':
    test()
    pylab.show()
