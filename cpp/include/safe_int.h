
#include <exception>
#include <cstddef>

class SafeIntException : public std::exception
{


};


namespace mh_int32
{

    const size_t int32_max = (1l<<32-1) - 1;
    const size_t int32_min = -(1l<<32-1) - 1;


    class SafeInt32
    {
        int _value;

    public:
        explicit SafeInt32(int value)
            : _value(value)
        {
            if( _value > int32_max || _value < int32_min )
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
        friend SafeInt32 operator<<(SafeInt32 a, SafeInt32 b);
        friend SafeInt32 operator>>(SafeInt32 a, SafeInt32 b);

        bool operator==(const SafeInt32& rhs)
        {
            return _value == rhs._value;    
        }

    };


    SafeInt32 operator+(SafeInt32 a, SafeInt32 b)
    {

        if(a.is_positive() )
        {
            if( b.is_positive() )
            {
                // Check for overflow:
                if( int32_max - a._value  > b._value )
                {
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
                if( int32_min + b._value  < a._value )
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
        return SafeInt32( a._value + b._value);
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

    SafeInt32 operator<<(SafeInt32 a, SafeInt32 b)
    {
        // TODO: Check for overflow/underflow here:
        return SafeInt32( a._value << b._value);
    }

    SafeInt32 operator>>(SafeInt32 a, SafeInt32 b)
    {
        // TODO: Check for overflow/underflow here:
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
