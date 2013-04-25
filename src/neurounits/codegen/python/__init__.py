 

import neurounits
import neurounits.codegen.utils as utils

def simulate( component, times ):
    print 'Python Simulation'
    print 'Component', component

    blks = utils.separate_integration_blocks(component)

    for blk in blks:
        print 'blks:', blk






    assert False
