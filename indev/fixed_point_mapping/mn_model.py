


import neurounits
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator,NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_MN(nbits):
    src_text = """
    define_component simple_hh_MN {
        from std.math import exp, ln

        <=> INPUT t:(ms)
        <=> INPUT i_injected:(mA)

        iInj_local = {0pA/ms} * t

        #iInj_local = [40pA] if [ 100ms < t < 200ms] else [0pA]

        Cap = 10 pF

        V' = (1/Cap) * (iInj_local + i_injected + iLk  + iKs + iKf +iNa +  syn_nmda_i + syn_ampa_i + syn_inhib_i)


        AlphaBetaFunc(v, A,B,C,D,E) = (A+B*v) / (C + exp( (D+v)/E))
        ClipMax(x, x_max) = [x] if [x<x_max] else [x_max]

        # NMDA
        # =======================
        syn_nmda_A_tau = 4ms
        syn_nmda_B_tau = 80ms
        syn_nmda_i = ( syn_nmda_g * (syn_nmda_B - syn_nmda_A) * (syn_nmda_erev - V) * (1/nmda_val_max) * nmda_vdep )  * 0
        syn_nmda_A' = -syn_nmda_A / syn_nmda_A_tau
        syn_nmda_B' = -syn_nmda_B / syn_nmda_B_tau
        # Normalisation:
        nmda_tc_max =  ln( syn_nmda_A_tau / syn_nmda_B_tau) * (syn_nmda_A_tau * syn_nmda_B_tau) / (syn_nmda_A_tau - syn_nmda_B_tau)
        nmda_val_max =  (exp( -nmda_tc_max / syn_ampa_B_tau) -  exp( -nmda_tc_max / syn_ampa_A_tau) ) 
        syn_nmda_g = 100pS
        syn_nmda_erev = 0mV
        v_scale = V * {-0.08mV-1}
        nmda_vdep =  1./(1. + 0.05 * exp(v_scale) )
        on recv_nmda_spike(){
            syn_nmda_A = ClipMax( x=syn_nmda_A + 1.0, x_max=syn_sat )
            syn_nmda_B = ClipMax( x=syn_nmda_B + 1.0, x_max=syn_sat )
        }
        # ===========================


        # AMPA
        syn_sat = 30
        # =======================
        syn_ampa_A_tau = 0.1ms
        syn_ampa_B_tau = 3ms
        syn_ampa_i = ( syn_ampa_g * (syn_ampa_erev - V)  * syn_ampa_open ) 
        syn_ampa_open = (syn_ampa_B - syn_ampa_A) * (1/ampa_val_max)
        syn_ampa_A' = -syn_ampa_A / syn_ampa_A_tau
        syn_ampa_B' = -syn_ampa_B / syn_ampa_B_tau

        # Normalisation:
        ampa_tc_max =  ln( syn_ampa_A_tau / syn_ampa_B_tau) * (syn_ampa_A_tau * syn_ampa_B_tau) / (syn_ampa_A_tau - syn_ampa_B_tau)
        ampa_val_max =  (exp( -ampa_tc_max / syn_ampa_B_tau) -  exp( -ampa_tc_max / syn_ampa_A_tau) ) 
        syn_ampa_g = 600pS 
        syn_ampa_erev = 0mV
        on recv_ampa_spike(){
            syn_ampa_A = ClipMax( x=syn_ampa_A + 1.0, x_max=syn_sat )
            syn_ampa_B = ClipMax( x=syn_ampa_B + 1.0, x_max=syn_sat )
            #syn_ampa_A = syn_ampa_A + 1.0
            #syn_ampa_B = syn_ampa_B + 1.0
        }
        # ===========================

        # Inhibitory
        # =======================
        syn_inhib_A_tau = 1.5ms
        syn_inhib_B_tau = 4ms
        syn_inhib_i = ( syn_inhib_g * (syn_inhib_B - syn_inhib_A) * (syn_inhib_erev - V)  * (1/inhib_val_max) )
        syn_inhib_A' = -syn_inhib_A / syn_inhib_A_tau
        syn_inhib_B' = -syn_inhib_B / syn_inhib_B_tau
        # Normalisation:
        inhib_tc_max =  ln( syn_inhib_A_tau / syn_inhib_B_tau) * (syn_inhib_A_tau * syn_inhib_B_tau) / (syn_inhib_A_tau - syn_inhib_B_tau)
        inhib_val_max = ( exp( -inhib_tc_max / syn_inhib_B_tau) -  exp( -inhib_tc_max / syn_inhib_A_tau) ) 
        syn_inhib_g = 300pS
        syn_inhib_erev = -60mV
        on recv_inh_spike(){
            syn_inhib_A = ClipMax( x=syn_inhib_A + 1.0, x_max=syn_sat * 3 )
            syn_inhib_B = ClipMax( x=syn_inhib_B + 1.0, x_max=syn_sat * 3)
            #syn_inhib_A = syn_inhib_A + 1.0
            #syn_inhib_B = syn_inhib_B + 1.0
        }
        # ===========================


        noise_min = 0.5
        noise_max = 1.5

        glk_noise1 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]
        glk_noise2 =  ~uniform(min=noise_min, max=noise_max + eK/{1V})[when=SIM_INIT, share=PER_POPULATION]
        glk_noise3 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_POPULATION]
        glk_noise4 =  ~uniform(min=noise_min, max=noise_max)[when=SIM_INIT, share=PER_NEURON]


        glk_noise = (glk_noise1 + glk_noise2 ) / 4.0




        eK = -80mV
        eNa = 50mV
        gKs = 1.0 nS
        gKf = 8.0 nS
        gNa = 110 nS
        gLk = 1/{400MOhm}
        eLk = -50mV

        # Leak
        iLk = gLk * (eLk-V) * glk_noise



        # Slow Potassium (Ks):
        alpha_ks_n = AlphaBetaFunc(v=V, A=0.2ms-1, B=0.0ms-1 mV-1, C=1.0, D=-2.96mV,E=-7.74mV)
        beta_ks_n = AlphaBetaFunc(v=V, A=0.05ms-1, B=0.0ms-1 mV-1, C=1.0, D=-14.07mV,E=6.1mV)
        inf_ks_n = alpha_ks_n / (alpha_ks_n + beta_ks_n)
        tau_ks_n = 1.0 / (alpha_ks_n + beta_ks_n)
        ks_n' = (inf_ks_n - ks_n) / tau_ks_n
        iKs = gKs * (eK-V) * ks_n


        # Fast potassium (Kf):
        alpha_denom = ( 1.0 + exp( (V + {-27.5mV}) / {-9.3mV}) )
        alpha_denom_cl = [alpha_denom] if [alpha_denom < 2800] else [2800]
        alpha_kf_n = {3.1ms-1} / alpha_denom_cl
        beta_kf_n = AlphaBetaFunc(v=V, A=0.44ms-1, B=0.0ms-1 mV-1, C=1.0, D=8.98mV,E=16.19mV)
        inf_kf_n = alpha_kf_n / (alpha_kf_n + beta_kf_n)
        tau_kf_n = 1.0 / (alpha_kf_n + beta_kf_n)
        kf_n' = (inf_kf_n - kf_n) / tau_kf_n
        iKf = gKf * (eK-V) * kf_n



        # Sodium (Na):
        alpha_na_m = AlphaBetaFunc(v=V, A=13.26ms-1, B=0.0ms-1 mV-1, C=0.5, D=-5.01mV,E=-12.56mV)
        beta_na_m =  AlphaBetaFunc(v=V, A=5.73ms-1, B=0.0ms-1 mV-1, C=1.0, D=5.01mV, E=9.69mV)
        inf_na_m = alpha_na_m / (alpha_na_m + beta_na_m)
        tau_na_m = 1.0 / (alpha_na_m + beta_na_m)
        na_m' = (inf_na_m - na_m) / tau_na_m



        alpha_na_h = AlphaBetaFunc(v=V, A=0.04ms-1, B=0.0ms-1 mV-1, C=0.0, D=28.88mV,E=26.0mV)
        #beta_na_h =  AlphaBetaFunc(v=V, A=2.04ms-1, B=0.0ms-1 mV-1, C=0.001, D=-9.09mV, E=-10.21mV)

        beta_na_h_denom = 0.001 + exp( ( {-9.09mV} + V) / {-10.21mV})
        beta_na_h =  {2.04ms-1} / beta_na_h_denom #if [beta_na_h_denom > 1e-4 or beta_na_h_denom < -1e-4] else [0.1ms-1]

        h_ab = (alpha_na_h + beta_na_h)

        inf_na_h = alpha_na_h / (alpha_na_h + beta_na_h)
        #tau_na_h = [1.0 / h_ab] if [h_ab ><ms-1] else [
        tau_na_h = 1.0 / h_ab
        na_h' = (inf_na_h - na_h) / tau_na_h

        iNa = gNa * (eNa-V) * na_m * na_m * na_m * na_h * glk_noise1





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
        'i_injected'    : NodeRange(min="0nA", max = "10nA"),
        'V'             : NodeRange(min="-100mV", max = "50mV"),
        'k'             : NodeRange(min="-0.01", max = "1.1"),
        #'ca_m'          : NodeRange(min="-0.01", max = "1.5"),
        'kf_n'          : NodeRange(min="-0.01", max = "1.5"),
        'ks_n'          : NodeRange(min="-0.01", max = "1.5"),
        'na_h'          : NodeRange(min="-0.01", max = "1.5"),
        'na_m'          : NodeRange(min="-0.01", max = "1.5"),
        'syn_nmda_A'    : NodeRange(min='0', max ='500'),
        'syn_nmda_B'    : NodeRange(min='0', max ='500'),
        'syn_ampa_A'    : NodeRange(min='0', max ='500'),
        'syn_ampa_B'    : NodeRange(min='0', max ='500'),
        'syn_inhib_A'    : NodeRange(min='0', max ='500'),
        'syn_inhib_B'    : NodeRange(min='0', max ='500'),
        }

    #var_annots_tags = {
    #    'V': 'Voltage',
    #    'syn_nmda_A':'',
    #    'syn_nmda_B' : '',
    #    'i_nmda' : '',
    #    'nmda_vdep' :'',
    #    'iLk' : '',
    #    'iKf' : '',
    #    'kf_n': '',
    #    'iInj_local': '',

    #}



    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_hh_MN']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)



    #comp.annotate_ast( NodeRangeAnnotator(var_annots_ranges) )
    RangeExpander().visit(comp)

    # New range optimiser:
    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))


    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    from neurounits.ast_annotations.common import NodeTagger
    #NodeTagger(var_annots_tags).visit(comp)

    return comp

