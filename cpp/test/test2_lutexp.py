
import os
os.environ['MREORG_CONFIG'] = 'SAVEALL;NOSHOW'
import mreorg


import pylab
import numpy as np

import pyneurounits



def test_lut(lut_address_size, lut_input_range_upscale, input_range, exp_out_scale, exp_in_scale=None):
    lut = pyneurounits.LUTExp24(lut_address_size, lut_input_range_upscale)

    # Create a vectorized 'get' function:
    def _getexp(a, b, c):
            return lut.get(int(a), int(b), int(c) )

    def _from_float(x, scale):
            return pyneurounits.n32_from_float24(float(x), int(scale))

    def _to_float(x, scale):
            return pyneurounits.n32_to_float24(int(x), int(scale))

    getexp = np.vectorize(_getexp )
    to_float = np.vectorize(_to_float )
    from_float = np.vectorize(_from_float )




    exp_in_scale = exp_in_scale if exp_in_scale is not None else lut_input_range_upscale

    x = np.linspace(input_range[0], input_range[1], num=1000)
    exp_x_int = getexp(from_float(x, exp_in_scale), exp_in_scale, exp_out_scale)
    exp_x = to_float(exp_x_int, exp_out_scale )


    err_diff_float_prop = np.fabs(np.exp(x) - exp_x) / np.exp(x)
    err_diff_int = np.fabs(from_float(np.exp(x), exp_out_scale) - exp_x_int)
    err_diff_float = err_diff_int / 2**(24-1)



    x1 = (2**(lut_input_range_upscale))
    x0 = -x1
    x_points = np.linspace(x0, x1, num=(2**lut_address_size))



    f = pylab.figure(figsize=(180./25.4, 3.))
    f.subplots_adjust(bottom=0.05, top=0.95, hspace=0.125, left=0.15, right=0.95)

    import matplotlib.gridspec as gridspec
    gs = gridspec.GridSpec(3, 1, height_ratios=[2, 1, 1])

    ax1 = f.add_subplot(gs[0])
    ax2 = f.add_subplot(gs[2])
    ax3 = f.add_subplot(gs[1])


    ax1.plot(x, exp_x, 'x', label='LUT', ms=1)
    ax1.plot(x, np.exp(x), lw=5, alpha=0.4, label='Builtin exp()')
    ax1.plot(x_points, np.exp(x_points), '.', color='red', ms=5)
    ax2.plot(x_points, np.zeros_like(x_points), '.', color='red', ms=5)
    ax2.plot(x, err_diff_float_prop * 100, 'x', label='Proportional error (double) in %' )
    ax3.plot(x, err_diff_float, 'x', label='Absolute error (float)')








    ax1.legend(loc=9)




     # Mini, zoomed in plots:
    z_x, z_y, z_w, z_h = (0.3, 0.8, 0.15, 0.125)
    ax1a = f.add_axes([z_x, z_y, z_w, z_h])
    ax1b = f.add_axes([z_x+0.35, z_y, z_w, z_h])
    for ax in [ax1a, ax1b]:
        ax.plot(x, exp_x, 'x', label='LUT', ms=1.5)
        ax.plot(x, np.exp(x), lw=5, alpha=0.4, label='Builtin exp()')
        ax.plot(x_points, np.exp(x_points), '.', color='red', ms=5)
    za_xrange = (-5.5, -4.5)
    zb_xrange = (4.5, 5.5)

    za_yrange = (-10, 10)
    zb_yrange = (100, 350)
    ax1a.set_xlim(za_xrange); ax1a.set_ylim(za_yrange)
    ax1b.set_xlim(zb_xrange); ax1b.set_ylim(zb_yrange)



    ax1.axvspan(*za_xrange, color='grey', alpha=0.4)
    ax1.axvspan(*zb_xrange, color='grey', alpha=0.4)


    ax1.set_ylim(-50, 550)
    ax1.set_ylabel("exp(x)")
    ax2.set_ylabel("Proportional\nerror from\n using LUT \n(in %) ")
    ax3.set_ylabel("Absolute\nerror from\n using LUT ")



    ax1.set_xticklabels("")
    ax3.set_xticklabels("")

    ax1.set_xlim(*input_range)
    ax2.set_xlim(*input_range)
    ax3.set_xlim(*input_range)

    for ax in [ax1, ax2, ax3]:
        ax.get_yaxis().set_label_coords(-0.075, 0.5)




#test_lut(lut_address_size=6, lut_input_range_upscale=4, input_range=(-8, 8), exp_out_scale=9)
test_lut(lut_address_size=5, lut_input_range_upscale=3, input_range=(-6, 6), exp_out_scale=10)

pylab.savefig("/home/mh735/hw/Cambridge2013/paper/generated/build/fig_newLUT.svg")
pylab.show()




print "Finsihed OK"
