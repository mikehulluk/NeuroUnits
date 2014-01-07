


from mako.template import Template
import numpy as np
import os




c_prog_header_tmpl = r"""


// #define DEBUG 1

/*
Two defines control the setup:
    ON_NIOS
    PC_DEBUG
*/







// By default, we run optimised on the PC:
#ifndef ON_NIOS
#define ON_NIOS true
#endif

#ifndef PC_DEBUG
#define PC_DEBUG false
#endif




#include "neurounits/neurounits.h"



// Define the fixed-point format:
const int VAR_NBITS = ${nbits};
#if SAFEINT 
typedef neurounits::Fixed<SafeInt, VAR_NBITS> FixedType;
#else 
typedef neurounits::Fixed<int, VAR_NBITS> FixedType;
#endif



// Define what classes to use in the fixed point:
typedef FixedType::IType32 IntType;








#if ON_NIOS
#define CALCULATE_FLOAT false
#define USE_HDF false
#define SAVE_HDF5_FLOAT false
#define SAVE_HDF5_INT false
#define SAFEINT false

#else

#if PC_DEBUG
#define CALCULATE_FLOAT true
#define USE_HDF true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT true
#define SAFEINT true
#define _GLIBCXX_DEBUG true

#else
#define CALCULATE_FLOAT false
#define USE_HDF true
#define SAVE_HDF5_FLOAT true
#define SAVE_HDF5_INT false
#define SAFEINT false
#endif // (PC_DEBUG)

#endif




#ifndef USE_BLUEVEC
#define USE_BLUEVEC true
#endif



## #if USE_BLUEVEC
## #include <BlueVecProxy.h>
## #endif








/* Runtime logging: */
#define RUNTIME_LOGGING_ON false
#define RUNTIME_LOGGING_STARTTIME 61.2998e-3
// #define RUNTIME_LOGGING_STARTTIME 100e-3







#if RUNTIME_LOGGING_ON

// Runtime-logging:
#define MHLOG(s) if(DBG.is_debug_log()) {s}
#define NO_MHLOG(s);


#define LOG_COMPONENT_STATEUPDATE  MHLOG
#define LOG_COMPONENT_EVENTDISPATCH NO_MHLOG
#define LOG_COMPONENT_EVENTHANDLER NO_MHLOG
#define LOG_COMPONENT_TRANSITION NO_MHLOG

#define CHECK_IN_RANGE_NODE(a,b,c,d,e)            _check_in_range(a,b,c,d,e, DBG.is_debug_check() )
#define CHECK_IN_RANGE_VARIABLE(a,b,c,d,e)        _check_in_range(a,b,c,d,e, DBG.is_debug_check() )
#define CHECK_IN_RANGE_VARIABLE_DELTA(a,b,c,d,e)  _check_in_range(a,b,c,d,e, DBG.is_debug_check() )

struct DebugCfg
{
    const bool is_debug_check() { return check_on; }
    const bool is_debug_log() { return log_on; }

    bool check_on;
    bool log_on;

    DebugCfg() : check_on(false), log_on(false)
        {}

    void update(double time)
    {
        if(time >= RUNTIME_LOGGING_STARTTIME)
        {
            check_on = true;
            log_on = true;
        }
    }
};

#else // RUNTIME_LOGGING_ON

#define LOG_COMPONENT_STATEUPDATE(a)
#define LOG_COMPONENT_EVENTDISPATCH(a)
//#define LOG_COMPONENT_EVENTHANDLER(a)
#define LOG_COMPONENT_EVENTHANDLER(a)
#define LOG_COMPONENT_TRANSITION(a)

#define CHECK_IN_RANGE_NODE(a,b,c,d,e) (a)
#define CHECK_IN_RANGE_VARIABLE(a,b,c,d,e) (a)
#define CHECK_IN_RANGE_VARIABLE_DELTA(a,b,c,d,e) (a)

struct DebugCfg
{
    void update(double time) { }
};

#endif





DebugCfg DBG;




#define DISPLAY_LOOP_INFO true




/* ------- General  ----------- */
#define CHECK_INT_FLOAT_COMPARISON true
#define CHECK_INT_FLOAT_COMPARISON_FOR_EXP false

const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT = 100;
const int ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT_FOR_EXP = 300;



// Define how often to record values:
//const int record_rate = int( 1.e-3 /  ${dt_float} ) + 1;
//const int record_rate = 10;
const int record_rate = 10;






#include <list>
#include <stdio.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <iomanip>
#include <sstream>
#include <assert.h>
#include <climits>
#include <stdint.h>
#include <string>
using namespace std;



## #include <BlueVecProxy.h>

// Headers to use when we are not on the NIOS:
#if ON_NIOS
#include <stdio.h>
#include <alt_types.h>
#include <system.h>
#include <io.h>
#include "HAL/inc/sys/alt_cache.h"
#include "nios_tools/mh_buffer.h"
using mhbuffer::array;



#else

#include <boost/format.hpp>
#include <boost/assign/list_of.hpp>
#include <cinttypes>
#include <fenv.h>
#include <gmpxx.h>
#include <array>
#endif




#if USE_HDF
#include <unordered_map>
// For Saving the data to HDF5:
#include "hdfjive.h"
#include "hdfjive-neuro.h"
const string output_filename = "${output_filename}";
const string simulation_name = "Sim1";



// Data types used for storing in HDF5:
const hid_t hdf5_type_int = H5T_NATIVE_INT;
const hid_t hdf5_type_float = H5T_NATIVE_DOUBLE;

typedef int T_hdf5_type_int;
typedef double T_hdf5_type_float;
#endif






//typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;



















struct LookUpTables
{
    LookUpTables()
        : exponential(8, 5)    // (nbits, upscale)
        //: exponential(5, 3)    // (nbits, upscale)
    { }

    LookUpTableExpPower2<VAR_NBITS, IntType> exponential;
};

LookUpTables lookuptables;


















#if USE_BLUEVEC
#include "/home/mh735/hw/BlueVec/BlueVec.h"
//typedef Stream DataStream;
#endif































namespace IntegerFixedPoint
{

    // New fixed point classes:
    template<int UPSCALE>
    struct ScalarType
    {
        IntType v;
        explicit ScalarType(int v) : v(v) { }
        ScalarType() {};

        const static int UP = UPSCALE;

        // Automatic rescaling during assignments:
        template<int OTHER_UP>
        ScalarType<UPSCALE>& operator=(const ScalarType<OTHER_UP>& rhs)
        {
            v = rhs.rescale_to<UPSCALE>().v;
            return *this;
        }



        // Explicit rescaling between different scaling factors:
        template<int NEW_UPSCALE>
        ScalarType<NEW_UPSCALE> rescale_to( ) const
        {
            return ScalarType<NEW_UPSCALE>( auto_shift(v, UPSCALE - NEW_UPSCALE) );
        }

        inline double to_float() const
        {
            return FixedType::Conversion::to_float(v, UP);
        }
        inline IntType to_int() const
        {
            return v;
        }

        bool operator<=( const ScalarType<UPSCALE>& rhs) const
        {
            return v <=rhs.v;
        }


        template<int RHS_UPSCALE>
        inline bool operator<( const ScalarType<RHS_UPSCALE>& rhs) const
        {
            if(  UPSCALE < RHS_UPSCALE) {
                return (this->rescale_to<RHS_UPSCALE>().v < rhs.v);
            } else if( UPSCALE > RHS_UPSCALE) {
                return ( v < rhs.rescale_to<UPSCALE>().v );
            } else {
                return (v < rhs.v);
            }
        }
    };


    template<int UOUT>
    struct ScalarOp
    {
        template<int U1, int U2>
        static inline ScalarType<UOUT> add( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = FixedType::Ops::do_add_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> sub( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = FixedType::Ops::do_sub_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> mul( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = FixedType::Ops::do_mul_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> div( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = FixedType::Ops::do_div_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1>
        static inline ScalarType<UOUT> exp( const ScalarType<U1>& a)
        {
            return ScalarType<UOUT> ( FixedType::Ops::int_exp( a.v, U1, UOUT, -1, lookuptables.exponential ) );
        }

    };
};




























namespace DoubleFixedPoint
{

    // New fixed point classes:
    template<int UPSCALE>
    struct ScalarType
    {
        double v_float;
        explicit ScalarType(int v) : v_float(FixedType::Conversion::to_float(v, UPSCALE)) { }
        explicit ScalarType(long unsigned int v) : v_float(FixedType::Conversion::to_float(v, UPSCALE)) { }
        explicit ScalarType(double v) : v_float(v) { }
        ScalarType() {};

        const static int UP = UPSCALE;

        // Automatic rescaling during assignments:
        template<int OTHER_UP>
        ScalarType<UPSCALE>& operator=(const ScalarType<OTHER_UP>& rhs)
        {
            v_float = rhs.v_float;
            return *this;
        }

        // Explicit rescaling between different scaling factors:
        template<int NEW_UPSCALE>
        ScalarType<NEW_UPSCALE> rescale_to( ) const
        {
            return ScalarType<NEW_UPSCALE>( v_float );
        }

        inline double to_float() const
        {
            return v_float;
        }
        inline IntType to_int() const
        {
            return (FixedType::Conversion::from_float(v_float,UPSCALE) );
        }



        // No implicit scaling-conversion:
        bool operator<=( const ScalarType<UPSCALE>& rhs) const
        {
            return v_float <= rhs.v_float;
        }


        template<int RHS_UPSCALE>
        inline
        bool operator<( const ScalarType<RHS_UPSCALE>& rhs) const
        {
            return v_float < rhs.v_float;
        }

    };


    template<int UOUT>
    struct ScalarOp
    {
        template<int U1, int U2>
        static inline ScalarType<UOUT> add( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            return ScalarType<UOUT> ( a.v_float + b.v_float );
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> sub( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            return ScalarType<UOUT> ( a.v_float - b.v_float );
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> mul( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            return ScalarType<UOUT> ( a.v_float * b.v_float );
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> div( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            return ScalarType<UOUT> ( a.v_float / b.v_float );
        }

        template<int U1>
        static inline ScalarType<UOUT> exp( const ScalarType<U1>& a)
        {
            return ScalarType<UOUT>( std::exp(a.to_float()) );
        }

    };
};





namespace StdCVectorType
{
    template<typename DATATYPE_, int SIZE>
    struct DataVector
    {
        typedef DATATYPE_ DATATYPE;
        DATATYPE* _data; //[SIZE];

        // Default Constructor - initialise everything to zero
        DataVector()
        {
            assert(sizeof(int)==sizeof(DATATYPE));
            #if USE_BLUEVEC
            _data = (DATATYPE*) bvMalloc(sizeof(DATATYPE) * SIZE);
            #else
            _data = (DATATYPE*) malloc(sizeof(DATATYPE) * SIZE);
            #endif
            for(int i=0;i<SIZE;i++) _data[i] = DATATYPE(0);
        }

        DataVector( int t )
        {
            assert(sizeof(int)==sizeof(DATATYPE));
            #if USE_BLUEVEC
            _data = (DATATYPE*) bvMalloc(sizeof(DATATYPE) * SIZE);
            #else
            _data = (DATATYPE*) malloc(sizeof(DATATYPE) * SIZE);
            #endif
            for(int i=0;i<SIZE;i++) _data[i] = DATATYPE(t);
        }

        DATATYPE& operator[](size_t index)
        {
            return _data[index];
        }



    };

    template<int SIZE>
    struct BoolVector
    {
        bool _data[SIZE];
        BoolVector() {}

        bool& operator[](size_t index)
        {
            return _data[index];
        }
    };





};









using IntegerFixedPoint::ScalarType;
using IntegerFixedPoint::ScalarOp;


using StdCVectorType::DataVector;
using StdCVectorType::BoolVector;









#if USE_BLUEVEC




struct BoolStream
{
    Stream s;
    BoolStream(Stream s) : s(s) {}
};




BoolStream operator||( const BoolStream& lhs, const BoolStream& rhs ) { return BoolStream( lhs.s || rhs.s ); }
BoolStream operator&&( const BoolStream& lhs, const BoolStream& rhs ) { return BoolStream( lhs.s && rhs.s ); }









// New fixed point classes:
template<int UPSCALE>
struct FixedPointStream
{
    Stream s;
    explicit FixedPointStream(int k) : s(constant(k))  {}
    explicit FixedPointStream(int* pData) : s(load(pData)) {}
    explicit FixedPointStream(Stream s) : s(s) { }



    const static int UP = UPSCALE;

    // Automatic rescaling during assignments:
    template<int OTHER_UP>
    FixedPointStream<UPSCALE>& operator=(const FixedPointStream<OTHER_UP>& rhs)
    {
        s = rhs.rescale_to<UPSCALE>().s;
        return *this;
    }



    // Explicit rescaling between different scaling factors:
    template<int NEW_UPSCALE>
    FixedPointStream<NEW_UPSCALE> rescale_to( ) const
    {
        if(UPSCALE==NEW_UPSCALE) {
            return FixedPointStream<NEW_UPSCALE>(s);
        } else if(UPSCALE>NEW_UPSCALE){
            return FixedPointStream<NEW_UPSCALE>( s << (UPSCALE-NEW_UPSCALE) );
        } else{
            return FixedPointStream<NEW_UPSCALE>( s >> (NEW_UPSCALE-UPSCALE) );
        }

        // WAS:
        //return FixedPointStream<NEW_UPSCALE>( auto_shift(s, UPSCALE - NEW_UPSCALE) );
    }


    bool operator<=( const FixedPointStream<UPSCALE>& rhs) const
    {
        return s <=rhs.s;
    }


    template<int RHS_UPSCALE>
    inline BoolStream operator<( const FixedPointStream<RHS_UPSCALE>& rhs) const
    {
        if(  UPSCALE < RHS_UPSCALE) {
            return (this->rescale_to<RHS_UPSCALE>().s < rhs.s);
        } else if( UPSCALE > RHS_UPSCALE) {
            return ( s < rhs.rescale_to<UPSCALE>().s );
        } else {
            return (s < rhs.s);
        }
    }
};












template<int UOUT_>
struct FixedPointStreamOp
{
    static const int UOUT = UOUT_;

    template<int U1, int U2>
    static inline FixedPointStream<UOUT> add( const FixedPointStream<U1>& a, const FixedPointStream<U2>& b)
    {
        return FixedPointStream<UOUT> (a.template rescale_to<UOUT>().s + b.template rescale_to<UOUT>().s);
    }

    template<int U1, int U2>
    static inline FixedPointStream<UOUT> sub( const FixedPointStream<U1>& a, const FixedPointStream<U2>& b)
    {
        return FixedPointStream<UOUT> (a.template rescale_to<UOUT>().s - b.template rescale_to<UOUT>().s);
    }

    template<int U1, int U2>
    static inline FixedPointStream<UOUT> mul( const FixedPointStream<U1>& a, const FixedPointStream<U2>& b)
    {
        return FixedPointStream<UOUT> ( multiply64_and_rshift(a.s, b.s, -(U1+U2-UOUT-(VAR_NBITS-1)) ) );

    }

    template<int U1, int U2>
    static inline FixedPointStream<UOUT> div( const FixedPointStream<U1>& a, const FixedPointStream<U2>& b)
    {
        return FixedPointStream<UOUT> ( divide64_and_rshift(a.s, b.s, -(U1-U2-UOUT) ) );
        //return divide64_and_rshift(v1, v2, -(up1-up2-up_local) );
        //return FixedPointStream<UOUT> (a.template rescale_to<UOUT>().s / b.template rescale_to<UOUT>().s);
    }





    // Exponential lookup on the BlueVec emulator:
    static
    Stream _get_upscale_for_xindex(Stream index)
    {
        LookUpTableExpPower2<VAR_NBITS, IntType>& table = lookuptables.exponential;

        const NativeInt32 n_bits_recip_ln_two = 12;
        const NativeInt32 recip_ln_two_as_int =  NativeInt32( ceil(recip_ln_two * pow(2.0, n_bits_recip_ln_two) ) );
        const IntType P = (table.upscale+1-n_bits_recip_ln_two-table.nbits_table) * -1;
        Stream result_int = ((recip_ln_two_as_int *(index - table.table_size_half) )>> P) + 1;

        return result_int;
    }





    template<int U1>
    static inline FixedPointStream<UOUT> exp( const FixedPointStream<U1>& a)
    {

        const Stream& x = a.s;
        const IntType up_x = U1;
        const IntType up_out = UOUT;

        ##IntType expr_id=-1;

        LookUpTableExpPower2<VAR_NBITS, IntType>& table = lookuptables.exponential;

        //bvPrint("");

        //bvPrint("Calculating Exponential:");
        //bvPrint(string(" -- UOUT:") + boost::lexical_cast<string>(UOUT) );
        //bvPrint(string(" -- U1:") + boost::lexical_cast<string>(U1) );
        //bvPrint(a.s);

        const IntType nbit_variables = IntType( VAR_NBITS );

        // 1. Calculate the X-indices to use to lookup in the table with:
        IntType rshift = -(up_x - nbit_variables -table.upscale+table.nbits_table);
        //bvPrint( string("rshift:") + boost::lexical_cast<string>(rshift));
        Stream table_index = (x>>rshift) + table.table_size_half;

        // 2. Lookup the yvalues, and also account for differences in fixed point format:
        int lut = -1;

        //bvPrint(" -- (About to lookup in table) ");
        //bvPrint(table_index);
        Stream yn =   lookup_lut(lut, table_index) ;
        Stream yn1 =  lookup_lut(lut, table_index+1) ;

        //bvPrint(" -- (Values found:) ");
        //bvPrint(yn);
        ////bvPrint(yn1);

        // 2a.Find the x-values at the each:
        Stream xn  = (((x>>rshift)+0) << rshift);


        Stream L1 = _get_upscale_for_xindex(table_index);
        Stream L2 = _get_upscale_for_xindex(table_index+1);

        Stream yn_upscale =   L1;
        Stream yn1_upscale =  L2;


        // 3. Perform the linear interpolation:
        Stream yn_rel_upscale = yn1_upscale-yn_upscale;
        Stream yn_rescaled = (yn>>yn_rel_upscale);


        //REPLACED: Stream d1 = auto_shift(yn, yn_upscale-up_out);
        Stream shift = yn_upscale-up_out;
        Stream d1 = ::ifthenelse( shift >= 0, yn << shift, yn >> (-shift));

        Stream d2 = multiply64_and_rshift( (yn1-yn_rescaled), (x-xn), (yn1_upscale - up_out-rshift) * -1 );

        FixedPointStream<UOUT> res = FixedPointStream<UOUT>( d1 + d2 );
        //bvPrint("Result:");
        //bvPrint(res.s);


        //bvPrint("Finished calculating exponential:");
        //bvAssert();
        return res;














    }


    template<int U1, int U2>
    static inline FixedPointStream<UOUT> ifthenelse( const BoolStream& p, const FixedPointStream<U1>& a, const FixedPointStream<U2>& b)
    {
        setCond(p.s);
        return FixedPointStream<UOUT>( cond(a.template rescale_to<UOUT>().s,b .template rescale_to<UOUT>().s) );
    }




};





#endif
































const ScalarType<${dt_upscale}> dt_fixed( ${dt_int} );


const IntType time_upscale = IntType(${time_upscale});


typedef ScalarType<time_upscale>  TimeType;

struct TimeInfo
{
    const IntType step_count;

    const TimeType time_fixed;

    TimeInfo(IntType step_count)
        : step_count(step_count),
          //time_fixed(  inttype32_from_inttype64<IntType>( auto_shift64( get_value64(dt_fixed.v) * get_value64(step_count), get_value64(dt_fixed.UP - time_upscale) ))  )
          time_fixed(  inttype32_from_inttype64<IntType>( auto_shift64( get_value64(dt_fixed.to_int() ) * get_value64(step_count), get_value64(dt_fixed.UP - time_upscale) ))  )
    {

    }

};


typedef ScalarType<time_upscale>  SpikeTime;

struct SpikeEmission
{
    const SpikeTime time;
    SpikeEmission(const SpikeTime& time) : time(time) {}
};



void record_output_event(IntType global_buffer, const SpikeEmission& evt );
void record_input_event(IntType global_buffer, const SpikeEmission& evt );









namespace rnd
{

    /*

    ('Taken from : http://www.helsbreth.org/random/rng_kiss.html )
    // MH: THIS HAS BEEN ADJUSTED TO BEHAVE THE SAME ON 32 and 64 bit platforms (TO BE TESTED!)
     KISS

     the idea is to use simple, fast, individually promising
     generators to get a composite that will be fast, easy to code
     have a very long period and pass all the tests put to it.
     The three components of KISS are
            x(n)=a*x(n-1)+1 mod 2^32
            y(n)=y(n-1)(I+L^13)(I+R^17)(I+L^5),
            z(n)=2*z(n-1)+z(n-2) +carry mod 2^32
     The y's are a shift register sequence on 32bit binary vectors
     period 2^32-1;
     The z's are a simple multiply-with-carry sequence with period
     2^63+2^32-1.  The period of KISS is thus
          2^32*(2^32-1)*(2^63+2^32-1) > 2^127
    */

    #define ulong unsigned long

    static ulong kiss_x = 1;
    static ulong kiss_y = 2;
    static ulong kiss_z = 4;
    static ulong kiss_w = 8;
    static ulong kiss_carry = 0;
    static ulong kiss_k;
    static ulong kiss_m;

    inline ulong do_mask(ulong x){ return ( x & 0xFFFFFFFF); }

    void seed_rand_kiss(ulong seed) {
        kiss_x = seed | 1;
        kiss_y = seed | 2;
        kiss_z = seed | 4;
        kiss_w = seed | 8;
        kiss_carry = 0;
    }

    ulong rand_kiss() {
        kiss_x = do_mask(do_mask(kiss_x * 69069) + 1 );
        kiss_y = do_mask( kiss_y ^  do_mask( kiss_y << 13 ) );
        kiss_y = do_mask( kiss_y ^ do_mask((kiss_y >> 17)));
        kiss_y = do_mask( kiss_y ^ do_mask((kiss_y << 5))) ;
        kiss_k = do_mask((kiss_z >> 2) + (kiss_w >> 3) + (kiss_carry >> 2));
        kiss_m = do_mask(kiss_w + kiss_w + kiss_z + kiss_carry);
        kiss_z = kiss_w;
        kiss_w = kiss_m;
        kiss_carry = do_mask( kiss_k >> 30 );

        ulong res = do_mask(kiss_x + kiss_y + kiss_w) / 2.0;

        return res;
    }


    double rand_in_range(double min, double max)
    {
        double r = (double) rand_kiss() / INT_MAX;
        return r * (max-min) + min;
    }





    template<int UP>
    struct Rnd
    {

        template<int U1, int U2>
        static ScalarType<UP> uniform(ScalarType<U1> min, ScalarType<U2> max)
        {
            return ScalarType<UP>(
                FixedType::Conversion::from_float(
                    rand_in_range(
                        min.to_float(),
                        max.to_float()
                        ), UP) );
        }
    };




}


IntType _check_in_range(IntType val, IntType upscale, double min, double max, const std::string& description, bool do_check)
{
    if(! do_check ) return val;
    double value_float = FixedType::Conversion::to_float(val, upscale);

    // Addsmall tolerance, to account for constants:
    double tolerance = 0.1;
    if(max > 0) max *= (1.+tolerance);
    else max /= (1.+tolerance);
    if(min < 0) min *= (1.+tolerance);
    else min /= (1.+tolerance);




    if(!( value_float <= max))
    {

        double pc_out = (value_float - max) / (max-min) * 100.;

        if(pc_out > 1)
        {
            cout << "\ncheck_in_range: (min):" << min << std::flush;
            cout << "\ncheck_in_range: (max):" << max << std::flush;
            cout << "\n\nOverflow on:" << description;
            cout << "\nvalue_float= " << value_float << " between(" << min << "," << max << ")?" << std::flush;
            cout << "\n  --> Amount out: " << pc_out << "%";
            cout << "\n";

            assert(0);

        }

    }
    if( !( value_float >= min || min >0))
    {
        double pc_out = (min - value_float) / (max-min) * 100.;

        if(pc_out > 1)
        {
            cout << "\ncheck_in_range: (min):" << min  << std::flush;
            cout << "\ncheck_in_range: (max):" << max  << std::flush;
            cout << "\n\nOverflow on:" << description;
            cout << "\nvalue_float= " << value_float << " between(" << min << "," << max << ")?" << std::flush;
            cout << "\n  --> Amount out: " << pc_out << "%";
            cout << "\n";
            assert(0);
        }
    }

    return val;
}









// Declarations:
%for projection in network.event_port_connectors:
// Event Coupling:
namespace NS_eventcoupling_${projection.name}
{
    void dispatch_event(IntType src_neuron, const TimeInfo& time_info );
}
%endfor

"""



