/*
Copyright (c) 2014, Michael Hull
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/




#ifndef __NEUROUNITS_H__
#define __NEUROUNITS_H__


#include "inttypes_native.h"
#include "inttypes_native_adapters.h"


#include "inttypes_safe.h"
#include "inttypes_safe_utils.h"
#include "inttypes_safe_adapters.h"



#include "int_float_conversion.h"
#include "exp_lut.h"
#include "generic_fixed_point_operations.h"





namespace neurounits
{

// Helper class to centralise NBITS and types:
template <typename IType32_, int NBITS_>
class Fixed
{
public:
    typedef IType32_ IType32;
    typedef FixedPointOp<NBITS_, IType32_> Ops;
    typedef mh::FixedFloatConversion<NBITS_> Conversion;
};
}



#endif //__NEUROUNITS_H__











