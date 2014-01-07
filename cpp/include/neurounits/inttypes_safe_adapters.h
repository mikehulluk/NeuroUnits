#ifndef __NEUROUNITS_INTTYPES_SAFE_ADAPTER__
#define __NEUROUNITS_INTTYPES_SAFE_ADAPTER__



// Native to Safe
template<> SafeInt32 inttype32_from_inttype64(NativeInt64 value) { return SafeInt32::from_long(value); }


// Safe to Native
NativeInt32 get_value32(SafeInt32 i) {  return i.get_value32(); }
NativeInt64 get_value64(SafeInt32 i) {  return i.get_value32(); }




#endif