c_population_details_tmpl = r"""

namespace NS_${population.name}
{
    // Input event types:
    namespace input_event_types
    {
    %for in_port in population.component.input_event_port_lut:
        struct InEvent_${in_port.symbol}
        {
            TimeType delivery_time;
            %for param in in_port.parameters:
            typedef ScalarType<${param.annotations['fixed-point-format'].upscale}> ${param.symbol}Type; // Upscale: ${param.annotations['fixed-point-format'].upscale}
            ${param.symbol}Type ${param.symbol}; // Upscale: ${param.annotations['fixed-point-format'].upscale}
            %endfor

            InEvent_${in_port.symbol}( TimeType delivery_time ${ ' '.join( [ ', %sType %s' % (param.symbol,param.symbol) for param in in_port.parameters ] ) })
              : delivery_time(delivery_time) ${ ' '.join( [ ',%s(%s)' % (param.symbol,param.symbol) for param in in_port.parameters ] ) }
            { }

        };

    %endfor
    }

    namespace output_event_types
    {
    %for in_port in population.component.output_event_port_lut:
        struct OutEvent_${in_port.symbol}
        {
            TimeType delivery_time;
            %for param in in_port.parameters:
            typedef ScalarType<${param.annotations['fixed-point-format'].upscale}> ${param.symbol}Type; // Upscale: ${param.annotations['fixed-point-format'].upscale}
            ${param.symbol}Type ${param.symbol}; // Upscale: ${param.annotations['fixed-point-format'].upscale}
            %endfor

            OutEvent_${in_port.symbol}( TimeType delivery_time ${ ' '.join( [ ',%sType %s' % (param.symbol,param.symbol) for param in in_port.parameters ] ) })
              : delivery_time(delivery_time) ${ ' '.join( [ ',%s(%s)' % (param.symbol,param.symbol) for param in in_port.parameters ] ) }
              { }

        };

    %endfor
    }








// Define the data-structures:
struct NrnPopData
{
    static const int size = ${population.get_size()};



    // Parameters:
    % for p in population.component.parameters:
    typedef  DataVector<  ScalarType<${p.annotations['fixed-point-format'].upscale}>, size> T_${p.symbol};
    T_${p.symbol} ${p.symbol};
    % endfor

    // Supplied:
    % for sv_def in population.component.suppliedvalues:
    typedef  DataVector<  ScalarType<${sv_def.annotations['fixed-point-format'].upscale}>, size> T_${sv_def.symbol};
    T_${sv_def.symbol} ${sv_def.symbol};
    % endfor

    // Assignments:
    % for ass in population.component.assignedvalues:
    typedef DataVector<  ScalarType<${ass.annotations['fixed-point-format'].upscale}>, size> T_${ass.symbol};
    T_${ass.symbol} ${ass.symbol};
    % endfor

    // States:
    % for sv_def in population.component.state_variables:
    typedef  DataVector<  ScalarType<${sv_def.annotations['fixed-point-format'].upscale}>, size> T_${sv_def.symbol};
    T_${sv_def.symbol} ${sv_def.symbol};
    typedef  DataVector<  ScalarType<${sv_def.annotations['fixed-point-format'].delta_upscale}>, size> T_d_${sv_def.symbol};
    T_d_${sv_def.symbol} d_${sv_def.symbol};

    % endfor




    // Random Variable nodes
    %for rv, _pstring in rv_per_population:
    <% rv_node_name = "RV%s" % rv.annotations['node-id'] %>
    ScalarType<${rv.annotations['fixed-point-format'].upscale}> RV${rv.annotations['node-id']};
    %endfor

    %for rv, _pstring in rv_per_neuron:
    <% rv_node_name = "RV%s" % rv.annotations['node-id'] %>
    typedef DataVector<  ScalarType<${rv.annotations['fixed-point-format'].upscale}>, size> T_${rv_node_name};
    T_${rv_node_name} ${rv_node_name};
    %endfor


    // AutoRegressive nodes:
    %for ar in population.component.autoregressive_model_nodes:
    <% ar_node_name = "AR%s" % ar.annotations['node-id'] %>
    typedef DataVector<  ScalarType<${ar.annotations['fixed-point-format'].upscale}>, size> T_${ar_node_name};
    T_${ar_node_name} ${ar_node_name};
    //ScalarType<${ar.annotations['fixed-point-format'].upscale}> ${ar_node_name}[size];
    %for i in range( len( ar.coefficients)):
    //ScalarType<${ar.annotations['fixed-point-format'].upscale}> _${ar_node_name}_t${i}[size];
    T_${ar_node_name} _${ar_node_name}_t${i};
    %endfor
    %endfor

    // Crossing Nodes:
    %for cc in population.component.conditioncrosses_nodes:
    BoolVector<size> C_${cc.annotations['node-id']}_lhs_is_gt_rhs;
    BoolVector<size> C_${cc.annotations['node-id']}_lhs_is_gt_rhs_prev;
    %endfor

    // Regimes:
    %for rtgraph in population.component.rt_graphs:
    %if len(rtgraph.regimes) > 1:
    struct Regime${rtgraph.name} {
        static const int NO_CHANGE = 0;
    %for index, regime in enumerate(rtgraph.regimes):
        static const int ${rtgraph.name}${regime.name} = ${index} + 1;
    %endfor
    };
    typedef int RegimeType${rtgraph.name};
    RegimeType${rtgraph.name} current_regime_${rtgraph.name}[size];
    %endif
    %endfor


    // Incoming event queues:
    %for in_port in population.component.input_event_port_lut:
    typedef std::list<input_event_types::InEvent_${in_port.symbol}>  EventQueueType_${in_port.symbol};
    EventQueueType_${in_port.symbol} incoming_events_${in_port.symbol}[size];
    %endfor

};



void set_supplied_values_to_zero(NrnPopData& d)
{
% for sv_def in population.component.suppliedvalues:
    for(int i=0;i<NrnPopData::size;i++) d.${sv_def.symbol}[i] = NrnPopData::T_${sv_def.symbol}::DATATYPE( 0 );
% endfor
}






void initialise_autoregressivenodes(NrnPopData& d)
{
     %for ar in population.component.autoregressive_model_nodes:
     for(int i=0;i<NrnPopData::size;i++) d.AR${ar.annotations['node-id']}[i] = ScalarType<${ar.annotations['fixed-point-format'].upscale}>(0);
     %for i in range( len( ar.coefficients)):
     for(int i=0;i<NrnPopData::size;i++) d._AR${ar.annotations['node-id']}_t${i}[i] = ScalarType<${ar.annotations['fixed-point-format'].upscale}>(0);
     %endfor
     %endfor

}

void initialise_randomvariables(NrnPopData& d)
{
    // Random Variable nodes
    %for rv, rv_param_string in rv_per_population:
    d.RV${rv.annotations['node-id']} = rnd::Rnd<${rv.annotations['fixed-point-format'].upscale}>::${rv.functionname}(${rv_param_string});
    %endfor

    for(int i=0;i<NrnPopData::size;i++)
    {
        %for rv, rv_param_string in rv_per_neuron:
        d.RV${rv.annotations['node-id']}[i] = rnd::Rnd<${rv.annotations['fixed-point-format'].upscale}>::${rv.functionname}( ${rv_param_string});
        %endfor
    }
}

void initialise_statevars(NrnPopData& d)
{
    for(int i=0;i<NrnPopData::size;i++)
    {
        % for sv_def in population.component.state_variables:
        d.${sv_def.symbol}[i] = ScalarType<${sv_def.initial_value.annotations['fixed-point-format'].upscale}>( ${sv_def.initial_value.annotations['fixed-point-format'].const_value_as_int} );
        % endfor

        // Initial regimes:
        %for rtgraph in population.component.rt_graphs:
        %if len(rtgraph.regimes) > 1:
        d.current_regime_${rtgraph.name}[i] = NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${rtgraph.default_regime.name};
        %endif
        %endfor
    }
}

void initialise_parameters(NrnPopData& d)
{

    for(int i=0;i<NrnPopData::size;i++)
    {
%for param in population.component.parameters:
        d.${param.symbol}[i] = ${ writer_stdc.visit(population.parameters[param.symbol] ) }  ;
%endfor
    }



}


namespace event_handlers
{
%for out_event_port in population.component.output_event_port_lut:

    //Events emitted from: ${population.name}
    void on_${out_event_port.symbol}(IntType index, const TimeInfo& time_info /*Params*/)
    {
        LOG_COMPONENT_EVENTHANDLER(std::cout << "\nOutputEvent ${population.name}[" << index  << "]::${out_event_port.symbol}: "; )

        // 1. Lets see what to record from these:
        %for poprec in network.all_output_event_recordings:
        %if poprec.src_population == population:
        // Lets record!
        if( (index >= IntType(${poprec.src_pop_start_index})) && (index < IntType(${poprec.src_pop_end_index})))
        {
            record_output_event( IntType(${poprec.global_offset}) + index - IntType(${poprec.src_pop_start_index}) , SpikeEmission(time_info.time_fixed) );
            <%pop,port=population,out_event_port%>
        }
        %endif
        %endfor

        // 2. Lets see which populations the event is routed to:
        %if (population,out_event_port) in evt_src_to_evtportconns:
        %for conn in evt_src_to_evtportconns[(population,out_event_port)]:
        // Via ${conn.name} -> ${conn.dst_population.name}
        LOG_COMPONENT_EVENTHANDLER(std::cout << "\n -- Dispatching via connection: ${conn.name} to ${conn.dst_population.name}::${conn.dst_port.symbol} "; )
        NS_eventcoupling_${conn.name}::dispatch_event(index, time_info);
        %endfor
        %endif



    }
%endfor
}







## Template functions:
## ===================
<%def name="trigger_transition_block(tr, rtgraph)">
            if(${writer_stdc.to_c(tr.trigger, population_access_index='i', data_prefix='d.')})
            {
                // Actions ...
                %for action in tr.actions:
                ${writer_stdc.to_c(action, population_access_index='i', data_prefix='d.')};
                %endfor

                // Switch regime?
                %if tr.changes_regime():
                if(next_regime != NrnPopData::Regime${rtgraph.name}::NO_CHANGE &&
                   next_regime != NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${tr.target_regime.name})
                {
                    assert(0); //Multiple transitions detected.
                }
                next_regime = NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${tr.target_regime.name};
                %endif
            }
</%def>



<%def name="trigger_event_block(tr, rtgraph, population)">
            while(true)
            {
                if( d.incoming_events_${tr.port.symbol}[i].size() == 0 ) break;

                input_event_types::InEvent_${tr.port.symbol}& evt = d.incoming_events_${tr.port.symbol}[i].front();
                TimeType evt_time = evt.delivery_time;

                if(evt_time <= time_info.time_fixed )
                {
                    // Handle the event:
                    LOG_COMPONENT_EVENTHANDLER( std::cout << "\nHandling InputEvent: ${population.name}[" << i << "]::${tr.port.symbol}:"; )

                    %for poprec in network.all_input_event_recordings:
                    %if (poprec.src_population == population) and (poprec.node == tr.port) :
                    // Lets record!
                    if( (i >= IntType(${poprec.src_pop_start_index})) && (i < IntType(${poprec.src_pop_end_index})))
                    {
                        record_input_event( IntType(${poprec.global_offset}) + i - IntType(${poprec.src_pop_start_index}) , SpikeEmission(time_info.time_fixed) );
                    }
                    %endif
                    %endfor

                     // Actions ...
                    %for action in tr.actions:
                    ${writer_stdc.to_c(action, population_access_index='i', data_prefix='d.')};
                    %endfor

                    // Switch regime?
                    %if tr.changes_regime():
                    if(next_regime != NrnPopData::Regime${rtgraph.name}::NO_CHANGE &&
                       next_regime != NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${tr.target_regime.name})
                    {
                        assert(0); //Multiple transitions detected.
                    }
                    next_regime = NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${tr.target_regime.name};
                    %endif

                    d.incoming_events_${tr.port.symbol}[i].pop_front();
                }
                else
                {
                    break;
                }
            }
</%def>














// Update-function
void sim_step_update_sv_sequential(NrnPopData& d, TimeInfo time_info)
{

    const ScalarType<time_upscale> t = time_info.time_fixed;

    // Serial Version:
    for(int i=0;i<NrnPopData::size;i++)
    {

        LOG_COMPONENT_STATEUPDATE(
            cout << "\n";
            cout << "\nFor ${population.name} " << i;
            cout << "\nAt: t=" << t.to_int() << "\t(" << t.to_float() * 1000.0 << "ms)";
            cout << "\nStarting State Variables:";
            cout << "\n-------------------------";
            % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
            cout << "\n d.${td.lhs.symbol}: " << d.${td.lhs.symbol}[i].to_int()  << " (" << d.${td.lhs.symbol}[i].to_float() << ")" << std::flush;
            % endfor
            cout << "\nSupplied Variables:";
            cout << "\n-------------------------";
            %for suppliedvalue in population.component.suppliedvalues:
            cout << "\n d.${suppliedvalue.symbol}: " << d.${suppliedvalue.symbol}[i].to_int()  << " (" << d.${suppliedvalue.symbol}[i].to_float() << ")" << std::flush;
            %endfor
            cout << "\nUpdates:";
            )

        // // Calculate the autoregressive nodes:
        %for ar in population.component.autoregressive_model_nodes:
        //Update the current value:
        d.${writer_stdc.to_c(ar)}[i] = ${writer_stdc.VisitAutoRegressiveModelUpdate(ar)};
        // Save the old values:
        %for i in range( len( ar.coefficients) -1 ):
        %if i==0:
        d._AR${ar.annotations['node-id']}_t0[i] = d.AR${ar.annotations['node-id']}[i];
        %else:
        d._AR${ar.annotations['node-id']}_t${i}[i] = d._AR${ar.annotations['node-id']}_t${i+1}[i] = 0;
        %endif
        %endfor
        %endfor



        // Calculate assignments:
        % for ass in population.component.ordered_assignments_by_dependancies:
        d.${ass.lhs.symbol}[i] = ${writer_stdc.to_c(ass, population_access_index='i', data_prefix='d.')} ;
        LOG_COMPONENT_STATEUPDATE( cout << "\n d.${ass.lhs.symbol}: " << d.${ass.lhs.symbol}[i].to_int()  << " (" << d.${ass.lhs.symbol}[i].to_float()  << ")" << std::flush;)
        % endfor

        // Calculate delta's for all state-variables:
        % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        <% cs1, cs2 = writer_stdc.to_c(td, population_access_index='i', data_prefix='d.') %>
        d.d_${td.lhs.symbol}[i] = ${cs1};
        d.${td.lhs.symbol}[i] = ScalarOp<NrnPopData::T_${td.lhs.symbol}::DATATYPE::UP>::add( d.${td.lhs.symbol}[i], d.d_${td.lhs.symbol}[i] ) ;

        LOG_COMPONENT_STATEUPDATE( cout << "\n delta:${td.lhs.symbol}: " << d.d_${td.lhs.symbol}[i].to_int()  << " (" << d.d_${td.lhs.symbol}[i].to_float()  << ")" << std::flush; )
        LOG_COMPONENT_STATEUPDATE( cout << "\n d.${td.lhs.symbol}: " << d.${td.lhs.symbol}[i].to_int()  << " (" << d.${td.lhs.symbol}[i].to_float()  << ")" << std::flush; )
        % endfor



        // Crossing Nodes:
        %for cc in population.component.conditioncrosses_nodes:
        // Copy the old value accross:
        d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs_prev[i] = d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i];
        // Calculate the next value:
        d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i] = ${writer_stdc._VisitOnConditionCrossing(cc)};

        %endfor

    }

    LOG_COMPONENT_STATEUPDATE( cout << "\n"; )
}






#if USE_BLUEVEC
Kernel sim_step_update_sv_bluevec_build_kernel(NrnPopData& d)
{
        Arg t;
        Stream _bv_t = constant(t);
        FixedPointStream<${time_upscale}> bv_t(_bv_t);



        Stream _bv_dt = constant( dt_fixed.to_int() );
        FixedPointStream<${dt_upscale}> bv_dt(_bv_dt);

        // A. Load in all the data (state-variables, supplied_values, random_nodes, ar-nodes):
        % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        //bvPrint("Loading ${td.lhs.symbol}");
        FixedPointStream<${td.lhs.annotations['fixed-point-format'].upscale}> bv_${td.lhs.symbol}( &(d.${td.lhs.symbol}[0].v) );
        %endfor

        % for suppl in population.component.suppliedvalues:
        FixedPointStream<${suppl.annotations['fixed-point-format'].upscale}> bv_${suppl.symbol}( &(d.${suppl.symbol}[0]).v );
        %endfor

        // Random Variable nodes
        %for rv, _pstring in rv_per_population:
        IntType RV${rv.annotations['node-id']} =  d.RV${rv.annotations['node-id']};
        %endfor
        %for rv, _pstring in rv_per_neuron:
        FixedPointStream <${rv.annotations['fixed-point-format'].upscale}> bv_RV${rv.annotations['node-id']}( &(d.RV${rv.annotations['node-id']}[0].v) );
        %endfor

        // AutoRegressive nodes:
        %for ar in population.component.autoregressive_model_nodes:
        <% ar_node_name = "AR%s" % ar.annotations['node-id'] %>
        <% ar_upscale = ar.annotations['fixed-point-format'].upscale %>
        FixedPointStream<${ar_upscale}> bv_${ar_node_name}( &(d.${ar_node_name}[0].v));
        %for i in range( len( ar.coefficients)):
        FixedPointStream<${ar_upscale}> bv__${ar_node_name}_t${i}( &(d._${ar_node_name}_t${i}[0].v));
        %endfor
        %endfor

        //FixedPointStream<${population.component.time_node.annotations['fixed-point-format'].upscale}> bv_t( time_info.time_fixed.v );








        ##// // Calculate the autoregressive nodes:
        ##%for ar in population.component.autoregressive_model_nodes:
        ##//Update the current value:
        ##d.${writer_stdc.to_c(ar)}[i] = ${writer_stdc.VisitAutoRegressiveModelUpdate(ar)};
        ##// Save the old values:
        ##%for i in range( len( ar.coefficients) -1 ):
        ##%if i==0:
        ##d._AR${ar.annotations['node-id']}_t0[i] = d.AR${ar.annotations['node-id']}[i];
        ##%else:
        ##d._AR${ar.annotations['node-id']}_t${i}[i] = d._AR${ar.annotations['node-id']}_t${i+1}[i] = 0;
        ##%endif
        ##%endfor
        ##%endfor




        // Calculate assignments:
        % for ass in population.component.ordered_assignments_by_dependancies:
        //bvPrint("");
        //bvPrint("Calculating assignment: ${ass.lhs.symbol}");
        FixedPointStream<${ass.lhs.annotations['fixed-point-format'].upscale}> bv_${ass.lhs.symbol} = ${writer_bluevec.to_c(ass, population_access_index=None, data_prefix='bv_')};
        //bvPrint("Finished calculating assignment: ${ass.lhs.symbol}");

        //bvPrint( bv_${ass.lhs.symbol}.s );
        ## %if ass.lhs.symbol=='alpha_ks_n':
        ##     bvAssert();
        ## %endif
        % endfor


        // Calculate delta's for all state-variables:
        %for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        //bvPrint("");
        //bvPrint("Calculating state variable: ${td.lhs.symbol}");
        FixedPointStream<${td.lhs.annotations['fixed-point-format'].delta_upscale}> bv_d_${td.lhs.symbol} = FixedPointStreamOp<${td.lhs.annotations['fixed-point-format'].delta_upscale}> ::mul(
                ${writer_bluevec.to_c(td.rhs_map ) },
                bv_dt
        );
        bv_${td.lhs.symbol} = FixedPointStreamOp<${td.lhs.annotations['fixed-point-format'].upscale}>::add(
                                bv_${td.lhs.symbol},
                                bv_d_${td.lhs.symbol});
        //bvPrint("Finished calculating state variable: ${td.lhs.symbol}");

        % endfor







        // Write back:
        // We need to copy all state-variables, plus anything that might be recorded, as well as anything that might trigger transition changes.
        // For now, lets just copy everything.

        % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        //bvPrint("Storing: ${td.lhs.symbol}");
        store(bv_${td.lhs.symbol}.s, &(d.${td.lhs.symbol}[0].v));
        %endfor
        % for ass in population.component.ordered_assignments_by_dependancies:
        //bvPrint("Storing: ${ass.lhs.symbol}");
        store(bv_${ass.lhs.symbol}.s, &(d.${ass.lhs.symbol}[0].v));
        % endfor





        cout << "\nBuilding Kernel" << flush;
        Kernel k = kernel();
        cout << "\nFinished building kernel" << flush;
        return k;;




}

#endif


void sim_step_update_sv_bluevec(NrnPopData& d, TimeInfo time_info)
{
#if USE_BLUEVEC
        // Only build kernel once:
        static Kernel k  = sim_step_update_sv_bluevec_build_kernel(d);

        // And run:
        //cout << "\nInvoking Kernel";
        alt_dcache_flush_all();
        call(NrnPopData::size, k, time_info.time_fixed.rescale_to<${time_upscale}>().v );


        // Crossings (to move into kernel more properly):
        for(int i=0;i<NrnPopData::size;i++)
        {
            %for cc in population.component.conditioncrosses_nodes:
            // Copy the old value accross:
            d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs_prev[i] = d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i];
            // Calculate the next value:
            d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i] = ${writer_stdc._VisitOnConditionCrossing(cc)};
            %endfor
        }

#endif

    LOG_COMPONENT_STATEUPDATE( cout << "\n"; )
}















void sim_step_update_sv(NrnPopData& d, TimeInfo time_info)
{




    // Sequential Solving:
    //sim_step_update_sv_sequential(d, time_info);
    //assert(0);

    #if USE_BLUEVEC
    sim_step_update_sv_bluevec(d, time_info);
    #else
    sim_step_update_sv_sequential(d, time_info);
    #endif


}






















void sim_step_update_rt(NrnPopData& d, TimeInfo time_info)
{

    // Make sure that we skip 2 steps before activating any crossing conditions:
    const bool is_condition_activation_guard = (time_info.step_count > 2);

    const ScalarType<time_upscale> t = time_info.time_fixed;
    //assert(t.v>=0); // Suppress compiler warning about unused variable

    for(int i=0;i<NrnPopData::size;i++)
    {
    // Resolve transitions for each rt-graph:
    %for rtgraph in population.component.rt_graphs:


        %if len(rtgraph.regimes) > 1:

        NrnPopData::RegimeType${rtgraph.name} next_regime = NrnPopData::Regime${rtgraph.name}::NO_CHANGE;

        // Non-trivial RT-graph
        switch(d.current_regime_${rtgraph.name}[get_value32(i)])
        {
        case NrnPopData::Regime${rtgraph.name}::NO_CHANGE:
            assert(0); // This is an internal error - this regime is only used as a flag internally.

        // Handle the transitions per regime:
        %for regime in rtgraph.regimes:
        case NrnPopData::Regime${rtgraph.name}::${rtgraph.name}${regime.name}:
            % if len(rtgraph.regimes) > 1 and regime.name is None:
            assert(0); // Should not be here - we should switch into a 'real' regime before we begin
            %endif

            // ==== Triggered Transitions: ====
            %for tr in population.component.conditiontriggertransitions_from_regime(regime):
            ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
            %endfor

            // ==== Event Transitions: ====
            %for tr in population.component.eventtransitions_from_regime(regime):
            ${trigger_event_block(tr, rtgraph, population)}
            %endfor

            break;
        %endfor

        }

        // And the transitions from the 'global namespace':
        // ==== Triggered Transitions: ====
        %for tr in population.component.conditiontriggertransitions_from_regime(rtgraph.get_regime(None)):
        ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
        %endfor

        // ==== Event Transitions: ====
        %for tr in population.component.eventtransitions_from_regime(rtgraph.get_regime(None)):
        ${trigger_event_block(tr, rtgraph, population)}
        %endfor




        %else:
            // And the transitions from the 'global namespace':
            // ==== Triggered Transitions: ====
            %for tr in population.component.conditiontriggertransitions_from_regime(rtgraph.get_regime(None)):
            ${trigger_transition_block(tr=tr, rtgraph=rtgraph)}
            %endfor

            // ==== Event Transitions: ====
            %for tr in population.component.eventtransitions_from_regime(rtgraph.get_regime(None)):
            ${trigger_event_block(tr, rtgraph, population)}
            %endfor

        %endif:

        // Update the next state:
        %if len(rtgraph.regimes) > 1:

        if( next_regime != NrnPopData::Regime${rtgraph.name}::NO_CHANGE)
        {
            LOG_COMPONENT_TRANSITION( cout << "\nSWitching into Regime:" << next_regime; )
            d.current_regime_${rtgraph.name}[i] = next_regime;
        }
        %endif
    %endfor
    }
}








} // End of population namespace

"""






