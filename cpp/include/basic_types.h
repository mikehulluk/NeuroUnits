
#ifndef __BASIC_TYPES_H__


// Define some basic types:

#if ON_NIOS
typedef int NativeInt32;
typedef long long int NativeInt64;

#else

#include <stdint.h>
typedef int32_t NativeInt32;
typedef int64_t NativeInt64;

#endif











#endif // __BASIC_TYPES_H__
