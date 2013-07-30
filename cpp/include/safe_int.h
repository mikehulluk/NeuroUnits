

#ifndef __SAFE_INT_H__
#define __SAFE_INT_H__


#include <exception>
#include <cstddef>

#include <iostream>

class SafeIntException : public std::exception
{


};

typedef signed long SL;


namespace mh_int32
{

    const long int32_max = (1l<<(32-1)) - 1;
    const long int32_min = -(1l<<(32-1)) - 1;


    class SafeInt32
    {
        int _value;

    public:


        static SafeInt32 from_long(long value)
        {
            assert( value < int32_max && value > int32_min);

            int v = value;
            assert( (long) v == value);

            return SafeInt32(v);
        }

        int get_value()
        {
            return _value;
        }

        long get_value_long()
        {
            return _value;
        }

        explicit SafeInt32(int value)
            : _value(value)
        {
            if( (SL)_value > (SL)int32_max || (SL)_value < (SL) int32_min )
            {
                throw SafeIntException();
            }
        }

        bool is_positive() const
        {
            return (_value >= 0);
        }

        friend SafeInt32 operator+(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator-(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator*(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator/(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator<<(const SafeInt32& a, const SafeInt32& b);
        friend SafeInt32 operator>>(const SafeInt32& a, const SafeInt32& b);
        friend SafeInt32 operator+(SafeInt32 a, int b);
        friend SafeInt32 operator-(SafeInt32 a, int b);
        friend SafeInt32 operator*(SafeInt32 a, int b);

        bool operator==(const SafeInt32& rhs)
        {
            return _value == rhs._value;
        }


        // Comparisons against ints:
        bool operator==(int rhs)
        {
            return _value == rhs;
        }
        bool operator>(int b)
        {
            return _value > b;
        }
        bool operator<(int b)
        {
            return _value < b;
        }
        bool operator>=(int b)
        {
            return _value >= b;
        }
        SafeInt32 operator-()  
        {
            return SafeInt32(-_value);
        }

    };


    SafeInt32 operator+(SafeInt32 a, SafeInt32 b)
    {

        if(a.is_positive() )
        {
            if( b.is_positive() )
            {
                // Check for overflow:
                if( (SL)int32_max - (SL) a._value  < (SL) b._value )
                {
                    std::cout << "\n\nEh Oh! (SafeInt32 operator+(SafeInt32 a, SafeInt32 b)) Overflow detected! ( " << (SL) a._value << " + " << (SL) b._value << " )\n\n";
                    throw SafeIntException();
                }

            }
            else
            {
                // (+) + (-) This should be OK, because we must still be in range
            }
        }
        else
        {
            if( b.is_positive() )
            {
                // (-) + (+) This should be OK, because we must still be in range

            }
            else
            {
                // (-) + (-)
                // Check for underflow:
                //std::cout << "int32_min: " << int32_min << "\n" << std::flush;
                if( (SL)int32_min + ((SL) b._value ) * -1  > (SL)a._value )
                {
                    throw SafeIntException();
                }

            }
        }
        return SafeInt32( a._value + b._value );
    }

    SafeInt32 operator-(SafeInt32 a, SafeInt32 b)
    {
        // TODO: Check for overflow/underflow here:
        return SafeInt32( a._value - b._value);
    }

    SafeInt32 operator*(SafeInt32 a, SafeInt32 b)
    {
        // TODO: Check for overflow/underflow here:
        return SafeInt32( a._value * b._value);
    }

    SafeInt32 operator/(SafeInt32 a, SafeInt32 b)
    {
        // TODO: Check for overflow/underflow here:
        return SafeInt32( a._value / b._value);
    }

    SafeInt32 operator<<(const SafeInt32& a, const SafeInt32& b)
    {
        // TODO: Check for overflow/underflow here:
        assert(b._value >= 0 );
        return SafeInt32( a._value << b._value);
    }

    SafeInt32 operator>>(const SafeInt32& a, const SafeInt32& b)
    {
        // TODO: Check for overflow/underflow here:
        assert(b._value >= 0 );
        return SafeInt32( a._value >> b._value);
    }


    SafeInt32 operator+(SafeInt32 a, int b)
    {
        return a + SafeInt32(b);
    }

    SafeInt32 operator-(SafeInt32 a, int b)
    {
        return a - SafeInt32(b);
    }

    SafeInt32 operator*(SafeInt32 a, int b)
    {
        return a * SafeInt32(b);
    }




}










namespace mh_uint32
{


    const size_t uint32_max = (1l<<32) - 1;
    class SafeUInt32
    {

        unsigned int _value;

    public:
        explicit SafeUInt32(unsigned int value)
            : _value(value)
        {
            if( uint32_max < _value )
            {
                throw SafeIntException();
            }

        }

        friend SafeUInt32 operator+(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator-(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator*(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator/(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator<<(SafeUInt32 a, SafeUInt32 b);
        friend SafeUInt32 operator>>(SafeUInt32 a, SafeUInt32 b);


        bool operator==(const SafeUInt32& rhs)
        {
            return _value == rhs._value;
        }

    };



    SafeUInt32 operator+(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for overflow:
        if( uint32_max - a._value < b._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value + b._value );
    }

    SafeUInt32 operator-(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for underflow:
        if( a._value < b._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value - b._value );
    }

    SafeUInt32 operator*(SafeUInt32 a, SafeUInt32 b)
    {
        // Check for overflow:
        if( uint32_max / b._value < a._value )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value * b._value );
    }

    SafeUInt32 operator/(SafeUInt32 a, SafeUInt32 b)
    {
        if( b._value == 0 )
        {
            throw SafeIntException();
        }
        return SafeUInt32( a._value / b._value );
    }

    SafeUInt32 operator<<(SafeUInt32 a, SafeUInt32 b)
    {
        // TODO: Ensure that the top bits 'b' are zero:
        return SafeUInt32( a._value << b._value );
    }

    SafeUInt32 operator>>(SafeUInt32 a, SafeUInt32 b)
    {
        // TODO: Ensure that the top bits 'b' are zero:
        return SafeUInt32( a._value >> b._value );
    }

};





using namespace mh_uint32;
using namespace mh_int32;






#endif // __SAFE_INT_H__
