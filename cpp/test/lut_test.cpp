

#include <iostream>
#include <fstream>
using namespace std;




const int nbits = 24;

#include "float_utils.h"

#include "lut.h"




int main()
{
    //LookUpTableExpPower2 exp_table( 12, 3);
    LookUpTableExpPower2<24, SafeInt32> exp_table( 5, 3);

	typedef mh::FixedFloatConversion<24> FixedFloatConversion;
	
	
    ofstream output("exp_out.txt");

    int in_upscale = 3;
    int out_upscale = 9;
    const int NPOINTS = 1000;
    for(int i=-700;i< 750;i++)
    {
        double x = (float)i/100.;
        int x_int = FixedFloatConversion::from_float( x, in_upscale);

        int exp_x = exp_table.get(x_int, in_upscale, out_upscale);

        float exp_x_float = FixedFloatConversion::to_float(exp_x, out_upscale);

        //output << "\nexp(" << x << ") => " << exp_x_float;
        output << "\n" << x << " " << exp_x_float;
    }





    cout << "All down";
}
