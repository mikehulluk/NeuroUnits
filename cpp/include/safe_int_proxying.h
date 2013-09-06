#ifndef __SAFE_INT_PROXY_H__
#define __SAFE_INT_PROXY_H__


#include "basic_types.h"

NativeInt32 get_value32(NativeInt32 i)
{
    return i;
}

NativeInt64 get_value64(NativeInt32 i)
{
    return i;
}


// Templates for allowing return types to change based on IntType
template<typename T>T inttype32_from_inttype64(NativeInt64 value){ assert(0); }
template<> int inttype32_from_inttype64(NativeInt64 value){ return value;}
template<> long long inttype32_from_inttype64(NativeInt64 value){ return value;}

#if SAFEINT
template<> SafeInt32 inttype32_from_inttype64(NativeInt64 value) { return SafeInt32::from_long(value); }
#endif 


#if SAFEINT 
typedef SafeInt32 IntType;
#else 
typedef int IntType;
//typedef long long IntType;
#endif










#endif
