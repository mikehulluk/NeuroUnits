
#ifndef __NEUROUNITS_INTTYPES_SAFE_UTILS__
#define __NEUROUNITS_INTTYPES_SAFE_UTILS__

#include <ostream>
#include <math.h>

#include "inttypes_safe.h"
#include "inttypes_safe_adapters.h"







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
    return pow(x, (double) rhs.get_value32() );
}


#endif // __NEUROUNITS_INTTYPES_SAFE_UTILS__
