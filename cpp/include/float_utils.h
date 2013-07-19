
#ifndef __FLOAT_UTILS_H__
#define __FLOAT_UTILS_H__


#include <stdio.h>
#include <math.h>
#include <cinttypes>




namespace mh 
{

	template<int cl_nbits> 
	class FixedFloatConversion
	{
		static const int cl_range_max = (1<<(cl_nbits-1));
	public:
		static double to_float(int val, int upscale)
		{
			double res =  ( double(val) * pow(2.0, upscale) / double(cl_range_max) );
			return res; 
		}
		
		static int from_float(double val, int upscale, int whoami=0)
		{
			int res =  int(val * (double(cl_range_max) / pow(2.0, upscale) ) ) ;
			return res;
		}
	};

	
	
	
	







	int auto_shift(int n, int m)
	{
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

}


#endif //__FLOAT_UTILS_H__
