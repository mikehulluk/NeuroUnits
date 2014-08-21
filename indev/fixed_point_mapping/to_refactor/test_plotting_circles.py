import matplotlib
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle
import numpy as np

# (modified from one of the matplotlib gallery examples)
resolution = 50  # the number of vertices
N = 100
x = np.random.random(N)
y = np.random.random(N)
radii = 0.1 * np.random.random(N)
patches = []
for (x1, y1, r) in zip(x, y, radii):
    circle = Circle((x1, y1), r)
    patches.append(circle)

fig = plt.figure()
ax = fig.add_subplot(111)

colors = 100 * np.random.random(N)
p = PatchCollection(patches, cmap=matplotlib.cm.jet, alpha=0.4)
p.set_array(colors)
ax.add_collection(p)
plt.colorbar(p)

plt.show()
