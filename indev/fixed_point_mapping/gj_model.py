


import neurounits
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator,NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_gj(nbits):
    src_text = """
    define_component simple_hh_MN {
    
        <=> INPUT v1:(V)
        <=> INPUT v2:(V)

        i1 = g * (v1-v2)
        i2 = -i1

    }



    """




    var_annots_ranges = {
        't'     : NodeRange(min="0ms", max = "1.1s"),
        'v1'    : NodeRange(min="-100mV", max = "50mV"),
        'v2'    : NodeRange(min="-100mV", max = "50mV"),
        'g'     : NodeRange(min="-100mV", max = "50mV"),
        }

    var_annots_tags = {
        'V': 'Voltage',

    }



    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_hh_MN']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)

    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))
    RangeExpander().visit(comp)

    comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    from neurounits.ast_annotations.common import NodeTagger
    NodeTagger(var_annots_tags).visit(comp)

    return comp

