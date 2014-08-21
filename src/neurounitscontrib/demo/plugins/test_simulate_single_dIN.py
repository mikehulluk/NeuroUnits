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

import pylab


import neurounits
from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork, NumberFormat
from neurounits.codegen.population_infrastructure import *







from neurounitscontrib.demo import DemoPluginBase
class DemoTadpole3(DemoPluginBase):


    def get_name(self, ):
        return 'Tadpole-single-dIN'

    def run(self, args):
        test_simulate_single_din()


def test_simulate_single_din():

    import neurounitscontrib.components.tadpole
    dIN_comp = neurounits.ComponentLibrary.instantiate_component('dIN')
    MN_comp =  neurounits.ComponentLibrary.instantiate_component('MN')
    RB_input = neurounits.ComponentLibrary.instantiate_component('RBInput')

    nbits=24










    network = Network()

    dINs = network.create_population(
            name='dINs', 
            component=dIN_comp,
            parameters= { 'inj_current': '30pA', 'ampa_multiplier':'1', 'nmda_multiplier':'1'},
            size=1)

    #network.create_eventportconnector(
    #            src_population=dINs,
    #            dst_population=dINs,
    #            src_port_name='spike',
    #            dst_port_name='recv_nmda_spike',
    #            name="dIN_dIN_NMDA", delay='1ms',
    #            connector=AllToAllConnector(0.3),
    #            parameter_map= {'weight': FixedValue("0.2nS")}
    #        )
    #
    #network.create_electricalsynapseprojection(
    #    src_population=dINs,
    #    dst_population=dINs,
    #    connector=AllToAllConnector(0.3),
    #    strength_S = 0.3e-9,
    #    injected_port_name='i_injected',
    #    name='E_Couple')



    network.record_output_events(dINs, 'spike' )
    network.record_traces(dINs, 'V' )
    network.record_traces(dINs, 'iCa iNa iKf iKs iLk syn_nmda_i iInj_local' )
    network.record_traces(dINs, 'ks_n kf_n na_m na_h ca_m' )
    network.record_traces(dINs, '' )
    network.record_traces(dINs, 'nmda_vdep' )


    results = CBasedEqnWriterFixedNetwork(
            network, 
            CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ', 
            number_format = NumberFormat.Int28, 
            step_size=0.01e-3,
            run_until=1.0,
            ).results
    #shutil.copy(hdffile, os.path.expanduser("~/debugging/") )


    filters_traces = [
       "ALL{V}",
       "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
       "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",
       #"ALL{POPINDEX:0000} AND ANY{iCa,iNa,iLk,iKf,iKs,syn_nmda_i}",
       #"ALL{POPINDEX:0000} AND ANY{nmda_vdep}",
    ]

    filters_spikes = [

        "ALL{EVENT:spike}",
    ]


    results.plot(trace_filters=filters_traces, spike_filters=filters_spikes, legend=True, xlim = (0.0,0.3)  )



    


if __name__=='__main__':
    test_simulate_single_din()
    pylab.show()
    
    