c_print_results_tmpl = r"""


namespace NS_${population.name}
{

void print_results_from_NIOS(NrnPopData* d)
{
    // Temporarily commented out:
    // Assignments + states:
    % for ass in population.component.assignedvalues + population.component.state_variables:
    //cout << "\n#!DATA{ 'name':'${ass.symbol}' } {'size': ${nsim_steps},  'fixed_point': {'upscale':${ass.annotations['fixed-point-format'].upscale}, 'nbits':${nbits}} } [";
    //for(IntType i=IntType(0);i<GlobalConstants::nsim_steps;i++) cout << d[ get_value32(i)].${ass.symbol} << " ";
    //cout << "]\n";
    % endfor
    cout << "\n#! FINISHED\n";
}
}



"""







c_nios_plotting_tmpl = r"""

typedef vector<size_t> RecIndicesList;


#if ON_NIOS
#include "lcd_graphics.h"
#endif

struct PlotBox
{
    int x0,x1, y0,y1;
    PlotBox(int x0, int x1, int y0, int y1, int padding=0): x0(x0), x1(x1), y0(y0+padding), y1(y1-padding) {
            cout << "PlotBox()\n";

    }



};

struct Axis
{
    PlotBox box;
    int ylim_int_min;
    int ylim_int_max;
    RecIndicesList rec_indices;
    RecIndicesList x_prev;
    RecIndicesList y_prev;

    Axis( const PlotBox& box, int ylim_int_min, int ylim_int_max, RecIndicesList rec_indices)
        :   box(box),
            ylim_int_min(ylim_int_min),
            ylim_int_max(ylim_int_max),
            rec_indices(rec_indices)
        {
            cout << "Axis()\n";
        }

    void plot_axes()
    {
        plot_box( box.x0, box.x1, box.y0, box.y1, 0x77EE77);
        int y0_as_pix = yvalue_to_pixel(0);
        plot_line( box.x0, y0_as_pix, box.x1, y0_as_pix, 0x000000);

        plot_line( box.x0, box.y0, box.x0, box.y1, 0x000000);

    }


    int yvalue_to_pixel(int value)
    {
        return (int) (((float) value-ylim_int_min) / ( ylim_int_max - ylim_int_min) * ( box.y1-box.y0) ) + box.y0;
    }

    int time_to_pixel(int step_count)
    {
        return (int) (((float) step_count) / ( GlobalConstants::nsim_steps) * ( box.x1-box.x0) ) + box.x0;
    }


    void update_plot(const TimeInfo& time_info)
    {
        int px_x = time_to_pixel( time_info.step_count ) ;

        if( global_data.recordings_new.n_results_written <= 0){
            return;
        }

        RecIndicesList x_prev_new, y_prev_new;

        for(size_t i = 0; i < rec_indices.size(); i++)
        {
            int y = global_data.recordings_new.data_buffers[rec_indices[i]][global_data.recordings_new.n_results_written-1];
            int px_y = yvalue_to_pixel(y);

            if( x_prev.size() ) {
                //plot_pixel(px_x, px_y, 0x0000FF);
                plot_line(x_prev[i], y_prev[i], px_x, px_y, 0x0000FF);
            }

            x_prev_new.push_back( px_x );
            y_prev_new.push_back( px_y );

        }

        x_prev = x_prev_new;
        y_prev = y_prev_new;


    }





};



struct NIOSPlotInfo {
    const static int TimeBarXStart = 300;
    const static int TimeBarXStop = 700;
    const static int TimeBarYStart = 25;
    const static int TimeBarYStop = 50;

    const static int TimeStepsPerPixel = (int) ( GlobalConstants::nsim_steps / (TimeBarXStop - TimeBarXStart ) );

    const static int PlotRegionYStart = TimeBarYStop + 50;
    const static int PlotRegionYEnd = LCD_HEIGHT - 50;
    const static int PlotRegionYSize = PlotRegionYEnd - PlotRegionYStart;

    const static int PlotRegionSizePerGraph = PlotRegionYSize / ${len(nios_options.plots)};


    const static int PlotPadding = 20;

    vector<Axis> axes;


};


NIOSPlotInfo nios_plot_info;

void nios_plot_init()
{

    lcd_blend(0, 0x80, 0x80, 0x00);
    // Setup the screen:
    clear_screen( 0xFFFFFF);

    cout << "AT A\n" << flush;

    // The time box:
    plot_box( NIOSPlotInfo::TimeBarXStart, NIOSPlotInfo::TimeBarXStop, NIOSPlotInfo::TimeBarYStart, NIOSPlotInfo::TimeBarYStop, 0xFF00FF);


    cout << "AT B\n" << flush;


    %for i, plt in enumerate(nios_options.plots):
    {
    RecIndicesList  global_rec_indices;
    %for r in plt._global_rec_indices:
    global_rec_indices.push_back(${r});
    %endfor

    nios_plot_info.axes.push_back(
        Axis(
            PlotBox(
                50, 750,
                NIOSPlotInfo::PlotRegionYStart + (${i}) * (NIOSPlotInfo::PlotRegionSizePerGraph),
                NIOSPlotInfo::PlotRegionYStart + (${i}+1) * (NIOSPlotInfo::PlotRegionSizePerGraph),
                20
                ),
            ${plt.ylimits_int[0]},
            ${plt.ylimits_int[1]},
            global_rec_indices
            )
        );
    }
    %endfor

    cout << "AT C\n" << flush;
    for(size_t ax_i = 0; ax_i != nios_plot_info.axes.size(); ax_i++)
    {
       nios_plot_info.axes[ax_i].plot_axes();

    }

    cout << "AT D\n" << flush;







}



void nios_plot_update(const TimeInfo& time_info)
{
    int filled_x_pixels = time_info.step_count / NIOSPlotInfo::TimeStepsPerPixel;
    plot_line(
        filled_x_pixels + NIOSPlotInfo::TimeBarXStart,
        NIOSPlotInfo::TimeBarYStart,
        filled_x_pixels + NIOSPlotInfo::TimeBarXStart,
        NIOSPlotInfo::TimeBarYStop,
        0xEE00EE);


    // Update the axes:
    for(size_t ax_i = 0; ax_i != nios_plot_info.axes.size(); ax_i++)
    {
       nios_plot_info.axes[ax_i].update_plot(time_info);

    }


}







"""







