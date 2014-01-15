



import neurounits
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator,NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations.node_range_byoptimiser import NodeRangeByOptimiser
from neurounits.ast_annotations.node_rangeexpander import RangeExpander


def get_rb_input():
    src_text = """
    define_component simple_input {

        t_next' = 0

    

        on ( t>50ms  and t > t_next) {
                emit spike()
                t_next  = 1s
            };

     initial {
        t_next = 0ms
    }



    <=> TIME t
    }


    """




    var_annots_ranges = {
        't'             : NodeRange(min="0ms", max = "1.1s"),
        't_next'             : NodeRange(min="0ms", max = "1s"),
        }


    library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)
    comp = library_manager['simple_input']
    comp.expand_all_function_calls()


    # Optimise the equations, to turn constant-divisions into multiplications:
    from neurounits.visitors.common.equation_optimisations import OptimiseEquations
    OptimiseEquations(comp)



    #comp.annotate_ast( NodeRangeAnnotator(var_annots_ranges) )
    RangeExpander().visit(comp)

    # New range optimiser:
    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))


    #comp.annotate_ast( NodeFixedPointFormatAnnotator(nbits=nbits), ast_label='fixed-point-format-ann' )
    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    from neurounits.ast_annotations.common import NodeTagger
    #NodeTagger(var_annots_tags).visit(comp)

    return comp


from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('RBInput', get_rb_input )
