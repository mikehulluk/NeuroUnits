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
import pylab


neuron_def = r'''
library my_neuro {
    from std.math import pow
    RateConstant5(V:{V},a1:{s-1} ,a2:{V-1 s-1 }, a3:{},a4:{V},a5:{V} ) = (a1 + a2*V)/(a3+std.math.exp( (V+a4)/a5) )

    ClipInf(inf:{}) = [0.0] if [inf<0.0] else [[1.0] if [inf>1.0]  else [inf]]
    ClipTau(tau:{s},tau_min:{s}) = [tau_min] if [tau<tau_min] else [tau]
}

define_component my_din {

    from my_neuro import RateConstant5, ClipInf, ClipTau
    from std.physics import F,R
    from std.math import exp

    # Sodium Channels:
    m_alpha_rate = RateConstant5(V=V, a1={8.67 ms-1}, a2={0.0mV-1 ms-1}, a3=1.000000, a4={-1.01mV}, a5={-12.56mV})
    m_beta_rate  = RateConstant5(V=V, a1={3.82 ms-1}, a2={0.0mV-1 ms-1}, a3=1.000000, a4={ 9.01mV}, a5={  9.69mV})
    h_alpha_rate = RateConstant5(V=V, a1={0.08 ms-1}, a2={0.0mV-1 ms-1}, a3=0.000000, a4={38.88mV}, a5={ 26.00mV})
    h_beta_rate  = RateConstant5(V=V, a1={4.08 ms-1}, a2={0.0mV-1 ms-1}, a3=1.000000, a4={-5.09mV}, a5={-10.21mV})

    minf = m_alpha_rate / (m_alpha_rate + m_beta_rate)
    mtau = 1.0 / (m_alpha_rate + m_beta_rate)
    m' = (minf-m) / mtau
    hinf = h_alpha_rate / (h_alpha_rate + h_beta_rate)
    htau = 1.0 / (h_alpha_rate + h_beta_rate)
    h' = (hinf-h) / htau
    i_na_bar = g_na * (e_na-V) * m**3*h

    # K-slow channels:
    ks_alpha_rate = RateConstant5(V=V, a1={0.462 ms-1}, a2={8.2e-3mV-1 ms-1}, a3=4.59, a4={-4.21mV}, a5={-11.97mV})
    ks_beta_rate  = RateConstant5(V=V, a1={0.0924 ms-1}, a2={-1.353e-3mV-1 ms-1}, a3=1.615, a4={2.1e5mV}, a5={3.33e5mV})
    ksinf = ks_alpha_rate / (ks_alpha_rate + ks_beta_rate)
    kstau = 1.0 / (ks_alpha_rate + ks_beta_rate)
    ks' = (ksinf-ks) / kstau
    i_ks_bar = g_ks * (e_k-V) * ks**2

    # K-fast channels:
    kf_alpha_rate = RateConstant5(V=V, a1={5.06 ms-1}, a2={0.0666mV-1 ms-1}, a3=5.12, a4={-18.396mV}, a5={-25.42mV})
    kf_beta_rate  = RateConstant5(V=V, a1={0.505 ms-1}, a2={0mV-1 ms-1}, a3=0, a4={28.7mV}, a5={34.6mV})
    kfinf = kf_alpha_rate / (kf_alpha_rate + kf_beta_rate)
    kftau = 1.0 / (kf_alpha_rate + kf_beta_rate)
    kf' = (kfinf-kf) / kftau
    i_kf_bar = g_kf * (e_k-V) * kf**4

    # Leak Currents:
    i_lk_bar = g_lk * (e_lk-V)

    # Ca currents:
    ca_m_alpha = RateConstant5(V=V, a1={4.05 ms-1}, a2={0.0   mV-1 ms-1}, a3= 1.0, a4={-15.32mV}, a5={-13.57mV} )
    ca_m_beta1 = RateConstant5(V=V, a1={1.24 ms-1}, a2={0.093 mV-1 ms-1}, a3=-1.0, a4={ 10.63mV}, a5={  1.00mV} )
    ca_m_beta2 = RateConstant5(V=V, a1={1.28 ms-1}, a2={0.0   mV-1 ms-1}, a3= 1.0, a4={  5.39mV}, a5={ 12.11mV} )
    ca_m_beta = [ca_m_beta1] if [V<{-25mV}] else [ca_m_beta2]
    ca_m_tau =  ClipTau( tau=1/(ca_m_alpha+ca_m_beta), tau_min={0.11ms} )
    ca_m_inf =  ClipInf( ca_m_alpha/(ca_m_alpha+ca_m_beta) )
    ca_m'= (ca_m_inf - ca_m) / ca_m_tau

    up = 2 * V * F / (R*T)
    ica_ungated = pca * 2 * up * F * (CAi - CAo*exp(-1.0*up) ) / (1-exp(-1.0*up) )
    i_ca_bar = ica_ungated * ca_m**2


    T = 300 K
    pca = {0.016cm/s} * 100

    CAi = 100nM
    CAo = 10uM

    area = 1000um2
    C = {1uF/cm2} * area
    g_na = {0.025 S/cm2} * 2
    e_na = 50 mV
    g_ks = {1.0 mS/cm2}
    e_k = -81 mV
    g_kf = {1.25 mS/cm2}
    g_lk = {0.00025 S/cm2}
    e_lk = -52mV



    # Injected Currents:
    i_Inj = [100pA] if [t>50ms and t<1000ms] else [0pA]



    # Convert densities into absolute values:
    i_lk = i_lk_bar * area
    i_na = i_na_bar * area
    i_ks = i_ks_bar * area
    i_kf = i_kf_bar * area
    i_ca = i_ca_bar * area

    # Simulated equation:
    V' = (i_lk + i_na + i_kf + i_ks +  i_ca + i_Inj) / C

    <=> output    V
    <=> input    t

    initial {
        V = -80mV
        ks = 0
        m=0
        h=0
        kf=0
        ca_m=0
    }


    }
'''



from neurounitscontrib.demo import DemoPluginBase
class Demo6(DemoPluginBase):


    def get_name(self):
        return '6'

    def run(self, args):
        test6()


def test6():
    import neurounits
    import numpy as np


    lm = neurounits.NeuroUnitParser.Parse9MLFile(neuron_def)

    nrn = lm.get('my_din')


    res = nrn.simulate(times=np.linspace(0.0, 0.100, 10000))
    res.auto_plot()


def main():
    test6()
    pylab.show()




if __name__ == '__main__':
    main()
