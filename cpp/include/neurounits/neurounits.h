

#ifndef __NEUROUNITS_H__
#define __NEUROUNITS_H__


#include "inttypes_native.h"
#include "inttypes_native_adapters.h"


#include "inttypes_safe.h"
#include "inttypes_safe_utils.h"
#include "inttypes_safe_adapters.h"





#if SAFEINT 
typedef SafeInt32 IntType;
#else 
typedef int IntType;
#endif



#include "int_float_conversion.h"
#include "lut.h"
#include "generic_fixed_point_operations.h"



#endif //__NEUROUNITS_H__











