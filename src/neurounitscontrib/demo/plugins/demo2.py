#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------


import mreorg
from neurounitscontrib.demo import DemoPluginBase

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy
import neurounits
import numpy as np



class Demo2(DemoPluginBase):


    def get_name(self, ):
        return '2'

    def run(self, args):
        test2()










ball_arena_text = """

    define_component ball_arena {
        from std.math import abs
        from std.math import pow

        # Define a function, to include units into dimensionless 'abs'
        abs_ms(x) = abs(x/{1m/s}) * {1m/s}
        mag(x,y) = pow(base=x*x+y*y, exp=0.5)
        L(x,y) = mag(x=x/{1m},y=y/{1m}) * {1m}


        # The 4 state variables for Ball 1: Velocity and Position in X,Y
        B1VX' = 0 m/s2
        B1VY'=  0 m/s2
        B1X' = B1VX
        B1Y' = B1VY

        # And make the ball bounce off the walls:
        on(B1X<0m){    B1VX = abs_ms(B1VX); }
        on(B1X>{10m}){ B1VX = -abs_ms(B1VX); }
        on(B1Y<0m){ B1VY = abs_ms(B1VY); }
        on(B1Y>{10m}){ B1VY = -abs_ms(B1VY); }

        B2VX' = 0 m/s2
        B2VY'=  0 m/s2
        B2X' = B2VX
        B2Y' = B2VY
        on(B2X<0m){    B2VX = abs_ms(B2VX); }
        on(B2X>{10m}){ B2VX = -abs_ms(B2VX); }
        on(B2Y<0m){ B2VY = abs_ms(B2VY); }
        on(B2Y>{10m}){ B2VY = -abs_ms(B2VY); }

        rad = 0.5m

        dist_sq = (B1X-B2X)*(B1X-B2X) + (B1Y-B2Y)*(B1Y-B2Y)

        # Work out the unit vector joining the two spheres (C12)
        C12_x = B2X-B1X; C12_y = B2Y-B1Y
        c12_mag = L(x=C12_x,y=C12_y)
        C12_x_hat = C12_x/c12_mag; C12_y_hat = C12_y/c12_mag

        # Take the dot product of C and velocity, to resolve
        # tangential and perpendicilar velocities of Ball 1:
        dot_c12_v1 = C12_x_hat * B1VX  +  C12_y_hat * B1VY
        V1_c_x = dot_c12_v1 * C12_x_hat;
        V1_c_y = dot_c12_v1 * C12_y_hat
        V1_t_x = B1VX - V1_c_x
        V1_t_y = B1VY - V1_c_y

        # Add for ball 2: ....
        C21_x_hat = -C12_x_hat; C21_y_hat = -C12_y_hat;
        dot_c21_v2 = C21_x_hat * B2VX  +  C21_y_hat * B2VY
        V2_c_x = dot_c21_v2 * C21_x_hat;
        V2_c_y = dot_c21_v2 * C21_y_hat
        V2_t_x = B2VX - V2_c_x
        V2_t_y = B2VY - V2_c_y


        t_last'=0
        on( dist_sq < rad*rad and t-t_last > 0.3s ) {
            t_last=t

            # Simply add the two components, but flip the sign of the
            # perpendicular velocity:

            B1VX = V1_t_x - V1_c_x
            B1VY = V1_t_y - V1_c_y

            B2VX = V2_t_x - V2_c_x
            B2VY = V2_t_y - V2_c_y

            emit collision(x=(B1X+B2X)/2, y=(B1Y+B2Y)/2)
        }

        <=> input t:s

}




"""







"""
This short code snippet utilizes the new animation package in
matplotlib 1.1.0; it's the shortest snippet that I know of that can
produce an animated plot in python. I'm still hoping that the
animate package's syntax can be simplified further.
"""

