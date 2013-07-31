
#ifndef __FLOAT_UTILS_H__
#define __FLOAT_UTILS_H__


#include <stdio.h>
#include <math.h>
#include <cinttypes>
#include <assert.h>
#include <stdio.h>
#include <execinfo.h>
#include <signal.h>
#include <stdlib.h>




#define DBG_RANGE

namespace mh
{


        class FixedFloatConversionError : public std::exception
        {


        };




        template<int cl_nbits>
        class FixedFloatConversion
        {
        public:
                static const int cl_range_max = (1<<(cl_nbits-1));

                static double to_float(int val, int upscale)
                {
                        double res =  ( double(val) * pow(2.0, upscale) / double(cl_range_max) );
                        return res;
                }

                static int from_float(double val, int upscale)
                {

#ifdef DBG_RANGE
                        if( fabs(val)>pow(2.0, upscale))
                        {
                                std::cout << "\nTrying to Encode: " << val << " using an upscale of " << upscale << ", which is outside the range!\n" << std::flush;
                                std::cerr << "\nTrying to Encode: " << val << " using an upscale of " << upscale << ", which is outside the range!\n" << std::flush;
                                void *array[10];
                                size_t size;

                                // get void*'s for all entries on the stack
                                size = backtrace(array, 10);
                                backtrace_symbols_fd(array, size, STDERR_FILENO);

                                assert(0);
                        }
                        assert( fabs(val) <= pow(2.0, upscale) ); // Encoding out of range.
                        if(val <0 ) assert( fabs(val) / pow(2.0, upscale) < cl_range_max-1 );
#endif

                        int res =  int(val * (double(cl_range_max) / pow(2.0, upscale) ) ) ;
                        return res;
                }





                // Wrappers:
                static double to_float(SafeInt32 val, SafeInt32 upscale)
                {
                    return to_float( get_value(val), get_value(upscale) );
                }
                static double to_float(int val, SafeInt32 upscale)
                {
                    return to_float( val, get_value(upscale) );
                }
                static double to_float(SafeInt32 val, int upscale)
                {
                    return to_float( get_value(val), upscale );
                }

                static int from_float(double val, SafeInt32 upscale)
                {
                    return from_float(val, get_value(upscale));
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
