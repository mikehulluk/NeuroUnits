
#ifndef __FLOAT_UTILS_H__
#define __FLOAT_UTILS_H__


#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdlib.h>



#if SAFEINT
#include "safe_int.h"
#include "safe_int_proxying.h"
#include "safe_int_utils.h"
#endif
//#define DBG_RANGE





namespace mh
{


        class FixedFloatConversionError : public std::exception
        {


        };




        template<int cl_nbits>
        class FixedFloatConversion
        {
        public:
                static const NativeInt64 cl_range_max = (1<<(cl_nbits-1));

                static double to_float(NativeInt32 val, NativeInt32 upscale)
                {
                        double res =  ( double(val) * pow(2.0, upscale) / double(cl_range_max) );
                        return res;
                }

                static NativeInt32 from_float(double val, NativeInt32 upscale)
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

                        NativeInt32 res =  NativeInt32(val * (double(cl_range_max) / pow(2.0, upscale) ) ) ;
                        return res;
                }





                // Wrappers:
#if SAFEINT
                static double to_float(SafeInt32 val, SafeInt32 upscale)
                {
                    return to_float( get_value32(val), get_value32(upscale) );
                }
                static double to_float(int val, SafeInt32 upscale)
                {
                    return to_float( val, get_value32(upscale) );
                }
                static double to_float(SafeInt32 val, int upscale)
                {
                    return to_float( get_value32(val), upscale );
                }

                static int from_float(double val, SafeInt32 upscale)
                {
                    return from_float(val, get_value32(upscale));
                }
#endif

        };












        NativeInt32 auto_shift(NativeInt32 n, NativeInt32 m)
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


        NativeInt64 auto_shift64(NativeInt64 n, NativeInt32 m)
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