c_main_loop_tmpl = r"""

#include <signal.h>
#include <ctime>




void my_terminate (int parameter)
{
    cout << "\n\nIN MY SIGNAL HANDLER\n" << flush;

    // Dump to HDF5
    {
        #if USE_HDF
        cout << "\nWriting HDF5 output" << std::flush;
        SimulationResultsPtr hdf_output = SimulationResultsFile(output_filename).Simulation(simulation_name);
        global_data.recordings_new.write_all_traces_to_hdf(hdf_output);
        global_data.recordings_new.write_all_output_events_to_hdf(hdf_output);
        #endif
    }

    cout << "\n\nERROR!!!\n\n";
    exit(0);

}









void run_simulation()
{

    #if ON_NIOS
    nios_plot_init();
    #endif


    clock_t begin_main = clock();

    // Setup the random number generator:
    rnd::seed_rand_kiss(1);

    // Setup the variables:
    %for pop in network.populations:
    NS_${pop.name}::initialise_statevars(data_${pop.name});
    NS_${pop.name}::initialise_parameters(data_${pop.name});
    NS_${pop.name}::initialise_randomvariables(data_${pop.name});
    NS_${pop.name}::initialise_autoregressivenodes(data_${pop.name} );
    %endfor


    // Setup the event connections:
    %for evt_conn in network.event_port_connectors:
    NS_eventcoupling_${evt_conn.name}::setup_connections();
    %endfor


    // Setup the analog-ports coupling:
    %for proj in network.analog_port_connectors:
    NS_${proj.name}::setup_analog_port_projection( ann_proj_data_${proj.name} );
    %endfor

    clock_t begin_sim = clock();



    global_data.recordings_new.n_results_written=0;
    for(IntType step_count=IntType(0);step_count<GlobalConstants::nsim_steps;step_count++)
    {

        TimeInfo time_info(step_count);
        DBG.update( time_info.time_fixed.to_float() );



        // C. Save the recorded values:
        if(get_value32(time_info.step_count) % get_value32(record_rate)==0)
        {
            // Save time:
            global_data.recordings_new.time_buffer[global_data.recordings_new.n_results_written] = time_info.time_fixed.to_int();
            %for poprec in network.all_trace_recordings:
            // Record: ${poprec}
            for(int i=0;i<${poprec.size};i++)
                global_data.recordings_new.data_buffers[${poprec.global_offset}+i][global_data.recordings_new.n_results_written] = data_${poprec.src_population.name}.${poprec.node.symbol}[i + ${poprec.src_pop_start_index} ].to_int();
            %endfor

            global_data.recordings_new.n_results_written++;


            #if ON_NIOS
            nios_plot_update(time_info);
            #endif
        }





        #if DISPLAY_LOOP_INFO
        if(get_value32(step_count)%100 == 0)
        {
            std::cout << "Loop: " << step_count << "\n";
            std::cout << "(t: " << time_info.time_fixed.to_float() * 1000 << "ms)\n";
            std::cout << "Total spikes emitted: " << global_data.recordings_new.nspikes_emitted << "\n";

        }
        #endif


        // 0. Reset the injected currents:
        %for pop in network.populations:
        NS_${pop.name}::set_supplied_values_to_zero(data_${pop.name});
        %endfor


        // A1. Analog port connectors:
        %for proj in network.analog_port_connectors:
        NS_${proj.name}::calculate_analog_ports(ann_proj_data_${proj.name}, data_${proj.src_population.population.name}, data_${proj.dst_population.population.name} );
        %endfor


        // B. Integrate all the state_variables of all the neurons:
        %for pop in network.populations:
        NS_${pop.name}::sim_step_update_sv( data_${pop.name}, time_info);
        %endfor

        // C. Resolve state transitions:
        %for pop in network.populations:
        NS_${pop.name}::sim_step_update_rt( data_${pop.name}, time_info);
        %endfor

    }



    clock_t end_sim = clock();


    // Dump to HDF5
    #if USE_HDF
    cout << "\nWriting HDF5 output" << std::flush;
    SimulationResultsPtr hdf_output = SimulationResultsFile(output_filename).Simulation(simulation_name);
    global_data.recordings_new.write_all_traces_to_hdf(hdf_output);
    global_data.recordings_new.write_all_output_events_to_hdf(hdf_output);
    global_data.recordings_new.write_all_input_events_to_hdf(hdf_output);
    #endif // USE_HDF


    #if ON_NIOS
    global_data.recordings_new.write_all_traces_to_console();
    #endif


    clock_t end_data_write = clock();


    printf("Simulation Complete\n");

    double elapsed_secs_total = double(end_data_write - begin_main) / CLOCKS_PER_SEC;
    double elapsed_secs_sim = double(end_sim - begin_sim) / CLOCKS_PER_SEC;
    double elapsed_secs_hdf = double(end_data_write - end_sim) / CLOCKS_PER_SEC;
    double elapsed_secs_setup = double(begin_sim - begin_main) / CLOCKS_PER_SEC;

    cout << "\nTime taken (setup):" << elapsed_secs_setup;
    cout << "\nTime taken (sim-total):"<< elapsed_secs_sim;
    cout << "\nTime taken (hdf):"<< elapsed_secs_hdf;
    cout << "\nTime taken (combined):"<< elapsed_secs_total;



}






int main()
{

    // Start the clock:


    // Lets handle signals:
    signal (SIGTERM,my_terminate);
    signal (SIGABRT,my_terminate);

    // Enable floating point exception trapping:
    #if !ON_NIOS
    //feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    feenableexcept(FE_DIVBYZERO |  FE_OVERFLOW | FE_INVALID);
    #endif //!ON_NIOS



    // Setup the exponential lookup tables for bluevec:
    #if USE_BLUEVEC
    cout << "loading LUT of size: " << lookuptables.exponential.table_size << " into BlueVec\n";
    load_lut( &(lookuptables.exponential.pData[0]), lookuptables.exponential.table_size);
    Kernel initLut = kernel();
    alt_dcache_flush_all();
    call(lookuptables.exponential.table_size*32, initLut);
    #endif


    run_simulation();




}




"""















