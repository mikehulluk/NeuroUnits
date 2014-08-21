import numpy as np
import matplotlib
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection


import pylab
from hdfjive import HDF5SimulationResultFile
results = HDF5SimulationResultFile("/tmp/neuronits.results-Seq-float.hdf")

import pickle
with open('mh_reduced_connectome.pickle') as f:
    pop_sizes, connections, pop_breakdowns, cell_positions = pickle.load(f)


pop_info = {
    'RB':  ('yellow', 7.),
    'dla': ('red',    6.),
    'dlc': ('red',    5.),

    'dIN': ('brown',  4.),
    'aIN': ('red',    3.),
    'cIN': ('cyan',   2.),
    'MN':  ('green',  1.),
}

plotting_info = {}

f = pylab.figure()
ax = f.add_subplot(111)

for (is_lhs,cell_type), (saved_pop_name, start_index, ncells) in pop_breakdowns.items():
    print 'Plotting: ', cell_type
    pop_color, pop_y_index = pop_info[cell_type]

    pop_y_pos = pop_y_index * (-1. if is_lhs else 1.) * 100.
    pop_x_poses = cell_positions[saved_pop_name][start_index:start_index+ncells]
    r = 10

    patches = []
    for x1 in pop_x_poses:
        circle = Circle((x1,pop_y_pos), r)
        patches.append(circle)


    cmap = matplotlib.colors.ListedColormap(colors=['white', pop_color, pop_color], name='from_list')


    colors = np.random.random(ncells)
    colors = colors * colors
    p = PatchCollection(patches, cmap=cmap, alpha=1.0)

    p.set_array(colors)
    ax.add_collection(p)


ax.set_ylim(-1000, 1000)
ax.set_xlim(400, 2000)

pylab.show()

print 'Done'

