

import neurounits
from neurounits.ast_annotations.common import  NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_dIN(nbits):
    src_text = """
    define_component simple_hh {
        from std.math import exp, ln

        <=> TIME t:(ms)
        <=> INPUT i_injected:(mA)
        <=> PARAMETER nmda_multiplier:()
        <=> PARAMETER ampa_multiplier:()

        #iInj_local = [50pA] if [ 50ms < t < 200ms] else [0pA] * 0.0
        iInj_local = 0pA





        Cap = 10 pF

        V' = (1/Cap) * ( itot)
        itot = iLk + iInj_local + iKs + iKf +iNa + iCa +  syn_nmda_i + syn_ampa_i + syn_inhib_i +  i_injected


        k = i_injected

        ##V_noisy = V + ~ar_model(0.3) * {2mV}
        ##V_vnoisy = V_noisy + ~ar_model() * 1mV + ~ar_model(p0=0.3,p1=0.3) * {3mV}
        ##noise = ~ar_model(0.3) * {3mV}
        ##noise_raw = ~ar_model()

        ClipMax(x, x_max) = [x] if [x<x_max] else [x_max]



        syn_sat = 1
        syn_nmda_g_bar =  1nS * nmda_multiplier
        syn_ampa_g =  1nS * ampa_multiplier
        syn_inhib_g = 1nS



        # Functions for working out the scaling factors of synapses, based on
        # their time constants:
        #_SynTimeMax(tc_open,tc_close) = ln( tc_close / tc_open) * (tc_open * tc_close) / (tc_close - tc_open)
        #SynScale(tc_open,tc_close) = 1 / (  exp( -_SynTimeMax(tc_open=tc_open, tc_close=tc_close) / tc_close) -  exp( -_SynTimeMax(tc_open=tc_open, tc_close=tc_close) / tc_open)  )



        # NMDA
        # =======================
        syn_nmda_A_tau = 4ms
        syn_nmda_B_tau = 80ms
        syn_nmda_i = ( syn_nmda_g_raw * (syn_nmda_erev - V) * nmda_vdep )
        #syn_nmda_g_raw = ( syn_nmda_g_bar * (syn_nmda_B - syn_nmda_A) * SynScale(tc_open=syn_nmda_A_tau, tc_close=syn_nmda_B_tau ) )
        syn_nmda_g_raw = ( syn_nmda_g_bar * (syn_nmda_B - syn_nmda_A) *  (1/nmda_val_max) )
        syn_nmda_A' = -syn_nmda_A / syn_nmda_A_tau
        syn_nmda_B' = -syn_nmda_B / syn_nmda_B_tau
        # Normalisation:
        nmda_tc_max =  ln( syn_nmda_B_tau / syn_nmda_A_tau) * (syn_nmda_A_tau * syn_nmda_B_tau) / (syn_nmda_B_tau - syn_nmda_A_tau)
        nmda_val_max = (  exp( -nmda_tc_max / syn_nmda_B_tau) -  exp( -nmda_tc_max / syn_nmda_A_tau)  )
        syn_nmda_erev = 0mV
        v_scale = V * {-0.08mV-1}
        nmda_vdep =  1./(1. + 0.05 * exp(v_scale) )
        on recv_nmda_spike(weight:(S)){
            syn_nmda_A = syn_nmda_A + (weight/{1nS})
            syn_nmda_B = syn_nmda_B + (weight/{1nS})
        }
        # ===========================


        # AMPA
        # =======================
        syn_ampa_A_tau = 0.1ms
        syn_ampa_B_tau = 3ms
        syn_ampa_i = syn_ampa_g * (syn_ampa_B - syn_ampa_A) * (syn_ampa_erev - V)  *(1/ampa_val_max)
        syn_ampa_A' = -syn_ampa_A / syn_ampa_A_tau
        syn_ampa_B' = -syn_ampa_B / syn_ampa_B_tau

        # Normalisation:
        ampa_tc_max =  ln( syn_ampa_B_tau / syn_ampa_A_tau) * (syn_ampa_A_tau * syn_ampa_B_tau) / (syn_ampa_B_tau - syn_ampa_A_tau)
        ampa_val_max =  (exp( -ampa_tc_max / syn_ampa_B_tau) -  exp( -ampa_tc_max / syn_ampa_A_tau) )
        syn_ampa_erev = 0mV
        on recv_ampa_spike(weight:(S)){
            syn_ampa_A = syn_ampa_A + (weight/{1nS})
            syn_ampa_B = syn_ampa_B + (weight/{1nS})
        }
        # ===========================

        # Inhibitory
        # =======================
        syn_inhib_A_tau = 1.5ms
        syn_inhib_B_tau = 4ms
        syn_inhib_i = (syn_inhib_g * (syn_inhib_B - syn_inhib_A) * (syn_inhib_erev - V)  * (1/inhib_val_max))
        syn_inhib_A' = -syn_inhib_A / syn_inhib_A_tau
        syn_inhib_B' = -syn_inhib_B / syn_inhib_B_tau
        # Normalisation:
        inhib_tc_max =  ln( syn_inhib_B_tau / syn_inhib_A_tau) * (syn_inhib_A_tau * syn_inhib_B_tau) / (syn_inhib_B_tau - syn_inhib_A_tau)
        inhib_val_max =  ( exp( -inhib_tc_max / syn_inhib_B_tau) -  exp( -inhib_tc_max / syn_inhib_A_tau)  )
        syn_inhib_erev = -60mV
        on recv_inh_spike(weight:(S)){
            syn_inhib_A = syn_inhib_A + (weight/{1nS})
            syn_inhib_B = syn_inhib_B + (weight/{1nS})
        }
        # ===========================

        noise_min = 0.5
        noise_max = 1.5

        #glk_noise1 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]
        #glk_noise2 =  ~uniform(min=noise_min, max=noise_max + eK/{1V})[when=SIM_INIT, share=PER_POPULATION]
        #glk_noise3 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_POPULATION]
        #glk_noise4 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]

        glk_noise1 = 1
        glk_noise2 = 1
        glk_noise3 = 1
        glk_noise4 = 1

        glk_noise = (glk_noise1 + glk_noise2 + glk_noise3 + glk_noise4 ) / 4.0



        AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))

        eK = -80mV
        eNa = 50mV
        gKs = 10.0 nS
        gKf = 12.5 nS
        gNa = 250 nS
        gLk = 1.25 nS
        eLk = -52mV

        # Leak
        iLk = gLk * (eLk-V) * glk_noise
        #iLk = gLk * (eLk-V)

        # Slow Potassium (Ks):
        alpha_ks_n = AlphaBetaFunc(v=V, A=0.462ms-1, B=8.2e-3ms-1 mV-1, C=4.59, D=-4.21mV,E=-11.97mV)
        beta_ks_n =  ({0.0924ms-1} + V*{-1.353e-3ms-1 mV-1}) / ({1.615} + 1.88959 )

        inf_ks_n = alpha_ks_n / (alpha_ks_n + beta_ks_n)
        tau_ks_n = 1.0 / (alpha_ks_n + beta_ks_n)
        ks_n' = (inf_ks_n - ks_n) / tau_ks_n
        iKs = gKs * (eK-V) * ks_n*ks_n


        # Fast potassium (Kf):
        alpha_kf_n = AlphaBetaFunc(v=V, A=5.06ms-1, B=0.0666ms-1 mV-1, C=5.12, D=-18.396mV,E=-25.42mV)
        beta_kf_n =  {0.505ms-1} * exp( ( {28.7mV} + V) / {-34.6mV} )

        inf_kf_n = alpha_kf_n / (alpha_kf_n + beta_kf_n)
        tau_kf_n = 1.0 / (alpha_kf_n + beta_kf_n)
        kf_n' = (inf_kf_n - kf_n) / tau_kf_n
        iKf = gKf * (eK-V) * kf_n4
        kf_n4 = kf_n * kf_n * kf_n * kf_n

        # Sodium (Na):
        alpha_na_m = AlphaBetaFunc(v=V, A=8.67ms-1, B=0.0ms-1 mV-1, C=1.0, D=-1.01mV,E=-12.56mV)
        beta_na_m =  AlphaBetaFunc(v=V, A=3.82ms-1, B=0.0ms-1 mV-1, C=1.0, D=9.01mV, E=9.69mV)
        inf_na_m = alpha_na_m / (alpha_na_m + beta_na_m)
        tau_na_m = 1.0 / (alpha_na_m + beta_na_m)
        na_m' = (inf_na_m - na_m) / tau_na_m

        alpha_na_h = {0.08ms-1} * exp( ({38.88mV}+V) / {-26.0mV} )

        #alpha_na_h = AlphaBetaFunc(v=V, A=0.08ms-1, B=0.0ms-1 mV-1, C=0.0, D=38.88mV,E=26.0mV)
        beta_na_h =  AlphaBetaFunc(v=V, A=4.08ms-1, B=0.0ms-1 mV-1, C=1.0, D=-5.09mV, E=-10.21mV)

        inf_na_h = alpha_na_h / (alpha_na_h + beta_na_h)
        tau_na_h = 1.0 / (alpha_na_h + beta_na_h)
        na_h' = (inf_na_h - na_h) / tau_na_h

        iNa = gNa * (eNa-V) * na_m * na_m * na_m * na_h * glk_noise1


        # Calcium:
        alpha_ca_m = AlphaBetaFunc(v=V, A=4.05ms-1, B=0.0ms-1 mV-1, C=1.0, D=-15.32mV,E=-13.57mV)
        beta_ca_m_1 =  V * {-0.0923 ms-1 mV-1} - {1.2 ms-1}
        beta_ca_m_2 =  AlphaBetaFunc(v=V, A=1.28ms-1, B=0.0ms-1 mV-1, C=1.0, D=5.39mV, E=12.11mV)
        beta_ca_m =  [beta_ca_m_1] if [V<-25mV] else [beta_ca_m_2]
        ca_m_inf = alpha_ca_m / (alpha_ca_m + beta_ca_m)
        tau_ca_m = 1.0 / (alpha_ca_m + beta_ca_m)

        ca_m_inf_cl = ClipMax(x=ca_m_inf, x_max=1.0 )
        ca_m' =  (ca_m_inf_cl - ca_m) / tau_ca_m


        ff = 1.0
        pca = {0.16 (mm3)/s} * 1e-6 * ff
        F = 96485 C / mol
        R = 8.3144 J/ (mol K)
        T = 300K
        Cai = 100 nM
        Cao = 10 mM
        z = 2.0
        nu = ( (z *  F) / (R*T) ) * V ;
        exp_neg_nu = exp( -1. * nu )
        #ca_v_eps = 1e-2mV
        ca_v_eps = 10e-1mV
        #iCa_ungated =  [-z *  pca *  F * ( (nu*( Cai - Cao*exp_neg_nu) ) / (1-exp_neg_nu)) ]
        iCa_ungated =  [ -z *  pca *  F * ( (nu*( Cai - Cao*exp_neg_nu) ) / (1-exp_neg_nu)) ] \
                            if [ (V > ca_v_eps) or (V < -ca_v_eps)] \
                            else [pca * (-z) * F * (Cai-Cao) ]

        iCa_disp = [2.9e-10] if [ (V > ca_v_eps) or (V < -ca_v_eps) ] else [3.1e-10]
        iCa =  iCa_ungated *  ca_m * ca_m



        on (V crosses (rising) 0V) and (t>3ms)  {
            emit spike()
        };

        on ( V crosses (falling) 0V ) {
            emit falling_spike()
        };

        regime sub{

        }

        #regime sub{
        #    on (V > 0mV) {
        #        emit spike()
        #        transition_to super
        #    };
        #}
        #regime super{
        #   #on (V < -10mV) {
        #   on (V < 0mV) {
        #    transition_to sub
        #    };
        #}


        initial {
            V = -60mV
            na_m = 0.0
            ca_m = 0.0
            #ca_m2 = 0.0
            na_h = 1.0
            ks_n = 0.0
            kf_n = 0.0

            syn_nmda_B = 0.0
            syn_nmda_A = 0.0
            syn_ampa_B = 0.0
            syn_ampa_A = 0.0
            syn_inhib_B = 0.0
            syn_inhib_A = 0.0

            regime sub
        }


    }



    """




    var_annots_ranges = {
        't'             : NodeRange(min="0ms", max = "1.1s"),
        'i_injected'    : NodeRange(min="-1500pA", max = "1500pA"),
        'V'             : NodeRange(min="-100mV", max = "60mV"),
        'ca_m'          : NodeRange(min="-0.01", max = "1.3"),
        'kf_n'          : NodeRange(min="-0.01", max = "1.3"),
        'ks_n'          : NodeRange(min="-0.01", max = "1.3"),
        'na_h'          : NodeRange(min="-0.01", max = "1.3"),
        'na_m'          : NodeRange(min="-0.01", max = "1.3"),
        'syn_nmda_A'    : NodeRange(min='0', max ='50'),
        'syn_nmda_B'    : NodeRange(min='0', max ='50'),
        'syn_ampa_A'    : NodeRange(min='0', max ='50'),
        'syn_ampa_B'    : NodeRange(min='0', max ='50'),
        'syn_inhib_A'    : NodeRange(min='0', max ='50'),
        'syn_inhib_B'    : NodeRange(min='0', max ='50'),
        'recv_ampa_spike::weight': NodeRange(min='0nS',max='10nS'),
        'recv_nmda_spike::weight': NodeRange(min='0nS',max='10nS'),
        'recv_inh_spike::weight': NodeRange(min='0nS',max='10nS'),

        'nmda_multiplier' : NodeRange(min='0',max='2'),
        'ampa_multiplier' : NodeRange(min='0',max='2'),
        }

    var_annots_tags = {
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
    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))
    RangeExpander().visit(comp)




    from neurounits.ast_annotations.common import NodeTagger
    NodeTagger(var_annots_tags).visit(comp)

    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )


    return comp



from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('dIN', get_dIN )
