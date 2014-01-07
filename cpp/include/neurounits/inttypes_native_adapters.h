#ifndef __INTTYPES_NATIVE_ADAPTER_H__
#define __INTTYPES_NATIVE_ADAPTER_H__

#include <assert.h>
#include <math.h>


#include "inttypes_native.h"


// Deprecated:
NativeInt32 get_value32(NativeInt32 i) { return i; }
NativeInt64 get_value64(NativeInt32 i){  return i; }


// Templates for allowing return types to change based on IntType
template<typename T>T inttype32_from_inttype64(NativeInt64 value){ assert(0); }
template<> int inttype32_from_inttype64(NativeInt64 value){ return value;}
template<> long long inttype32_from_inttype64(NativeInt64 value){ return value;}




double pow(double a, NativeInt32 b)
{
    return pow(a, (double)b);
}

double pow(double a, NativeInt64 b)
{
    return pow(a, (double)b);
}


#endif //__INTTYPES_NATIVE_ADAPTER_H__
