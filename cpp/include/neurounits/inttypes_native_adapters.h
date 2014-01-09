/*
Copyright (c) 2014, Michael Hull
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef __NEUROUNITS_INTTYPES_NATIVE_ADAPTER_H__
#define __NEUROUNITS_INTTYPES_NATIVE_ADAPTER_H__

#include <assert.h>
#include <math.h>


#include "inttypes_native.h"


// Deprecated:
NativeInt32 get_value32(NativeInt32 i)
{
    return i;
}
NativeInt64 get_value64(NativeInt32 i)
{
    return i;
}


// Templates for allowing return types to change based on IntType
template<typename T>T inttype32_from_inttype64(NativeInt64 value)
{
    assert(0);
}
template<> int inttype32_from_inttype64(NativeInt64 value)
{
    return value;
}
template<> long long inttype32_from_inttype64(NativeInt64 value)
{
    return value;
}




double pow(double a, NativeInt32 b)
{
    return pow(a, (double)b);
}

double pow(double a, NativeInt64 b)
{
    return pow(a, (double)b);
}

inline
NativeInt32 auto_shift(NativeInt32 n, NativeInt32 m)
{
    if(m == 0) {
        return n;
    } else if(m > 0) {
        return n << m;
    } else {
        return n >> -m;
    }
}

inline
NativeInt64 auto_shift64(NativeInt64 n, NativeInt32 m)
{
    if(m == 0) {
        return n;
    } else if(m > 0) {
        return n << m;
    } else {
        return n >> -m;
    }
}





#endif //__NEUROUNITS_INTTYPES_NATIVE_ADAPTER_H__
