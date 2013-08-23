

import neurounits
from neurounits.ast_annotations.common import NodeRangeAnnotator, NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator, _NodeRangeFloat, RangeExpander


def get_dIN(nbits):
    src_text = """
    define_component simple_hh {
        from std.math import exp, ln

        #iInj_local = [{50pA} * k] if [t > 75ms and t< 85ms or t<1ms] else [0pA]
        iInj_local = [{50pA} * k] if [t > 75ms and t< 185ms or t<1ms] else [0pA]
        Cap = 10 pF

        V' = (1/Cap) * (iInj_local + i_injected + iLk + iKs + iKf +iNa + i_nmda )



        # NMDA noise:
        # =======================
        syn_nmda_A_tau = 4ms
        syn_nmda_B_tau = 80ms
        i_nmda = g_nmda * (syn_nmda_B - syn_nmda_A) * (e_NMDA - V) * nmda_vdep  * 0.5
        syn_nmda_A' = -syn_nmda_A / syn_nmda_A_tau
        syn_nmda_B' = -syn_nmda_B / syn_nmda_B_tau
        # TOOO:
        #nmda_tc_max = (syn_nmda_A_tau * syn_nmda_B_tau) * ln( syn_nmda_B_tau / syn_nmda_A_tau)
        g_nmda = 300pS
        e_NMDA = 0mV

        v_scale = V * {-0.08mV-1}
        nmda_vdep =  1./(1. + 0.05 * exp(v_scale) )

        on recv_nmda_spike(){

            syn_nmda_A = syn_nmda_A + 1.0
            syn_nmda_B = syn_nmda_B + 1.0
        }
        # ===========================





        noise_min = 0.5
        noise_max = 1.5

        glk_noise1 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]
        glk_noise2 =  ~uniform(min=noise_min, max=noise_max + eK/{1V})[when=SIM_INIT, share=PER_POPULATION]
        glk_noise3 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_POPULATION]
        glk_noise4 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]


        glk_noise = (glk_noise1 + glk_noise2 ) / 4.0



        AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))

        eK = -80mV
        eNa = 50mV
        gKs = 10.0 nS
        gKf = 12.5 nS
        gNa = 250 nS
        gLk = 1.25 nS
        eLk = -50mV

        # Leak
        iLk = gLk * (eLk-V) * glk_noise

        # Slow Potassium (Ks):
        alpha_ks_n = AlphaBetaFunc(v=V, A=0.462ms-1, B=8.2e-3ms-1 mV-1, C=4.59, D=-4.21mV,E=-11.97mV)
        beta_ks_n =  AlphaBetaFunc(v=V, A=0.0924ms-1, B=-1.353e-3ms-1 mV-1, C=1.615, D=2.1e5mV, E=3.3e5mV)
        inf_ks_n = alpha_ks_n / (alpha_ks_n + beta_ks_n)
        tau_ks_n = 1.0 / (alpha_ks_n + beta_ks_n)
        ks_n' = (inf_ks_n - ks_n) / tau_ks_n
        iKs = gKs * (eK-V) * ks_n*ks_n


        # Fast potassium (Kf):
        alpha_kf_n = AlphaBetaFunc(v=V, A=5.06ms-1, B=0.0666ms-1 mV-1, C=5.12, D=-18.396mV,E=-25.42mV)
        beta_kf_n =  AlphaBetaFunc(v=V, A=0.505ms-1, B=0.0ms-1 mV-1, C=0.0, D=28.7mV, E=34.6mV)
        inf_kf_n = alpha_kf_n / (alpha_kf_n + beta_kf_n)
        tau_kf_n = 1.0 / (alpha_kf_n + beta_kf_n)
        kf_n' = (inf_kf_n - kf_n) / tau_kf_n
        iKf = gKf * (eK-V) * kf_n2 #kf_n*kf_n * kf_n*kf_n
        kf_n2 = kf_n*kf_n * kf_n * kf_n

        # Sodium (Kf):
        alpha_na_m = AlphaBetaFunc(v=V, A=8.67ms-1, B=0.0ms-1 mV-1, C=1.0, D=-1.01mV,E=-12.56mV)
        beta_na_m =  AlphaBetaFunc(v=V, A=3.82ms-1, B=0.0ms-1 mV-1, C=1.0, D=9.01mV, E=9.69mV)
        inf_na_m = alpha_na_m / (alpha_na_m + beta_na_m)
        tau_na_m = 1.0 / (alpha_na_m + beta_na_m)
        na_m' = (inf_na_m - na_m) / tau_na_m

        alpha_na_h = AlphaBetaFunc(v=V, A=0.08ms-1, B=0.0ms-1 mV-1, C=0.0, D=38.88mV,E=26.0mV)
        beta_na_h =  AlphaBetaFunc(v=V, A=4.08ms-1, B=0.0ms-1 mV-1, C=1.0, D=-5.09mV, E=-10.21mV)
        inf_na_h = alpha_na_h / (alpha_na_h + beta_na_h)
        tau_na_h = 1.0 / (alpha_na_h + beta_na_h)
        na_h' = (inf_na_h - na_h) / tau_na_h

        iNa = gNa * (eNa-V) * na_m * na_m * na_m * na_h * glk_noise1


        # Calcium:
        #beta_ca_m =  [beta_ca_m_1] if [ V<-25mV] else [beta_ca_m_2]
        #beta_ca_m =  [AlphaBetaFunc(v=V, A=1.24ms-1, B=0.093ms-1 mV-1, C=-1.0, D=10.63mV, E=1.0mV)] if [V<-25mV] else [beta_ca_m_2] 
        #beta_ca_m_1 =  ({1.24ms-1} + {0.093ms-1 mV-1} * V) / (exp(({10.63mV}+V)/{1.0mV}) -{1.0})  
        #ca_m' =  (ca_m_inf - ca_m) / tau_ca_m_cl
        #ca_m' =  (ca_m_inf - ca_m) / tau_ca_m_cl
        #tau_ca_m_cl = [tau_ca_m] if [tau_ca_m > 0.3ms] else [0.3ms]
        #ca_m' = 0ms-1

        alpha_ca_m = AlphaBetaFunc(v=V, A=4.05ms-1, B=0.0ms-1 mV-1, C=1.0, D=-15.32mV,E=-13.57mV)
        #beta_ca_m_1 =  AlphaBetaFunc(v=V, A=1.24ms-1, B=0.093ms-1 mV-1, C=-1.0, D=10.63mV, E=1.0mV)
        beta_ca_m_1 =  V * {-0.0923 ms-1 mV-1} - {1.2 ms-1}
        beta_ca_m_2 =  AlphaBetaFunc(v=V, A=1.28ms-1, B=0.0ms-1 mV-1, C=1.0, D=5.39mV, E=12.11mV)
        beta_ca_m =  [beta_ca_m_1] if [V<-25mV] else [beta_ca_m_2] 
        ca_m_inf = alpha_ca_m / (alpha_ca_m + beta_ca_m)
        tau_ca_m = 1.0 / (alpha_ca_m + beta_ca_m)
        ca_m' =  (ca_m_inf - ca_m) / tau_ca_m
        

        pca = {0.16 (m m m)/s} * 1e-6 * 1e-5
        F = 96485 C / mol
        R = 8.3144 J/ (mol K)
        T = 300K
        Cai = 100 nM
        Cao = 10 mM
        nu = ( (2.0 *  F) / (R*T) ) * V ;
        exp_neg_nu = exp( -1. * nu );
        #iCa =  -2.0 * 1.e-3 * pca * nu * F * (( Cai - Cao*exp_neg_nu) / (1-exp_neg_nu)) *  ca_m * ca_m
        iCa = [4pA] if [t < 0ms] else [4pA]
        iCa2 =  -3pA


        <=> INPUT t:(ms)
        <=> INPUT i_injected:(mA)

        k'=0 s-1



        regime sub{
            on (V > 0V) {
                k=0
                emit spike()
                transition_to super
            };
        }
        regime super{
           on (V < 0V) {
               k=1
            transition_to sub
            };
        }


        initial {
            V = -60mV
            k=1
            na_m = 0.0
            ca_m = 0.0
            na_h = 1.0
            ks_n = 0.0
            kf_n = 0.0

           syn_nmda_B = 0.0
           syn_nmda_A = 0.0
            regime sub
        }


    }



    """




    var_annots_ranges = {
        't'             : NodeRange(min="0ms", max = "1.1s"),
        'i_injected'    : NodeRange(min="0nA", max = "10nA"),
        'V'             : NodeRange(min="-100mV", max = "50mV"),
        'k'             : NodeRange(min="0", max = "1.1"),
        'ca_m'          : NodeRange(min="0", max = "1.5"),
        'kf_n'          : NodeRange(min="0", max = "1.5"),
        'ks_n'          : NodeRange(min="0", max = "1.5"),
        'na_h'          : NodeRange(min="0", max = "1.5"),
        'na_m'          : NodeRange(min="0", max = "1.5"),
        'syn_nmda_A'    : NodeRange(min='0', max ='30'),
        'syn_nmda_B'    : NodeRange(min='0', max ='30'),
        }

    var_annots_tags = {
        'V': 'Voltage',
        'V': 'Voltage',


        'syn_nmda_A':'',
        'syn_nmda_B' : '',
        'i_nmda' : '',
        'nmda_vdep' :'',
        'iLk' : '',
        'iKf' : '',
        'kf_n': '',
        'iInj_local': '',

    }



    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_hh']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)

    comp.annotate_ast( NodeRangeAnnotator(var_annots_ranges) )
    RangeExpander().visit(comp)
    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    from neurounits.ast_annotations.common import NodeTagger
    #NodeTagger(var_annots_tags).visit(comp)

    return comp

