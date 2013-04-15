import numpy as np
import pylab

v = np.linspace(-90, 50)

vrel = v - (-65)

SF = 1
s_alpha_h = 0.07 * np.exp(vrel/-20) * SF
s_beta_h = (1/ (np.exp((30-vrel)/10) + 1) ) *SF

h_inf = s_alpha_h/ ( s_alpha_h + s_beta_h)

pylab.figure()
pylab.plot(v, s_alpha_h)
pylab.figure()
pylab.plot(v, s_beta_h)
pylab.figure()
pylab.plot(v, h_inf)

pylab.show()
