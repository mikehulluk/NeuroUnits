

neuron_def = r'''
library my_neuro {
    from std.math import pow
    RateConstant5(V:(V),a1:(s-1 ) ,a2:(V-1 s-1 ), a3:(),a4:(V),a5:(V) ) = (a1 + a2*V)/(a3+std.math.exp( (V+a4)/a5) )

    ClipInf(inf:()) = [0.0] if [inf<0.0] else [[1.0] if [inf>1.0]  else [inf]]
    ClipTau(tau:(s),tau_min:(s)) = [tau_min] if [tau<tau_min] else [tau]
}

eqnset my_din {

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
    g_na = {0.025 S/cm2}
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

    <=> OUTPUT    V
    <=> INPUT    t
    }



'''






import neurounits
import numpy as np
import pylab
from neurounits.writers.writer_ast_to_simulatable_object import EqnSimulator




library_manager = neurounits.NeuroUnitParser.File(neuron_def)
from neurounits import NeuroUnitParser as P


print library_manager



evaluator = EqnSimulator( library_manager.eqnsets[0] )
res = evaluator(
        time_data = np.linspace(0.0, 0.100, 1000),
        params={
            },
        state0In={
            'V':P.QuantityExpr('-52mV'),
            'm':P.QuantityExpr('0'),
            'h':P.QuantityExpr('0'),
            'kf':P.QuantityExpr('0'),
            'ks':P.QuantityExpr('0'),
            'ca_m':P.QuantityExpr('0'),
            }
        )

print 'Done Simulating'
print res
print res.keys()


#pylab.figure()
#pylab.plot(res['x'], res['y'])

fig = pylab.figure()

ax1 = fig.add_subplot(611)
ax2 = fig.add_subplot(612)
ax3 = fig.add_subplot(613)
ax4 = fig.add_subplot(614)
ax5 = fig.add_subplot(615)
ax6 = fig.add_subplot(616)

ax1.plot(res['t'], res['V'],'x-')

ax2.plot(res['t'], res['i_na_bar'])
#ax2.plot(res['t'], res['i_lk_bar'])
#ax2.plot(res['t'], res['i_ks_bar'])
#ax2.plot(res['t'], res['i_kf_bar'])
ax2.plot(res['t'], res['i_ca_bar'])
#ax5.plot(res['t'], res['i_ca_bar'])



#ax3.plot(res['t'], res['m'], 'b')
#ax3.plot(res['t'], res['h'], 'g')
#ax3.plot(res['t'], res['ks'], 'm')
#ax3.plot(res['t'], res['kf'], 'm')
ax3.plot(res['t'], res['ca_m'],'r')


ax4.plot(res['t'], res['i_na']  ,label='na')
#ax4.plot(res['t'], res['i_lk']  ,label='lk')
#ax4.plot(res['t'], res['i_ks']  ,label='ks')
#ax4.plot(res['t'], res['i_kf']  ,label='kf')
ax4.plot(res['t'], res['i_ca']  ,label='ca')
ax6.plot(res['t'], res['i_ca']  ,label='ca')
#ax4.plot(res['t'], res['i_Inj'] ,label='iinj')

ax4.legend()






#ax1.plot(res['t'], res['i_Inj'])
ax1.margins( 0.1)
ax2.margins( 0.1)
ax3.margins( 0.1)
ax4.margins( 0.1)


pylab.show()
