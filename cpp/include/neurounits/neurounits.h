

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





namespace neurounits {

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











