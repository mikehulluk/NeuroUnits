/* 
Copyright (c) 2014, Michael Hull
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/


#ifndef __NEUROUNITS_INTFLOAT_CONVERSION_H__
#define __NEUROUNITS_INTFLOAT_CONVERSION_H__




#include <stdio.h>
#include <math.h>
#include <assert.h>
#include <stdlib.h>
#include <execinfo.h>
#include <cxxabi.h>



#include "inttypes_native.h"
#include "inttypes_native_adapters.h"

#include "inttypes_safe.h"
#include "inttypes_safe_adapters.h"
#include "inttypes_safe_utils.h"






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

                inline
                static double to_float(NativeInt32 val, NativeInt32 upscale)
                {
                        double res =  ( double(val) * pow(2.0, upscale) / double(cl_range_max) );
                        return res;
                }

                inline
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

                        double t1 = (double(cl_range_max) / pow(2.0, upscale) );
                        double t2 =  val * t1;
                        NativeInt32 res =  NativeInt32( t2 ) ;
                        return res;
                }





                // Wrappers:
                inline
                static double to_float(SafeInt32 val, SafeInt32 upscale)
                {
                    return to_float( get_value32(val), get_value32(upscale) );
                }
                inline
                static double to_float(int val, SafeInt32 upscale)
                {
                    return to_float( val, get_value32(upscale) );
                }
                inline
                static double to_float(SafeInt32 val, int upscale)
                {
                    return to_float( get_value32(val), upscale );
                }

                inline
                static int from_float(double val, SafeInt32 upscale)
                {
                    return from_float(val, get_value32(upscale));
                }
        };










}


#endif //__NEUROUNITS_INTFLOAT_CONVERSION_H__
