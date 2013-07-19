
#include <stdio.h>
#include <iostream>
//#include <fstream>
#include <math.h>
//#include <gmpxx.h>
//#include <iomanip>
//#include <sstream>
#include <assert.h>
#include <cinttypes>
#include <fenv.h>
// Save-data function

double to_float(int val, int upscale)
{
    //double res =  ( double(val) * (1<<(upscale-bits+1) ) );
    double res =  ( double(val) * pow(2.0, upscale) / double(range_max) );
    //std::cout << "to_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res; 
}

int from_float(double val, int upscale, int whoami=0)
{
    int res =  int(val * (double(range_max) / pow(2.0, upscale) ) ) ;
    //std::cout << "from_float(" << val << ", " << upscale << ") => " << res << "\n";
    return res;
}

int auto_shift(int n, int m)
{
    //std::cout << "\n" << "n/m:" << n << "/" << m << "\n";
    if(m==0)
    {
        return n;
    }
    if( m>0)
    {
        return n << m;
    }
    else 
    {
       return n >> -m;
    }
}


long auto_shift64(long n, int m)
{
    //std::cout << "\n" << "n/m:" << n << "/" << m << "\n";
    if(m==0)
    {
        return n;
    }
    if( m>0)
    {
        return n << m;
    }
    else 
    {
       return n >> -m;
    }
}
