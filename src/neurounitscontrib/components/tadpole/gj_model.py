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
from neurounits.ast_annotations import NodeRange, NodeToIntAnnotator
from neurounits.ast_annotations import NodeRangeByOptimiser
from neurounits.ast_annotations import RangeExpander, NodeTagger
from neurounits.visitors.common.equation_optimisations import OptimiseEquations

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
    
    OptimiseEquations(comp)

    comp.annotate_ast( NodeRangeByOptimiser(var_annots_ranges))
    RangeExpander().visit(comp)

    comp.annotate_ast( NodeToIntAnnotator(), ast_label='node-ids' )

    #from neurounits.ast_annotations.common import 
    NodeTagger(var_annots_tags).visit(comp)

    return comp



from neurounits import ComponentLibrary
ComponentLibrary.register_component_functor('GJ', get_gj )
