/*
Copyright (c) 2014, Michael Hull
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/



#include <iostream>
#include <fstream>
using namespace std;




const int nbits = 24;

#include "neurounits/neurounits.h"

//#include "lut.h"




int main()
{
    //LookUpTableExpPower2 exp_table( 12, 3);
    LookUpTableExpPower2<24, NativeInt32> exp_table(5, 3);

    typedef mh::FixedFloatConversion<24> FixedFloatConversion;
    ofstream output("exp_out.txt");

    int in_upscale = 3;
    int out_upscale = 9;
    const int NPOINTS = 1000;
    for(int i = -700; i < 750; i++) {
        double x = (float)i / 100.;
        int x_int = FixedFloatConversion::from_float(x, in_upscale);

        int exp_x = exp_table.get(x_int, in_upscale, out_upscale);

        float exp_x_float = FixedFloatConversion::to_float(exp_x, out_upscale);

        //output << "\nexp(" << x << ") => " << exp_x_float;
        output << "\n" << x << " " << exp_x_float;
    }





    cout << "All down";
}