c_analog_projection_tmpl = r"""

namespace NS_${projection.name}
{


    struct ProjData
    {
        int size;

        // Parameters:
        % for p in projection.connection_object.parameters:
        typedef  std::vector<  ScalarType<${p.annotations['fixed-point-format'].upscale}> > T_${p.symbol};
        T_${p.symbol} ${p.symbol};
        % endfor

        typedef std::vector<int> Indices_t;
        Indices_t src_indices;
        Indices_t dst_indices;



    };





    void setup_analog_port_projection( ProjData& data )
    {
        <% assert not projection.connection_object.has_state() %>

        // A. How space do we need to allocate:
        int size = ${len( projection.connector.indices ) };
        data.size = size;

        data.src_indices.resize(size);
        data.dst_indices.resize(size);
        % for p in projection.connection_object.parameters:
        data.${p.symbol}.resize(size);
        % endfor


        ### Prewrite the string for C for generating each parameter:
        <% param_func = dict([
            (p.symbol, writer_stdc.visit( projection.connection_properties[p.symbol]) ) for p in  projection.connection_object.parameters] ) %>



        // B. Lets load up our arrays:
        %for i in range( len(projection.connector.indices) ):
        // Indices: ${i}
        data.src_indices[${i}] = ${projection.connector.indices[i][0]};
        data.dst_indices[${i}] = ${projection.connector.indices[i][1]};
        % for p in projection.connection_object.parameters:
        data.${p.symbol}[${i}] = ${param_func[p.symbol]};
        % endfor
        %endfor


    }

    void calculate_analog_ports(ProjData& data, NS_${projection.src_population.population.name}::NrnPopData& src, NS_${projection.dst_population.population.name}::NrnPopData& dst)
    {
        for(int i=0;i<data.size;i++)
        {
            // Expose constant interface, by using references to alias other arrays::
            % for p in projection.connection_object.parameters:
            ScalarType<${p.annotations['fixed-point-format'].upscale}>& ${p.symbol} = data.${p.symbol}[i];
            %endfor

            // Input from other arrays:
            % for src,dst in projection.port_map:
            <%(src_comp, src_port, src_pop_str) = src %>\
            <%(dst_comp, dst_port, dst_pop_str) = dst %> \
            <% assert src_pop_str in ['Src','Dst','Conn'] %>
            <% assert dst_pop_str in ['Src','Dst','Conn'] %>
            %if dst_pop_str ==  'Conn':
            //Copy in data from: ${src_comp.name}.${src_port.symbol} to ${dst_port.symbol}:
                %if src_pop_str == 'Src':
            
            NS_${projection.src_population.population.name}::NrnPopData::T_${src_port.symbol}::DATATYPE& ${dst_port.symbol} = src.${src_port.symbol}[ data.src_indices[i] ] ;
                %elif src_pop_str == 'Dst':
            NS_${projection.dst_population.population.name}::NrnPopData::T_${src_port.symbol}::DATATYPE& ${dst_port.symbol} = dst.${src_port.symbol}[ data.dst_indices[i] ] ;
                %else:
                ** @~@~@ !!!ERRROR!!! @~@~@ **
                %endif
            %endif
            % endfor






            // A. Do the calculations:
            %for ass in projection.connection_object.ordered_assignments_by_dependancies:
            ScalarType<${ass.lhs.annotations['fixed-point-format'].upscale}> ${ass.lhs.symbol} = ${writer_stdc.visit( ass.rhs_map )};
            %endfor


            // B. Copy values out:
            % for src,dst in projection.port_map:
                <%(src_comp, src_port, src_pop_str) = src %>\
                <%(dst_comp, dst_port, dst_pop_str) = dst %>\
                <% assert src_pop_str in ['Src','Dst','Conn'] %>\
                <% assert dst_pop_str in ['Src','Dst','Conn'] %>
                %if src_pop_str == 'Conn':
                    %if dst_pop_str == 'Src':
            //Save to ${projection.src_population.name}.${src_port.symbol}
            src.${dst_port.symbol}[data.src_indices[i]] = ScalarOp<${dst_port.annotations['fixed-point-format'].upscale}>::add( src.${dst_port.symbol}[data.src_indices[i]], ${src_port.symbol});
                    %elif dst_pop_str == 'Dst':
            dst.${dst_port.symbol}[data.dst_indices[i]] = ScalarOp<${dst_port.annotations['fixed-point-format'].upscale}>::add( dst.${dst_port.symbol}[data.dst_indices[i]], ${src_port.symbol});
            //Save to ${projection.dst_population.name}.${src_port.symbol}
                    %endif
                %endif
            % endfor
        }



    }
}

"""








