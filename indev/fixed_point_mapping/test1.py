



import neurounits

import numpy as np
import pylab




src_text = """

define_component simple_leak {
    iInj = [4pA] if [t > 50ms] else [0pA]
    C = 10 pF
    gLk = 1.25 nS
    eLk = -50mV

    iLk = gLk * (eLk-V) * glk_noise
    V' = (1/C) * (iInj + iLk)

 <=> INPUT t:(ms)
 <=> PARAMETER glk_noise:()

}

"""


library_manager = neurounits.NeuroUnitParser.Parse9MLFile( src_text)


comp = library_manager['simple_leak']


## Check it works:
#res = comp.simulate(
#                times = np.arange(0, 0.1,0.00001),
#                initial_state_values={'V':'-60mV'},
#                parameters={'glk_noise': '1.2'},
#                )
#res.auto_plot()



import mako
from mako.template import Template







c_prog = """



// Define the data-structures:
${DEF_DATASTRUCT}



// Update-function
${DEF_UPDATE_FUNC}



int main()
{

    SimData data;


    for(int i=0;i<10000;i++)
    {
        sim_step(data);
    }



}




"""



import os




class CBasedEqnWriter(object):
    def __init__(self, component, annotations):
        self.component = component


        def_DATASTRUCT = self.build_data_structure()
        def_UPDATEFUNC = self.build_update_function()



        cfile = Template(c_prog).render(
                    DEF_DATASTRUCT = def_DATASTRUCT,
                    DEF_UPDATE_FUNC = def_UPDATEFUNC )

        with open( 'sim1.cpp','w') as f:
            f.write(cfile)

        os.system("g++ sim1.cpp")


    def build_data_structure(self):
        return "struct SimData {};"
    def build_update_function(self):
        return "void sim_step(SimData& d) {};"

#print Template("hello ${data}!").render(data="world")





class VariableAnnotation(object):
    pass




CBasedEqnWriter(comp, annotations=[] )


pylab.show()


