

import mreorg
mreorg.PlotManager.autosave_image_formats = [mreorg.FigFormat.SVG]

import os
import pylab
import cPickle as pickle
import hashlib
import shutil
import subprocess

import neurounits
from neurounits.codegen.cpp.fixed_point import CBasedEqnWriterFixedNetwork, NumberFormat
from neurounits.visualisation.mredoc import MRedocWriterVisitor
from neurounits.codegen.population_infrastructure import *





from neurounitscontrib.demo import DemoPluginBase
class DemoTadpole4(DemoPluginBase):


    def get_name(self, ):
        return 'Tadpole-single-dIN'

    def run(self, args):
        test_simulate_single_hh()




def _build_sim(number_format, inj_current):
    
    #import neurounitscontrib.components.
    import neurounitscontrib.components.tadpole
    
    HH_comp = neurounits.ComponentLibrary.instantiate_component('HH')
    network = Network()
    dINs = network.create_population(
            name=('HH_%s'%number_format),
            component=HH_comp,
            size=1,
            parameters={
                'inj_current': inj_current,

                },
            )
    network.record_output_events(dINs, 'spike' )
    network.record_traces(dINs, 'V' )

    results = CBasedEqnWriterFixedNetwork(
                    network,
                    CPPFLAGS='-DON_NIOS=false -DPC_DEBUG=false -DUSE_BLUEVEC=false ',
                    step_size=0.01e-3,
                    run_until=0.55,
                    number_format = number_format,
                    record_rate=1,
                    ).results
    return results

def build_sim(number_format, inj_current):
    try:
        return _build_sim(number_format=number_format, inj_current=inj_current)
    except subprocess.CalledProcessError:
        return None


def test_simulate_single_hh():

    import hdfjive
    number_formats = [
            (NumberFormat.GMP,"50pA"),
            (NumberFormat.GMP,"49.5pA"),
            (NumberFormat.Double,"50pA"),
            (NumberFormat.Int28,"50pA"),
            (NumberFormat.Int24,"50pA"),
            (NumberFormat.Int20,"50pA"),
            ]
    results = [ build_sim(number_format=number_format,inj_current=inj_current) for (number_format,inj_current) in number_formats ]
    for r in results:
        assert r

    results = hdfjive.HDF5SimulationResultFileSet(results)




    filters_traces = [
       "ALL{V}",
       "ALL{POPINDEX:0000} AND ANY{iLk,iInj_local}",
       "ALL{POPINDEX:0000} AND ANY{ks_n,kf_n,na_m,na_h}",

    ]

    filters_spikes = [
        "ALL{spike}",
    ]


    left=0.25
    text_kwargs = dict( weight='bold', fontweight='bold' )

    f1,f2 = results.plot(trace_filters=filters_traces,
                 spike_filters=filters_spikes,
                 legend=False,
                 xlim = (0.0,0.7),
                 fig_trace_kwargs= dict(figsize=(85/25.4, 1) ),
                 fig_event_kwargs= dict(figsize=(85/25.4, 1) ),
                   )

    f1[0].get_axes()[0].set_ylabel("Voltage (V)")

    f1[0].text(0.05, 0.92, 'A', **text_kwargs)
    f2[0].text(0.05, 0.92, 'B', **text_kwargs)


    f1[0].subplots_adjust(top=0.9, left=left)

    f1[0].get_axes()[0].axvspan( 0.4, 0.45, color='grey', alpha=0.2)

    if not os.path.exists('_build'):
        os.mkdir('_build')
    f1[0].savefig('_build/res_hh1_newA_i.svg')
    f2[0].savefig('_build/res_hh1_newB_i.svg')



    f1,f2 = results.plot(trace_filters=filters_traces,
                 spike_filters=filters_spikes,
                 xlim = (0.4,0.45),
                 fig_trace_kwargs= dict(figsize=(85/25.4, 1.5) ),
                 fig_event_kwargs= dict(figsize=(85/25.4, 1) ),
                   )



    f1[0].text(0.05, 0.92, 'B', **text_kwargs )
    f2[0].text(0.05, 0.92, 'C', **text_kwargs)

    f1[0].get_axes()[0].set_ylabel("Voltage (V)")

    f2[0].get_axes()[0].set_ylabel("")
    f2[0].get_axes()[0].set_yticks([0,1,2,3,4,5])
    f2[0].get_axes()[0].set_yticklabels([
                                'MPFR - 50.0pA',
                                'MPFR - 49.5pA',
                                'F64 - 50.0pA',
                                'I28 - 50.0pA',
                                'I24 - 50.0pA',
                                'I20 - 50.0pA',
                                        ])
    for label in f2[0].get_axes()[0].get_yticklabels(): 
        label.set_horizontalalignment('right') 
                                        
    f2[0].get_axes()[0].set_ylim(-0.5, 5.5)

    f1[0].get_axes()[0].set_xticklabels('')


    f1[0].subplots_adjust(top=0.90, bottom=0.05, left=left)
    f2[0].subplots_adjust(top=0.85,left=left)

    

    f1[0].savefig('_build/res_hh1_newA_ii.svg')
    f2[0].savefig('_build/res_hh1_newB_ii.svg')



if __name__=='__main__':
    test_simulate_single_hh()

pylab.show()
