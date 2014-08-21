#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
os.environ['MREORG_CONFIG'] = 'SAVEALL;NOSHOW'
import mreorg

import pyneurounits
import pylab
import numpy as np







def test_lut(lut_address_size, lut_input_range_upscale, input_range, exp_out_scale, exp_in_scale=None,):
    lut = pyneurounits.LUTExp24(lut_address_size, lut_input_range_upscale)

    # Create a vectorized 'get' function:
    def _getexp(a, b, c):
            return lut.get(int(a), int(b), int(c))

    def _from_float(x, scale):
            return pyneurounits.n32_from_float24(float(x), int(scale))

    def _to_float(x, scale):
            return pyneurounits.n32_to_float24(int(x), int(scale))

    getexp = np.vectorize(_getexp)
    to_float = np.vectorize(_to_float)
    from_float = np.vectorize(_from_float)



    exp_in_scale = exp_in_scale if exp_in_scale is not None else lut_input_range_upscale

    x = np.linspace(input_range[0], input_range[1], num=1000)
    exp_x_int = getexp(from_float(x, exp_in_scale), exp_in_scale, exp_out_scale)
    exp_x = to_float(exp_x_int, exp_out_scale)


    err_diff_float_prop = np.fabs(np.exp(x) - exp_x) / np.exp(x)
    err_diff_int = np.fabs(from_float(np.exp(x), exp_out_scale) - exp_x_int)


    f = pylab.figure(figsize=(180. / 25.4, 4.))
    f.suptitle('Results from lookup table:')
    ax1 = f.add_subplot(311)
    ax2 = f.add_subplot(312)
    ax3 = f.add_subplot(313)

    ax1.plot(x, exp_x, 'x-', label='LUT', ms=2)
    ax1.plot(x, np.exp(x), lw=10, alpha=0.4, label='Builtin exp()')
    ax2.plot(x, err_diff_float_prop * 100, 'x', label='Proportional error (double) in %')
    ax3.plot(x, err_diff_int, 'x', label='Absolute error (int)')

    for ax in [ax1, ax2, ax3]:
        ax.legend()




test_lut(lut_address_size=5, lut_input_range_upscale=3, input_range=(-6, 6), exp_out_scale=10)
test_lut(lut_address_size=5, lut_input_range_upscale=3, input_range=(-6, -2), exp_out_scale=-2)
#
test_lut(lut_address_size=7, lut_input_range_upscale=3, input_range=(-6, 6), exp_out_scale=10)
test_lut(lut_address_size=7, lut_input_range_upscale=3, input_range=(-6, -2), exp_out_scale=-2)
#
test_lut(lut_address_size=7, lut_input_range_upscale=4, input_range=(-15, -14), exp_out_scale=-19)

test_lut(lut_address_size=10, lut_input_range_upscale=3, input_range=(-6, 6), exp_out_scale=10)
test_lut(lut_address_size=10, lut_input_range_upscale=3, input_range=(-6, -2), exp_out_scale=-2)
#
#test_lut(lut_address_size=7, lut_input_range_upscale=4, input_range=(10, 14), exp_out_scale=21)

pylab.show()




print "Finsihed OK"