c_event_projection_tmpl = r"""

// Event Coupling:
namespace NS_eventcoupling_${projection.name}
{

    typedef std::vector<IntType> TargetList;
    TargetList projections[${projection.src_population.get_size()}];


    void setup_connections()
    {

        ${projection.connector.build_c( src_pop_size_expr=projection.src_population.get_size(),
                                        dst_pop_size_expr=projection.dst_population.get_size(),
                                        add_connection_functor=lambda i,j: "projections[get_value32(%s)].push_back(%s)" % (i,j),
                                        add_connection_set_functor=None
                                        ) }

        size_t n_connections = 0;
        for(size_t i=0;i<${projection.src_population.get_size()};i++) n_connections+= projections[i].size();
        cout << "\n Projection: ${projection.name} contains: " << n_connections << std::flush;
    }


    // This is the neuron index inside the whole population, so lets check its for us and dispatch if so:
    void dispatch_event(IntType src_neuron, const TimeInfo& time_info )
    {
        if( src_neuron < ${projection.src_population.start_index} || src_neuron >= ${projection.src_population.end_index} )
            return;


        const ScalarType<${projection.delay_upscale}> delay( ${projection.delay_int} );


        //string output = "";

        TargetList& targets = projections[get_value32(src_neuron - ${projection.src_population.start_index} )];
        for( TargetList::iterator it = targets.begin(); it!=targets.end();it++)
        {
            <% evt_type = 'NS_%s::input_event_types::InEvent_%s' % (projection.dst_population.population.name, projection.dst_port.symbol)%>


            TimeType evt_time = ScalarOp<time_upscale>::add(time_info.time_fixed, delay);

            // Create the event, remebering to rescale parameters between source and target appropriately:
            %for p in projection.dst_port.alphabetic_params:
            <% upscale = projection.dst_port.parameters.get_single_obj_by(symbol=p.symbol).annotations['fixed-point-format'].upscale %>
            ScalarType<${upscale}> param_${p.symbol}( ${projection.parameter_map[p.symbol].value_scaled_for_target} ) ;
            %endfor


            ${evt_type} evt(evt_time ${' '.join([',param_%s' % p.symbol for p in projection.dst_port.alphabetic_params])}  );

            int tgt_nrn_index = get_value32(*it) + ${projection.dst_population.start_index};

            data_${projection.dst_population.population.name}.incoming_events_${projection.dst_port.symbol}[tgt_nrn_index].push_back( evt ) ;

            //output += boost::lexical_cast<string>(tgt_nrn_index) + ",";
        }

        LOG_COMPONENT_EVENTDISPATCH( cout << "\n   -> Disptached to indices: [" << output << "]"; )


    }
}


"""


