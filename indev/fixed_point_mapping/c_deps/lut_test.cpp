

#include <iostream>
#include <fstream>
using namespace std;




const int nbits = 24;
const int range_max = (1<<(nbits-1)) ;
#include "float_utils.h"

#include "lut.h"



int main()
{
    //LookUpTableExpPower2 exp_table( 12, 3);
    LookUpTableExpPower2 exp_table( 8, 3);

    ofstream output("exp_out.txt");

    int in_upscale = 2;
    int out_upscale = 8;
    const int NPOINTS = 1000;
    for(int i=-700;i< 750;i++)
    {
        double x = (float)i/100.;
        int x_int = from_float( x, in_upscale);

        int exp_x = exp_table.get(x_int, in_upscale, out_upscale);

        float exp_x_float = to_float(exp_x, out_upscale);

        //output << "\nexp(" << x << ") => " << exp_x_float;
        output << "\n" << x << " " << exp_x_float;
    }




    cout << "All down";
}
