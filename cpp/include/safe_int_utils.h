
#ifndef __SAFE_INT_UTILS_H__
#define __SAFE_INT_UTILS_H__

#include <ostream>



#include "safe_int.h"
#include "safe_int_proxying.h"



#if SAFEINT
NativeInt32 get_value32(SafeInt32 i)
{
    return i.get_value32();
}

long get_value_long(SafeInt32 i)
{
    return i.get_value32();
}




SafeInt32 auto_shift(SafeInt32 n, SafeInt32 m)
{
    if(m.get_value32()==0)
    {
            return n;
    }
    if(m.get_value32()>0)
    {
            return n << m;
    }
    else
    {
       return n >> -m;
    }

}

std::ostream& operator<<(std::ostream& o, SafeInt32 v)
{
    o << v.get_value32();
    return o;
}


double pow(double x, SafeInt32 rhs)
{
    return pow(x, rhs.get_value32() );
}
#endif


#endif // __SAFE_INT_UTILS_H__