popl_obj_tmpl = r"""

// Setup the global variables:
%for pop in network.populations:
NS_${pop.name}::NrnPopData data_${pop.name};
%endfor

%for proj in network.analog_port_connectors:
NS_${proj.name}::ProjData ann_proj_data_${proj.name};
%endfor





struct GlobalConstants
{
    static const int nsim_steps = ${nsim_steps};
};










struct RecordMgr
{
    static const int n_expected_recording_times = int(GlobalConstants::nsim_steps / record_rate) + 1;
    static const int buffer_size = n_expected_recording_times;



    // What are we recording:
    %for poprec in network.all_trace_recordings:
    // Record: ${poprec}
    %endfor
    static const int n_rec_buffers = ${network.n_trace_recording_buffers};


    // Traces:
    typedef array<IntType, buffer_size>  RecordingBuffer;
    // Allocate the storage for the traces:
    RecordingBuffer time_buffer;
    array<RecordingBuffer, n_rec_buffers> data_buffers;
    int n_results_written;



    // Events:
    typedef  list<SpikeEmission> SpikeList;
    int nspikes_emitted;
    array<SpikeList,  ${network.n_output_event_recording_buffers} >  spikerecordbuffers_send;

    int nspikes_recv;
    array<SpikeList, ${network.n_input_event_recording_buffers}> spikerecordbuffers_recv;



    // What events are we recording:
    // NOT YET USED!
    %for pop, port in network._record_output_events:
    // Output event:    ${pop} :  ${port}
    //    -- ${port.parameters}
    typedef list< NS_${pop.name}::output_event_types::OutEvent_${port.symbol}> List${pop.name}Out${port.symbol};
    List${pop.name}Out${port.symbol} ${pop.name}_out_${port.symbol}[NS_${pop.name}::NrnPopData::size];









    %endfor







    RecordMgr()
    : n_results_written(0),
      nspikes_emitted(0)
    {
    }





    void write_all_traces_to_console()
    {

        cout << "\n\nWriting traces to HDF5";

        // Working buffers:
        int data_int[n_results_written];


        for(int t=0;t<n_results_written;t++)
        {
            data_int[t] = get_value32(time_buffer[t]);
        }



        %for i,poprec in enumerate(network.all_trace_recordings):
        {
            // Save: ${poprec}

            for(int i=0;i<${poprec.size};i++)
            {
                int buffer_offset = ${poprec.global_offset}+i;

                for(int t=0;t<n_results_written;t++)
                {
                    data_int[t] = get_value32( data_buffers[t][buffer_offset] );
                }

                <% ass = poprec.node %>
                cout << "\n#!DATA{ 'population': '${poprec.src_population.name}', 'index': '" << i <<  "',  name':'${ass.symbol}' } {'size': ${nsim_steps},  'fixed_point': {'upscale':${ass.annotations['fixed-point-format'].upscale}, 'nbits':${nbits}} } [";
                for(IntType i=IntType(0);i<n_results_written;i++) cout << data_int[get_value32(i)] << " ";
                cout << "]\n";
            }
        }
        %endfor
        cout << "\n\nFinished writing to HDF5";
    }







    #if USE_HDF
    void write_all_traces_to_hdf(SimulationResultsPtr output)
    {

        cout << "\n\nWriting traces to HDF5\n";
        T_hdf5_type_float dt_float = FixedType::Conversion::to_float(1, time_upscale);
        // New version:
        SharedTimeBufferPtr times = output->write_shared_time_buffer(n_results_written, &time_buffer[0]);
        times->get_dataset()->set_scaling_factor(dt_float);


        ## How many recs?
        <%n_tot = sum([poprec.size for poprec in network.all_trace_recordings]) %>


        int hdf_n_written = 0;
        %for i,poprec in enumerate(network.all_trace_recordings):
        // Write out values for ${poprec.src_population.name}.${poprec.node.symbol}:
        {
            for(int i=0;i<${poprec.size};i++)
            {
                int buffer_offset = ${poprec.global_offset}+i;
                int neuron_index = i + ${poprec.src_pop_start_index};
                TagList tags = boost::assign::list_of( "${','.join(poprec.tags)}")("${','.join(poprec.node.annotations['tags'])}");

                HDF5DataSet2DStdPtr pDataset = output->write_trace("${poprec.src_population.name}", neuron_index, "${poprec.node.symbol}", times, &(data_buffers[buffer_offset][0]), tags);
                pDataset->set_scaling_factor( pow(2.0, ${poprec.node.annotations['fixed-point-format'].upscale} - (VAR_NBITS-1)) );

            }
            hdf_n_written +=${poprec.size};
            cout << "\rWriting trace: " << hdf_n_written << " of " << ${n_tot} << "           ";

        }
        %endfor

        cout << "\n\nFinished Writing to HDF5";
    }




    struct SpikeEmissionExtractor
    {
        typedef SpikeEmission EVENTTYPE;
        typedef int DTYPE;
        static const int NPARAMS = 0;
        static DTYPE get_time(const EVENTTYPE& o) { return o.time.to_int(); }
        static DTYPE get_parameter_value(const EVENTTYPE& o, int i) {  assert(0);  }
        static string get_parameter_name( int i) { assert(0); }

        static const size_t NSRCINDICES = 0;
        static DTYPE get_srcindex_value(const EVENTTYPE& o, size_t i) { return 0; }
    };



    void write_all_output_events_to_hdf(SimulationResultsPtr output)
    {
        cout << "\n\nWriting output events\n";
        T_hdf5_type_float dt_float = FixedType::Conversion::to_float(1, time_upscale);
        %for i,poprec in enumerate(network.all_output_event_recordings):
        for(int i=0; i< ${poprec.size};i++)
        {
            int buffer_offset = ${poprec.global_offset}+i;
            int neuron_index = i + ${poprec.src_pop_start_index};
            TagList tags = boost::assign::list_of( "${','.join(poprec.tags)}");
            EventDataSetTuple evtdata = output->write_outputevents_byobjects_extractor<SpikeEmissionExtractor>("${poprec.src_population.name}", neuron_index, "${poprec.node.symbol}",  spikerecordbuffers_send[buffer_offset].begin(), spikerecordbuffers_send[buffer_offset].end(), tags );
            evtdata.spiketimes->set_scaling_factor(dt_float);
            cout << "\rWriting events: " << i << " of " << ${poprec.size} << "           ";
        }
        %endfor
    }

    void write_all_input_events_to_hdf(SimulationResultsPtr output)
    {
        cout << "\n\nWriting input events\n";
        T_hdf5_type_float dt_float = FixedType::Conversion::to_float(1, time_upscale);
        %for i,poprec in enumerate(network.all_input_event_recordings):
        for(int i=0; i< ${poprec.size};i++)
        {
            int buffer_offset = ${poprec.global_offset}+i;
            int neuron_index = i + ${poprec.src_pop_start_index};
            TagList tags = boost::assign::list_of( "${','.join(poprec.tags)}");
            EventDataSetTuple evtdata = output->write_inputevents_byobjects_extractor<SpikeEmissionExtractor>("${poprec.src_population.name}", neuron_index, "${poprec.node.symbol}",  spikerecordbuffers_recv[buffer_offset].begin(), spikerecordbuffers_recv[buffer_offset].end(), tags );
            evtdata.spiketimes->set_scaling_factor(dt_float);
            cout << "\rWriting events: " << i << " of " << ${poprec.size} << "           ";
        }
        %endfor
    }

    #endif //USE_HDF


































};




struct GlobalData {

    // Data-store:
    RecordMgr recordings_new;



};


GlobalData global_data;




void record_output_event( IntType global_buffer, const SpikeEmission& evt )
{
    //cout << "\n -- Recording output-event to buffer:" << global_buffer;
    global_data.recordings_new.spikerecordbuffers_send[get_value32(global_buffer)].push_back(evt);
    global_data.recordings_new.nspikes_emitted++;
}


void record_input_event( IntType global_buffer, const SpikeEmission& evt )
{
    //cout << "\n -- Recording input-event to buffer:" << global_buffer;
    global_data.recordings_new.spikerecordbuffers_recv[get_value32(global_buffer)].push_back(evt);
    global_data.recordings_new.nspikes_recv++;
}







#if USE_BLUEVEC
#include "/home/mh735/hw/BlueVec/BlueVec.cpp"
#endif


"""



