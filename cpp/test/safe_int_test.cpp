


#include "safe_int.h"
#include <iostream>
using namespace std;

#define BOOST_TEST_DYN_LINK
#define BOOST_TEST_MAIN
#define BOOST_TEST_MODULE MyTest
#include <boost/test/unit_test.hpp>


BOOST_AUTO_TEST_CASE( my_test )
{
    SafeUInt32 t1( 4 );
    SafeUInt32 t2( 7 );


    // Overflow on addition
    BOOST_CHECK_THROW( SafeUInt32(1<<31) + SafeUInt32(1<<31),  SafeIntException  );

    // Underflow on subtraction
    BOOST_CHECK_THROW( SafeUInt32(4) - SafeUInt32(7),  SafeIntException  );
    
    // Overflow on multiply: 
    BOOST_CHECK_THROW( SafeUInt32(1<<31) *SafeUInt32(2),  SafeIntException  );

    BOOST_CHECK( SafeUInt32(3) << SafeUInt32(2) == SafeUInt32(12) ) ;

    SafeInt32 myval = 34;
}
