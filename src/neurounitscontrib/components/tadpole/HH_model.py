 


import neurounits
from neurounits.ast_annotations.common import  NodeFixedPointFormatAnnotator,\
    NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_HH():
    src_text = """

    define_component simple_hh {
        from std.math import exp, ln

        <=> TIME t:(ms)
        <=> INPUT i_injected:(mA)
        #<=> PARAMETER nmda_multiplier:()
        #<=> PARAMETER ampa_multiplier:()
        <=> PARAMETER inj_current:(pA)

        iInj_local = [inj_current] if [ 50ms < t < 500ms] else [0pA]
        #iInj_local = 0pA





        Cap = 10 pF

        V' = (1/Cap) * ( itot)
        itot = iLk + iInj_local + iKs + iKf +iNa +  i_injected

        noise_min = 0.5
        noise_max = 1.5


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


      

        on (V crosses (rising) 0V) and (t>3ms)  {
            emit spike()
        };

        regime sub{

        }


        initial {
            V = -60mV
            na_m = 0.0
            na_h = 1.0
            ks_n = 0.0
            kf_n = 0.0

            #syn_nmda_B = 0.0
            #syn_nmda_A = 0.0
            #syn_ampa_B = 0.0
            #syn_ampa_A = 0.0
            #syn_inhib_B = 0.0
            #syn_inhib_A = 0.0

            regime sub
        }


    }





    """




    var_annots_ranges = {
        't'             : NodeRange(min="0ms", max = "1.1s"),
        'i_injected'    : NodeRange(min="-1500pA", max = "1500pA"),
        'V'             : NodeRange(min="-100mV", max = "60mV"),
        'kf_n'          : NodeRange(min="-0.01", max = "1.3"),
        'ks_n'          : NodeRange(min="-0.01", max = "1.3"),
        'na_h'          : NodeRange(min="-0.01", max = "1.3"),
        'na_m'          : NodeRange(min="-0.01", max = "1.3"),

        'inj_current' : NodeRange(min='0pA',max='300pA'),
        }

    var_annots_tags = {
        'V': 'Voltage',
        'i_nmda' : '',
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

    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )


    return comp



from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('HH', get_HH )
