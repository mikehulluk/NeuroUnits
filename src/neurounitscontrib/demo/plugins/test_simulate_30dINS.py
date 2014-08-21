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

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.PNG]

import os
import neurounits

import random
import pylab

from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork, NumberFormat
from hdfjive import HDF5SimulationResultFileSet

from neurounits.codegen.population_infrastructure import *







from neurounitscontrib.demo import DemoPluginBase
class DemoTadpole1(DemoPluginBase):


    def get_name(self, ):
        return 'Tadpole-30'

    def run(self, args):
        test_simulate30dINs()





def get_results():

    import neurounitscontrib.components.tadpole
    dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')

    #import components
    #dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')
    #MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN')
    #RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput')


    network = Network()


    dINs = network.create_population(
            name='dINs',
            component=dIN_comp,
            size=30,
            parameters= {
                'nmda_multiplier': 1.0,
                'ampa_multiplier': 1.0,
                'inj_current':'20pA',
            },

            )

    GJ_comp =  neurounits.ComponentLibrary.instantiate_component('GJ')
    assert not GJ_comp.has_state()




    #AllToAllConnector(0.3),
    gap_junction_indices = []
    for i in range(30):
        for j in range(i):
            if random.uniform(0.,1.) < 0.2:
                gap_junction_indices.append( (i,j) )




    network.add(
        AnalogPortConnector(
            src_population =  dINs,
            dst_population =  dINs,
            port_map = [
                ('conn.v1', 'src.V'),
                ('conn.i1', 'src.i_injected'),
                ('conn.v2', 'dst.V'),
                ('conn.i2', 'dst.i_injected'),
                ],
            connector=ExplicitIndicesLoop(gap_junction_indices),
            connection_object=GJ_comp,
            connection_properties={
                'g': "2nS",
                },

            name='Ecoupling'
            )

)

    network.create_eventportconnector(
                src_population=dINs,
                dst_population=dINs,
                src_port_name='spike',
                dst_port_name='recv_nmda_spike',
                name="dIN_dIN_NMDA", delay='1ms',
                connector=AllToAllConnector(0.2),
                parameter_map= {'weight': FixedValue("150pS")}
            )

    #network.create_electricalsynapseprojection(
    #    src_population=dINs,
    #    dst_population=dINs,
    #    connector=AllToAllConnector(0.3),
    #    strength_S = 0.3e-9,
    #    injected_port_name='i_injected',
    #    name='E_Couple')




    network.record_input_events(dINs, 'recv_nmda_spike' )
    network.record_input_events(dINs, 'recv_inh_spike' )
    network.record_input_events(dINs, 'recv_ampa_spike' )
    network.record_output_events(dINs, 'spike' )
    network.record_traces(dINs, '*' )


    op_filename = 'output_fixed.hd5'
    if os.path.exists(op_filename):
        os.unlink(op_filename)

    CBasedEqnWriterFixedNetwork(
                        network,
                        output_filename=op_filename,
                        CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                        step_size=0.1e-3,
                        run_until=1.0,
                        as_float=False,
                        number_format = NumberFormat.Int28,
                        ).results






def test_simulate30dINs():
    get_results()
    results = HDF5SimulationResultFileSet(['output_fixed.hd5'])

    import neurounitscontrib.components.tadpole
    dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')

    pylab.margins(0.1)

    filters_traces = [
        'ALL{POPINDEX:0000,V}',
        'ALL{V}',
        'ALL{POPINDEX:0001,V}',
        'ALL{POPINDEX:0002,V}',
        'ALL{POPINDEX:0003,V}',
        ]

    for symbol in sorted(dIN_comp.terminal_symbols, key=lambda o:o.symbol):
        filters_traces.append( "ALL{POPINDEX:0000} AND ANY{%s}" % symbol.symbol )

    results.plot(trace_filters=filters_traces, legend=True )




if __name__=='__main__':
    test_simulate30dINs()
    pylab.show()
