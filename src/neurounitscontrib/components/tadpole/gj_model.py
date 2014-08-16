


import neurounits
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator,NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_gj():
    src_text = """
    define_component simple_gj {
        <=> parameter g:(S)
        <=> input v1:(V)
        <=> input v2:(V)

        i1 = g * (v2-v1)
        i2 = -i1
    }



    """




    var_annots_ranges = {
        '__t__' : NodeRange(min="0s", max="1.1s"),
        'v1'    : NodeRange(min="-100mV", max="50mV"),
        'v2'    : NodeRange(min="-100mV", max="50mV"),
        'g'     : NodeRange(min="0nS", max="10nS"),
        }

    var_annots_tags = {
        'v1': 'Voltage',
        'v2': 'Voltage',
    }



    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_gj']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)

    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))
    RangeExpander().visit(comp)

    #comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    from neurounits.ast_annotations.common import NodeTagger
    NodeTagger(var_annots_tags).visit(comp)

    return comp



from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('GJ', get_gj )
