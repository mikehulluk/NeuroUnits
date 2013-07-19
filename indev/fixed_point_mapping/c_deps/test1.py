import numpy as np
import pylab


d = np.loadtxt("exp_out.txt")

pylab.plot( d[:,0], d[:,1], 'x-')

pylab.plot( d[:,0], np.exp(d[:,0]), lw=10, alpha=0.4 )
pylab.show()
