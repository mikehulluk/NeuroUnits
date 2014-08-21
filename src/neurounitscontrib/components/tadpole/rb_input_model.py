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




import neurounits
from neurounits.ast_annotations.common import NodeRange, NodeToIntAnnotator
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



    <=> time t
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

    return comp


from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('RBInput', get_rb_input )
