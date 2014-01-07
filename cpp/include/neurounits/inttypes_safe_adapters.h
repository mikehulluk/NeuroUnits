#ifndef __NEUROUNITS_INTTYPES_SAFE_ADAPTER__
#define __NEUROUNITS_INTTYPES_SAFE_ADAPTER__


template<> SafeInt32 inttype32_from_inttype64(NativeInt64 value) { return SafeInt32::from_long(value); }




#endif
