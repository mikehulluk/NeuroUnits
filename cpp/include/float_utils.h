
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
	public:
		static const int cl_range_max = (1<<(cl_nbits-1));
	public:
		static double to_float(int val, int upscale)
		{
			double res =  ( double(val) * pow(2.0, upscale) / double(cl_range_max) );
			return res; 
		}
		
		static int from_float(double val, int upscale)
		{
			
			if( fabs(val)>pow(2.0, upscale))
			{
				cout << "Trying to Encode: " << val << " using an upscale of " << upscale << ", which is outside the range!\n";
				assert(0);	
			}
			assert( fabs(val) <= pow(2.0, upscale) ); // Encoding out of range.
			if(val <0 ) assert( fabs(val) <= pow(2.0, upscale) -1 );
			
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