from fixed_point_common import  CBasedFixedWriter, CBasedFixedWriterBlueVecOps

import hdfjive














class NIOSOptions(object):
    def __init__(self, plots, use_bluevec=True, plot_realtime=True):
        self.plots = plots
        self.use_bluevec = use_bluevec
        self.plot_realtime = plot_realtime





class CBasedEqnWriterFixedNetwork(object):
    op_file_cnt = 0

    def __init__(self,
            network,
            output_filename=None,
            output_c_filename=None,
            run=True,
            compile=True,
            CPPFLAGS=None,
            output_exec_filename=None,
            step_size=0.1e-3,
            run_until=0.3,
            as_float=False,
            nios_options=None,
            nbits=24
            ):


        # There is an opportunity here. Sometimes, the parameters are going to be constants - so
        # we can re-run the optimiser to remove constants:
        from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator
        for pop in network.populations:
            fp_ann = NodeFixedPointFormatAnnotator(nbits=nbits)

            # Annotate the parameters:
            pop.component.annotate_ast(fp_ann , ast_label='fixed-point-format-ann' )

            # And the parameters:
            for pval in pop.parameters.values():
                fp_ann.visit(pval)


        # Deal with the analog connectors
        for apc in network.analog_port_connectors:
            fp_ann = NodeFixedPointFormatAnnotator(nbits=nbits)
            # Annotate the parameters:
            apc.connection_object.annotate_ast(fp_ann , ast_label='fixed-point-format-ann' )

            #for ass in apc.connection_object.ordered_assignments_by_dependancies:

            # And the parameters:
            for pval in apc.connection_properties.values():
                fp_ann.visit(pval)



        network.finalise()


        # Integerisation of time:
        self.dt_float = step_size
        self.dt_upscale = int(np.ceil(np.log2(self.dt_float)))


        # Check all the components use the same floating point formats:
        # NBITS:
        # This is redundant now, but keep it in during transition for testing (Dec 2013)
        nbits_check = set([ pop.component.annotation_mgr._annotators['fixed-point-format-ann'].nbits for pop in network.populations])
        assert len(nbits_check) == 1
        self.nbits = list(nbits_check)[0]
        assert nbits == self.nbits


        # Where shall we save the results?
        if output_filename is None:
            output_filename = 'neuronits%03d.results.hdf' % CBasedEqnWriterFixedNetwork.op_file_cnt
            CBasedEqnWriterFixedNetwork.op_file_cnt += 1


        #ENCODING OF TIME:
        time_upscale = set([pop.component._time_node.annotations['fixed-point-format'].upscale for pop in network.populations])
        print time_upscale
        assert len(time_upscale) == 1
        self.time_upscale = list(time_upscale)[0]


        self.dt_int = NodeFixedPointFormatAnnotator.encode_value_cls(self.dt_float, self.dt_upscale, self.nbits )

        # Make sure the events can be connected:
        evt_src_to_evtportconns = {}
        for evt_conn in network.event_port_connectors:
            key = (evt_conn.src_population, evt_conn.src_port)
            if not key in evt_src_to_evtportconns:
                evt_src_to_evtportconns[key] = []
            evt_src_to_evtportconns[key].append(evt_conn)


        t_stop = run_until
        n_steps = int( t_stop / self.dt_float )
        std_variables = {
            'nsim_steps' : n_steps,
            'nbits':self.nbits,
            'dt_float' : self.dt_float,
            'dt_int' : self.dt_int,
            'dt_upscale' : self.dt_upscale,
            'time_upscale' : self.time_upscale,
            'output_filename' : output_filename,
            'network':network,
            'evt_src_to_evtportconns': evt_src_to_evtportconns,
            'as_float':as_float
                         }





        code_per_eventport_projection = []
        for proj in network.event_port_connectors:
            c = Template(c_event_projection_tmpl).render(
                                        projection=proj,
                                        **std_variables
                                            )
            code_per_eventport_projection.append(c)

        code_per_analogconnection_projection = []
        for proj in network.analog_port_connectors:
            self.writer_stdc = CBasedFixedWriter(component=proj.connection_object, population_access_index=None, data_prefix=None,)# is_connecting_component=True)
            self.writer_bluevec = CBasedFixedWriterBlueVecOps(component=proj.connection_object, population_access_index='i', data_prefix='d.')
            c = Template(c_analog_projection_tmpl).render(
                                        projection=proj,
                                        writer_stdc = self.writer_stdc,
                                        **std_variables
                                            )
            code_per_analogconnection_projection.append(c)





        code_per_pop = []

        for population in network.populations:


            component = population.component


            self.writer_stdc = CBasedFixedWriter(component=population.component, population_access_index='i', data_prefix='d.')
            self.writer_bluevec = CBasedFixedWriterBlueVecOps(component=population.component, population_access_index='i', data_prefix='d.')


            rv_per_neuron = []
            rv_per_population = []

            for rv in component.random_variable_nodes:

                assert rv.functionname == 'uniform'
                params = [ rv.parameters.get_single_obj_by(name='min'), rv.parameters.get_single_obj_by(name='max'), ]
                param_string = ','.join( "(%s)" % (self.writer_stdc.visit( p.rhs_ast)  ) for p in params )

                if rv.modes['share']=='PER_NEURON':
                    rv_per_neuron.append( (rv,param_string) )
                elif rv.modes['share']=='PER_POPULATION':
                    rv_per_population.append( (rv,param_string) )



            cfile = Template(c_population_details_tmpl).render(
                            population=population,

                            writer_stdc = self.writer_stdc,
                            writer_bluevec = self.writer_bluevec,

                            rv_per_neuron = rv_per_neuron,
                            rv_per_population = rv_per_population,

                            **std_variables
                            )


            code_per_pop.append(cfile)


        cout_data_writers = []
        for population in network.populations:
                cfile = Template(c_print_results_tmpl).render(population=population, **std_variables)
                cout_data_writers.append(cfile)

        c_prog_header = Template(c_prog_header_tmpl).render(
                          ** std_variables
                        )

        c_nios_plotting = ""
        if nios_options:
            c_nios_plotting = Template(c_nios_plotting_tmpl).render(
                            nios_options = nios_options,
                            ** std_variables
                            )

        c_main_loop = Template(c_main_loop_tmpl).render(
                        ** std_variables
                        )

        popl_objs = Template(popl_obj_tmpl).render(
                        ** std_variables
                        )




        #cfile = '\n'.join([c_prog_header] +  code_per_pop + code_per_analogconnection_projection +  [popl_objs] + code_per_electrical_projection +  code_per_eventport_projection  + cout_data_writers +[c_nios_plotting] + [c_main_loop])
        cfile = '\n'.join([c_prog_header] +  code_per_pop + code_per_analogconnection_projection +  [popl_objs] +  code_per_eventport_projection  + cout_data_writers +[c_nios_plotting] + [c_main_loop])

        for f in ['sim1.cpp','a.out',output_filename, 'debug.log',]:
            if os.path.exists(f):
                os.unlink(f)


        if not compile and output_c_filename:
            with open(output_c_filename,'w') as f:
                f.write(cfile)



        self.results = None
        if compile:
            self.compile_and_run(cfile, output_c_filename=output_c_filename, run=run, CPPFLAGS=CPPFLAGS,  output_exec_filename=output_exec_filename)
            self.results = hdfjive.HDF5SimulationResultFile(output_filename)





    def compile_and_run(self, cfile, output_c_filename, run, CPPFLAGS,  output_exec_filename):

        from neurounits.codegen.utils.c_compilation import CCompiler, CCompilationSettings



        # The executable:
        CCompiler.build_executable( src_text=cfile,
                                    compilation_settings = CCompilationSettings(
                                        additional_include_paths=[os.path.expanduser("~/hw/hdf-jive/include"), os.path.abspath('../../cpp/include/'), ],
                                        additional_library_paths=[os.path.expanduser("~/hw/hdf-jive/lib/"), os.path.expanduser("~/hw/BlueVec/lib/")],
                                        libraries = ['gmpxx', 'gmp','hdfjive','hdf5','hdf5_hl'],
                                        compile_flags=['-Wall  -Wfatal-errors -std=gnu++0x  -O2  -g -D_GLIBCXX_DEBUG ' + (CPPFLAGS if CPPFLAGS else '') ]
                                        ),
                                    run=run,
                                    output_filename=output_exec_filename or None,
                                    intermediate_filename = output_c_filename or None,
                                    )