def simData():
# this function is called as the argument for
# the simPoints function. This function contains
# (or defines) and iterator---a device that computes
# a value, passes it back to the main program, and then
# returns to exactly where it left off in the function upon the
# next call. I believe that one has to use this method to animate
# a function using the matplotlib animation package.
#
    times = res.get_time()
    x1s = res.state_variables['B1X']
    y1s = res.state_variables['B1Y']
    x2s = res.state_variables['B2X']
    y2s = res.state_variables['B2Y']

    V1_t_x = res.assignments['V1_t_x']
    V1_t_y = res.assignments['V1_t_y']
    V1_c_x = res.assignments['V1_c_x']
    V1_c_y = res.assignments['V1_c_y']

    c_x_hat = res.assignments['C12_x_hat']
    c_y_hat = res.assignments['C12_y_hat']

    for i in range( len(res.get_time() ) ):
        print 'Getting i:',i
        yield times[i],x1s[i], y1s[i] , x2s[i], y2s[i], V1_t_x[i], V1_t_y[i], V1_c_x[i], V1_c_y[i], c_x_hat[i], c_y_hat[i]

def simPoints(simData):
    global res
    global time_text
    global line1
    global line2
    global line_v1_t
    global line_v1_join
    global line_v1_c
    global time_template

    t,x1,y1, x2, y2, V1_t_x, V1_t_y, V1_c_x, V1_c_y, c_x_hat, c_y_hat = simData
    time_text.set_text(time_template%(t))
    line1.set_data(x1, y1)
    line2.set_data(x2, y2)



    V1_t_mag = numpy.sqrt( float(V1_t_x**2 + V1_t_y**2))
    V1_c_mag = numpy.sqrt( float(V1_c_x**2 + V1_c_y**2))


    line_v1_join.set_data( [x1, x1+c_x_hat], [y1, y1+c_y_hat] )
    line_v1_t.set_data( [x1, x1+V1_t_x/V1_t_mag], [y1, y1+V1_t_y/V1_t_mag] )
    line_v1_c.set_data( [x1, x1+V1_c_x/V1_c_mag], [y1, y1+V1_c_y/V1_c_mag] )
    return line1, line2, time_text, line_v1_t, line_v1_c






res = None
time_text = None
line1 = None
line2 = None
line_v1_t = None
line_v1_join = None
line_v1_c = None
time_template = None


def test2():
    global res
    global time_text
    global time_template
    global line1
    global line2
    global line_v1_t
    global line_v1_join
    global line_v1_c



    lm = neurounits.NeuroUnitParser.Parse9MLFile(ball_arena_text)
    ball_arena = lm.get('ball_arena')



    res=  ball_arena.simulate(
            times = np.linspace(0,70,num=5000),
            parameters={
                },
            initial_state_values= {
                'B1VX':'3m/s',
                'B1VY':'5m/s',
                'B1X':'3.5m',
                'B1Y':'2.5m',

                'B2VX':'-3m/s',
                'B2VY':'-5m/s',
                'B2X':'6.5m',
                'B2Y':'7.5m',
                't_last':'0s',
                },
            initial_regimes = {

                },
            )

    print res
    print res.state_variables
    print res.events




    ##
    ##   set up figure for plotting:
    ##
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # I'm still unfamiliar with the following line of code:
    line1, = ax.plot([], [], 'bo', ms=10)
    line2, = ax.plot([], [], 'go', ms=10)
    line_v1_join, = ax.plot([], [], 'm-')

    line_v1_t, = ax.plot([], [], 'r-', )
    line_v1_c, = ax.plot([], [], 'c-', )

    ax.set_ylim(-2, 12)
    ax.set_xlim(-2, 12)
    ax.axhline(0, ls='--')
    ax.axhline(10, ls='--')
    ax.axvline(0, ls='--')
    ax.axvline(10, ls='--')

    time_template = 'Time = %.1f s'    # prints running simulation time
    time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
    plt.title('NineML bouncing ball simulation (test_nineml2.py)')
    ## Now call the animation package: (simData is the user function
    ## serving as the argument for simPoints):
    ani = animation.FuncAnimation(fig, simPoints, simData, blit=False, interval=1, repeat=True, save_count=1000)

    #ani.save('myoutput.avi', writer='ffmpeg', bitrate=200, fps=20, codec='ffv1' )#extra_args=['-vcodec huffyuv']) # codec='ffv1')
    try:
        ani.save('myoutput.avi', fps=40, codec='ffv1' )#extra_args=['-vcodec huffyuv']) # codec='ffv1')
    except:
        print 'Unable to save video (issue with matplotlib)'
    #writer='ffmpeg',








if __name__=='__main__':
    test2()
    import pylab
    pylab.show()






