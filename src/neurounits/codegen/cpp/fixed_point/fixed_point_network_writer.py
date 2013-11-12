


from mako.template import Template
import numpy as np
import os
from neurounits.ast_annotations.common import NodeFixedPointFormatAnnotator




c_prog_header_tmpl = r"""


/*
Two defines control the setup:
    ON_NIOS
    PC_DEBUG
*/







// By default, we run optimised on the PC:
#ifndef ON_NIOS
#define ON_NIOS false
#endif

#ifndef PC_DEBUG
#define PC_DEBUG false
#endif




#include "basic_types.h"



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
#define USE_BLUEVEC false
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
#include <array>
#include <string>
using namespace std;



## #include <BlueVecProxy.h>

// Headers to use when we are not on the NIOS:
#if ON_NIOS
#else
#include <boost/format.hpp>
#include <boost/assign/list_of.hpp>
#include <cinttypes>
#include <fenv.h>
#include <gmpxx.h>
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






#include "float_utils.h"
const int VAR_NBITS = ${nbits};
typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
using mh::auto_shift;
using mh::auto_shift64;










#if SAFEINT
#include "safe_int.h"
#include "safe_int_utils.h"
#endif


#include "safe_int_proxying.h"
#include "lut.h"









struct LookUpTables
{
    LookUpTables()
        : exponential(8, 4)    // (nbits, upscale)
        //: exponential(5, 3)    // (nbits, upscale)
    { }

    LookUpTableExpPower2<VAR_NBITS, IntType> exponential;
};

LookUpTables lookuptables;



















#include "/home/mh735/from_Matt/BlueVec.h"
typedef Stream DataStream;



















#ifdef USE_BLUEVEC
/*
namespace BVOps
{

    DataStream auto_shift(DataStream da, IntType amount)
    {
        if(amount==0)
        {
            return da;
        }
        else
        {
            if(amount>0) return da<<amount;
            else return da>>(-amount);
        }
    }

    DataStream auto_shift(DataStream da, DataStream amount)
    {
        return ifthenelse(amount==0, da, (ifthenelse(amount>0, da<<amount, da>>(-1 * amount)) ) );
    }

    // Add:
    inline DataStream do_add_op(DataStream v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        DataStream res = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local);
        return res;
    }
    inline DataStream do_add_op(IntType v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        DataStream res = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local);
        return res;
    }
    inline DataStream do_add_op(DataStream v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
        DataStream res = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local);
        return res;
    }

    // Sub:
    inline DataStream do_sub_op(DataStream v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local);
    }
    inline DataStream do_sub_op(IntType v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local);
    }
    inline DataStream do_sub_op(DataStream v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
        return auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local);
    }

    // Mul:
    inline DataStream do_mul_op(DataStream v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return multiply64_and_rshift(v1, v2, -(up1+up2-up_local-(VAR_NBITS-1)) );
    }
    inline DataStream do_mul_op(IntType v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return multiply64_and_rshift(v1, v2, -(up1+up2-up_local-(VAR_NBITS-1)) );
    }
    inline DataStream do_mul_op(DataStream v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
        return multiply64_and_rshift(v1, v2, -(up1+up2-up_local-(VAR_NBITS-1)) );
    }


    // Div:
    inline DataStream do_div_op(DataStream v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return divide64_and_rshift(v1, v2, -(up1-up2-up_local) );
    }
    inline DataStream do_div_op(IntType v1, IntType up1, DataStream v2, IntType up2, IntType up_local, IntType expr_id) {
        return divide64_and_rshift(v1, v2, -(up1-up2-up_local) );
    }
    inline DataStream do_div_op(DataStream v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id) {
        return divide64_and_rshift(v1, v2, -(up1-up2-up_local) );
    }

    inline DataStream do_ifthenelse_op(BoolStream pred, DataStream v1, IntType up1, DataStream v2, IntType up2) {
        return ifthenelse(pred, auto_shift(v1, up1), auto_shift(v2, up2));
    }
    inline DataStream do_ifthenelse_op(BoolStream pred, IntType v1, IntType up1, DataStream v2, IntType up2) {
        return ifthenelse(pred, auto_shift(v1, up1), auto_shift(v2, up2));
    }
    inline DataStream do_ifthenelse_op(BoolStream pred, DataStream v1, IntType up1, IntType v2, IntType up2) {
        return ifthenelse(pred, auto_shift(v1, up1), auto_shift(v2, up2));
    }

    // Exponential lookup on the BlueVec emulator:
    DataStream _get_upscale_for_xindex(DataStream index)
    {
        LookUpTableExpPower2<VAR_NBITS, IntType>& table = lookuptables.exponential;

        const NativeInt32 n_bits_recip_ln_two = 12;
        const NativeInt32 recip_ln_two_as_int =  NativeInt32( ceil(recip_ln_two * pow(2.0, n_bits_recip_ln_two) ) );
        const IntType P = (table.upscale+1-n_bits_recip_ln_two-table.nbits_table) * -1;
        DataStream result_int = ((recip_ln_two_as_int *(index - table.table_size_half) )>> P) + 1;

        return result_int;
    }

    template<typename LUTTYPE>
    inline DataStream int_exp(DataStream x, IntType up_x, IntType up_out, IntType expr_id, LUTTYPE lut ) {


        LookUpTableExpPower2<VAR_NBITS, IntType>& table = lookuptables.exponential;

        const IntType nbit_variables = IntType( VAR_NBITS );

        // 1. Calculate the X-indices to use to lookup in the table with:
        IntType rshift = -(up_x - nbit_variables -table.upscale+table.nbits_table);
        DataStream table_index = (x>>rshift) + table.table_size_half;

        // 2. Lookup the yvalues, and also account for differences in fixed point format:
        DataStream yn =   lookup_lut(lut, table_index) ;
        DataStream yn1 =  lookup_lut(lut, table_index+1) ;

        // 2a.Find the x-values at the each:
        DataStream xn  = (((x>>rshift)+0) << rshift);


        DataStream L1 = _get_upscale_for_xindex(table_index);
        DataStream L2 = _get_upscale_for_xindex(table_index+1);

        DataStream yn_upscale =   L1;
        DataStream yn1_upscale =  L2;


        // 3. Perform the linear interpolation:
        DataStream yn_rel_upscale = yn1_upscale-yn_upscale;
        DataStream yn_rescaled = (yn>>yn_rel_upscale);


        DataStream d1 = auto_shift(yn, yn_upscale-up_out);
        DataStream d2 = multiply64_and_rshift( (yn1-yn_rescaled), (x-xn), (yn1_upscale - up_out-rshift) * -1 );

        return (d1 + d2);
    }



}
*/
#endif




#include "fixed_point_operations.h"








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
            return FixedFloatConversion::to_float(v, UP);
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
            IntType res = tmpl_fp_ops::do_add_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> sub( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = tmpl_fp_ops::do_sub_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> mul( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = tmpl_fp_ops::do_mul_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1, int U2>
        static inline ScalarType<UOUT> div( const ScalarType<U1>& a, const ScalarType<U2>& b)
        {
            IntType res = tmpl_fp_ops::do_div_op(a.v, U1, b.v, U2, UOUT, -1);
            return ScalarType<UOUT> (res);
        }

        template<int U1>
        static inline ScalarType<UOUT> exp( const ScalarType<U1>& a)
        {
            return ScalarType<UOUT> ( tmpl_fp_ops::int_exp( a.v, U1, UOUT, -1, lookuptables.exponential ) );
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
        explicit ScalarType(int v) : v_float(FixedFloatConversion::to_float(v, UPSCALE)) { }
        explicit ScalarType(long unsigned int v) : v_float(FixedFloatConversion::to_float(v, UPSCALE)) { }
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
            return (FixedFloatConversion::from_float(v_float,UPSCALE) );
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
        DATATYPE _data[SIZE];

        // Default Constructor - initialise everything to zero
        DataVector()
        {
            for(int i=0;i<SIZE;i++) _data[i] = DATATYPE(0);
        }

        DataVector( int t )
        {
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













struct BoolDataStream
{
    Stream s;
    BoolDataStream(Stream s) : s(s) {}
};




BoolDataStream operator||( const BoolDataStream& lhs, const BoolDataStream& rhs ) { return BoolDataStream( lhs.s || rhs.s ); }
BoolDataStream operator&&( const BoolDataStream& lhs, const BoolDataStream& rhs ) { return BoolDataStream( lhs.s && rhs.s ); }









// New fixed point classes:
template<int UPSCALE>
struct FixedPointDataStream
{
    Stream s;
    explicit FixedPointDataStream(Stream s) : s(s) { }
    explicit FixedPointDataStream(int k) : s(constant(k))  {}

    // From data pointer:
    explicit FixedPointDataStream(int* pData) : s(load(pData)) {}
    //FixedPointDataStream() {};

    const static int UP = UPSCALE;

    // Automatic rescaling during assignments:
    template<int OTHER_UP>
    FixedPointDataStream<UPSCALE>& operator=(const FixedPointDataStream<OTHER_UP>& rhs)
    {
        s = rhs.rescale_to<UPSCALE>().s;
        return *this;
    }



    // Explicit rescaling between different scaling factors:
    template<int NEW_UPSCALE>
    FixedPointDataStream<NEW_UPSCALE> rescale_to( ) const
    {
        if(UPSCALE==NEW_UPSCALE) {
            return FixedPointDataStream<NEW_UPSCALE>(s);
        } else if(UPSCALE>NEW_UPSCALE){
            return FixedPointDataStream<NEW_UPSCALE>( s << (UPSCALE-NEW_UPSCALE) );
        } else{
            return FixedPointDataStream<NEW_UPSCALE>( s >> (NEW_UPSCALE-UPSCALE) );
        }

        // WAS:
        //return FixedPointDataStream<NEW_UPSCALE>( auto_shift(s, UPSCALE - NEW_UPSCALE) );
    }


    bool operator<=( const FixedPointDataStream<UPSCALE>& rhs) const
    {
        return s <=rhs.s;
    }


    template<int RHS_UPSCALE>
    inline BoolDataStream operator<( const FixedPointDataStream<RHS_UPSCALE>& rhs) const
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
struct FixedPointDataStreamOp
{
    static const int UOUT = UOUT_;

    template<int U1, int U2>
    static inline FixedPointDataStream<UOUT> add( const FixedPointDataStream<U1>& a, const FixedPointDataStream<U2>& b)
    {
        return FixedPointDataStream<UOUT> (a.template rescale_to<UOUT>().s + b.template rescale_to<UOUT>().s);
    }

    template<int U1, int U2>
    static inline FixedPointDataStream<UOUT> sub( const FixedPointDataStream<U1>& a, const FixedPointDataStream<U2>& b)
    {
        return FixedPointDataStream<UOUT> (a.template rescale_to<UOUT>().s - b.template rescale_to<UOUT>().s);
    }

    template<int U1, int U2>
    static inline FixedPointDataStream<UOUT> mul( const FixedPointDataStream<U1>& a, const FixedPointDataStream<U2>& b)
    {
        return FixedPointDataStream<UOUT> (a.template rescale_to<UOUT>().s * b.template rescale_to<UOUT>().s);
    }

    template<int U1, int U2>
    static inline FixedPointDataStream<UOUT> div( const FixedPointDataStream<U1>& a, const FixedPointDataStream<U2>& b)
    {
        return FixedPointDataStream<UOUT> (a.template rescale_to<UOUT>().s / b.template rescale_to<UOUT>().s);
    }

    template<int U1>
    static inline FixedPointDataStream<UOUT> exp( const FixedPointDataStream<U1>& a)
    {
        cout << "MISSING EXP FUNCTION";
        return FixedPointDataStream<UOUT>(0);
        //return FixedPointDataStream<UOUT> ( BVOps::int_exp( a.v, U1, UOUT, -1, lookuptables.exponential ) );
    }


    template<int U1, int U2>
    static inline FixedPointDataStream<UOUT> ifthenelse( const BoolDataStream& p, const FixedPointDataStream<U1>& a, const FixedPointDataStream<U2>& b)
    {
        setCond(p.s);
        return FixedPointDataStream<UOUT>( cond(a.template rescale_to<UOUT>().s,b .template rescale_to<UOUT>().s) );
    }


    template<int U1>
    static inline FixedPointDataStream<UOUT> mul( const FixedPointDataStream<U1>& a, Arg b)
    {
        return FixedPointDataStream<UOUT> (a.template rescale_to<UOUT>().s * b);
    }


};






































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
                FixedFloatConversion::from_float(
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
    double value_float = FixedFloatConversion::to_float(val, upscale);

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







Kernel sim_step_update_sv_bluevec_build_kernel(NrnPopData& d)
{
        Arg t;
        Stream _bv_t = load(t);
        FixedPointDataStream<${time_upscale}> bv_t(_bv_t);

        // A. Load in all the data (state-variables, supplied_values, random_nodes, ar-nodes):
        % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        FixedPointDataStream<${td.lhs.annotations['fixed-point-format'].upscale}> bv_${td.lhs.symbol}( &(d.${td.lhs.symbol}[0].v) );
        %endfor

        % for suppl in population.component.suppliedvalues:
        FixedPointDataStream<${suppl.annotations['fixed-point-format'].upscale}> bv_${suppl.symbol}( &(d.${suppl.symbol}[0]).v );
        %endfor

        // Random Variable nodes
        %for rv, _pstring in rv_per_population:
        IntType RV${rv.annotations['node-id']} =  d.RV${rv.annotations['node-id']};
        %endfor
        %for rv, _pstring in rv_per_neuron:
        FixedPointDataStream <${rv.annotations['fixed-point-format'].upscale}> bv_RV${rv.annotations['node-id']}( &(d.RV${rv.annotations['node-id']}[0].v) );
        %endfor

        // AutoRegressive nodes:
        %for ar in population.component.autoregressive_model_nodes:
        <% ar_node_name = "AR%s" % ar.annotations['node-id'] %>
        <% ar_upscale = ar.annotations['fixed-point-format'].upscale %>
        FixedPointDataStream<${ar_upscale}> bv_${ar_node_name}( &(d.${ar_node_name}[0].v));
        %for i in range( len( ar.coefficients)):
        FixedPointDataStream<${ar_upscale}> bv__${ar_node_name}_t${i}( &(d._${ar_node_name}_t${i}[0].v));
        %endfor
        %endfor

        //FixedPointDataStream<${population.component.time_node.annotations['fixed-point-format'].upscale}> bv_t( time_info.time_fixed.v );

        // B.Load the exponential table:
        //assert(0); // WTF!
        //LUT bv_explut = load_lut( &(lookuptables.exponential.pData[0]), lookuptables.exponential.table_size);
        int bv_explut;







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
        bv_print("\nCalculating assignment: ${ass.lhs.symbol}");
        FixedPointDataStream<${ass.lhs.annotations['fixed-point-format'].upscale}> bv_${ass.lhs.symbol} = ${writer_bluevec.to_c(ass, population_access_index=None, data_prefix='bv_')};
        bv_print("Finished calculating assignment: ${ass.lhs.symbol}");
        % endfor


        // Calculate delta's for all state-variables:
        %for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        FixedPointDataStream<${td.lhs.annotations['fixed-point-format'].delta_upscale}> bv_d_${td.lhs.symbol} = ${writer_bluevec.to_c(td.rhs_map ) }.rescale_to<${td.lhs.annotations['fixed-point-format'].delta_upscale}>()  ;
        bv_${td.lhs.symbol} = FixedPointDataStreamOp<${td.lhs.annotations['fixed-point-format'].upscale}>::add( bv_${td.lhs.symbol}, bv_d_${td.lhs.symbol});
        % endfor





        ##// Crossing Nodes:
        ##%for cc in population.component.conditioncrosses_nodes:
        ##// Copy the old value accross:
        ##d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs_prev[i] = d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i];
        ##// Calculate the next value:
        ##d.C_${cc.annotations['node-id']}_lhs_is_gt_rhs[i] = ${writer_stdc._VisitOnConditionCrossing(cc)};

        ##%endfor


        // Write back:
        // We need to copy all state-variables, plus anything that might be recorded:
        % for td in sorted(population.component.timederivatives, key=lambda td:td.lhs.symbol):
        store(bv_${td.lhs.symbol}.s, &(d.${td.lhs.symbol}[0].v));
        %endfor





        cout << "\nBuilding Kernel";
        //Kernel k;
        return kernel();


}


void sim_step_update_sv_bluevec(NrnPopData& d, TimeInfo time_info)
{
        // Only build kernel once:
        static Kernel k  = sim_step_update_sv_bluevec_build_kernel(d);

        // And run:
        cout << "\nInvoking Kernel";
        call(128, k, time_info.time_fixed.rescale_to<${time_upscale}>().v );
        cout << "\nInvoke done!";








    LOG_COMPONENT_STATEUPDATE( cout << "\n"; )
}















void sim_step_update_sv(NrnPopData& d, TimeInfo time_info)
{
    // Sequential Solving:
    //sim_step_update_sv_sequential(d, time_info);
    sim_step_update_sv_bluevec(d, time_info);

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









c_main_loop_tmpl = r"""

#include <signal.h>
#include <ctime>




void my_terminate (int parameter)
{
    cout << "\n\nIN MY SIGNAL HANDLER\n" << flush;

    // Dump to HDF5
    cout << "\nWriting HDF5 output" << std::flush;

    {
        SimulationResultsPtr hdf_output = SimulationResultsFile(output_filename).Simulation(simulation_name);
        global_data.recordings_new.write_all_traces_to_hdf(hdf_output);
        global_data.recordings_new.write_all_output_events_to_hdf(hdf_output);
    }

    cout << "\n\nERROR!!!\n\n";
    exit(0);

}




int main()
{

    // Start the clock:
    clock_t begin_main = clock();

    // Setup the random number generator:
    rnd::seed_rand_kiss(1);


    // Lets handle signals:
    signal (SIGTERM,my_terminate);
    signal (SIGABRT,my_terminate);




    // Enable floating point exception trapping:
    #if !ON_NIOS
    //feenableexcept(FE_DIVBYZERO | FE_UNDERFLOW | FE_OVERFLOW | FE_INVALID);
    feenableexcept(FE_DIVBYZERO |  FE_OVERFLOW | FE_INVALID);
    #endif //!ON_NIOS


    // Setup the variables:
    %for pop in network.populations:
    NS_${pop.name}::initialise_statevars(data_${pop.name});
    NS_${pop.name}::initialise_randomvariables(data_${pop.name});
    NS_${pop.name}::initialise_autoregressivenodes(data_${pop.name} );
    %endfor

    // Setup the electical coupling:
    %for proj in network.electrical_synapse_projections:
    NS_${proj.name}::setup_electrical_coupling();
    %endfor

    // Setup the event connections:
    %for evt_conn in network.event_port_connectors:
    NS_eventcoupling_${evt_conn.name}::setup_connections();
    %endfor






    clock_t begin_sim = clock();


    #if NSIM_REPS
    for(int k=0;k<NSIM_REPS;k++)
    {
        if(k%100==0) cout << "Loop: " << k << "\n" << flush;
    #endif

        global_data.recordings_new.n_results_written=0;
        for(IntType step_count=IntType(0);step_count<GlobalConstants::nsim_steps;step_count++)
        {


            TimeInfo time_info(step_count);


            DBG.update( time_info.time_fixed.to_float() );

            #if DISPLAY_LOOP_INFO
            if(get_value32(step_count)%10000 == 0)
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



            // A. Electrical coupling:
            %for proj in network.electrical_synapse_projections:
            NS_${proj.name}::calculate_electrical_coupling( data_${proj.src_population.population.name}, data_${proj.dst_population.population.name} );
            %endfor



            // B. Integrate all the state_variables of all the neurons:
            %for pop in network.populations:
            NS_${pop.name}::sim_step_update_sv( data_${pop.name}, time_info);
            %endfor

            // C. Resolve state transitions:
            %for pop in network.populations:
            NS_${pop.name}::sim_step_update_rt( data_${pop.name}, time_info);
            %endfor




            // C. Save the recorded values:
            if(get_value32(time_info.step_count) % get_value32(record_rate)==0)
            {
                // Save time:
                global_data.recordings_new.time_buffer[global_data.recordings_new.n_results_written] = time_info.time_fixed.to_int();
                //write_time_to_hdf5(time_info);
                %for poprec in network.all_trace_recordings:
                // Record: ${poprec}
                for(int i=0;i<${poprec.size};i++) global_data.recordings_new.data_buffers[${poprec.global_offset}+i][global_data.recordings_new.n_results_written] = data_${poprec.src_population.name}.${poprec.node.symbol}[i + ${poprec.src_pop_start_index} ].to_int();
                %endfor

                global_data.recordings_new.n_results_written++;
            }


        }

    #if NSIM_REPS
    }
    #endif


    clock_t end_sim = clock();


    // Dump to HDF5
    cout << "\nWriting HDF5 output" << std::flush;
    SimulationResultsPtr hdf_output = SimulationResultsFile(output_filename).Simulation(simulation_name);

    global_data.recordings_new.write_all_traces_to_hdf(hdf_output);
    global_data.recordings_new.write_all_output_events_to_hdf(hdf_output);
    global_data.recordings_new.write_all_input_events_to_hdf(hdf_output);


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




"""









c_electrical_projection_tmpl = r"""

// Electrical Coupling

namespace NS_${projection.name}
{


    struct GapJunction
    {
        IntType i,j;
        //IntType strength_S;

        ScalarType<${projection.strength_S_upscale}>  strength_S_fixed;

        GapJunction(IntType i, IntType j, IntType strength)
         : i(i), j(j), strength_S_fixed(strength)
        {


        }

    };



    typedef std::vector<GapJunction>  GJList;
    GJList gap_junctions;


    void setup_electrical_coupling()
    {

        const IntType strength_S_int =  ${projection.strength_S_int};

        ${projection.connector.build_c( src_pop_size_expr=projection.src_population.get_size(),
                                        dst_pop_size_expr=projection.dst_population.get_size(),
                                        add_connection_functor=lambda i,j: "gap_junctions.push_back( GapJunction(IntType(%s), IntType(%s), strength_S_int) );" % (i,j) ,
                                        add_connection_set_functor=None
                                        ) }
    }

    void calculate_electrical_coupling( NS_${projection.src_population.population.name}::NrnPopData& src, NS_${projection.dst_population.population.name}::NrnPopData& dst)
    {
        <%
        pre_V_node = projection.src_population.component.get_terminal_obj_or_port('V')
        post_V_node = projection.dst_population.component.get_terminal_obj_or_port('V')
        pre_iinj_node = projection.src_population.component.get_terminal_obj_or_port(projection.injected_port_name)
        post_iinj_node = projection.dst_population.component.get_terminal_obj_or_port(projection.injected_port_name)
        v_upscale = max( [pre_V_node.annotations['fixed-point-format'].upscale, post_V_node.annotations['fixed-point-format'].upscale] )
        curr_upscale = max( [pre_iinj_node.annotations['fixed-point-format'].upscale, post_iinj_node.annotations['fixed-point-format'].upscale] )
        %>

        for(GJList::iterator it = gap_junctions.begin(); it != gap_junctions.end();it++)
        {
            ScalarType<${curr_upscale}> curr = ScalarOp<${curr_upscale}>::mul(
                    ScalarOp<${v_upscale}>::sub( src.V[get_value32(it->i)], dst.V[get_value32(it->j)] ),
                    it->strength_S_fixed
                );

            src.${pre_iinj_node.symbol}[get_value32(it->i)]  = ScalarOp<${pre_iinj_node.annotations['fixed-point-format'].upscale}>::sub (src.${pre_iinj_node.symbol}[get_value32(it->i)], curr);
            src.${post_iinj_node.symbol}[get_value32(it->j)] = ScalarOp<${post_iinj_node.annotations['fixed-point-format'].upscale}>::add (src.${post_iinj_node.symbol}[get_value32(it->j)], curr);

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


        string output = "";

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

            output += boost::lexical_cast<string>(tgt_nrn_index) + ",";
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
    typedef std::array<IntType, buffer_size>  RecordingBuffer;
    // Allocate the storage for the traces:
    RecordingBuffer time_buffer;
    std::array<RecordingBuffer, n_rec_buffers> data_buffers;
    int n_results_written;



    // Events:
    typedef  list<SpikeEmission> SpikeList;
    int nspikes_emitted;
    std::array<SpikeList,  ${network.n_output_event_recording_buffers} >  spikerecordbuffers_send;

    int nspikes_recv;
    std::array<SpikeList, ${network.n_input_event_recording_buffers}> spikerecordbuffers_recv;



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







    void write_all_traces_to_hdf(SimulationResultsPtr output)
    {
        #if USE_HDF

        cout << "\n\nWriting traces to HDF5";
        T_hdf5_type_float dt_float = FixedFloatConversion::to_float(1, time_upscale);

        // New version:
        SharedTimeBufferPtr times = output->write_shared_time_buffer(n_results_written, &time_buffer[0]);
        times->get_dataset()->set_scaling_factor(dt_float);

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
        }
        %endfor

        cout << "\n\nFinished Writing to HDF5";
        #endif //USE_HDF
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
        T_hdf5_type_float dt_float = FixedFloatConversion::to_float(1, time_upscale);
        %for i,poprec in enumerate(network.all_output_event_recordings):
        for(int i=0; i< ${poprec.size};i++)
        {
            int buffer_offset = ${poprec.global_offset}+i;
            int neuron_index = i + ${poprec.src_pop_start_index};
            TagList tags = boost::assign::list_of( "${','.join(poprec.tags)}");
            EventDataSetTuple evtdata = output->write_outputevents_byobjects_extractor<SpikeEmissionExtractor>("${poprec.src_population.name}", neuron_index, "${poprec.node.symbol}",  spikerecordbuffers_send[buffer_offset].begin(), spikerecordbuffers_send[buffer_offset].end(), tags );
            evtdata.spiketimes->set_scaling_factor(dt_float);
        }
        %endfor
    }

    void write_all_input_events_to_hdf(SimulationResultsPtr output)
    {
        T_hdf5_type_float dt_float = FixedFloatConversion::to_float(1, time_upscale);
        %for i,poprec in enumerate(network.all_input_event_recordings):
        for(int i=0; i< ${poprec.size};i++)
        {
            int buffer_offset = ${poprec.global_offset}+i;
            int neuron_index = i + ${poprec.src_pop_start_index};
            TagList tags = boost::assign::list_of( "${','.join(poprec.tags)}");
            EventDataSetTuple evtdata = output->write_inputevents_byobjects_extractor<SpikeEmissionExtractor>("${poprec.src_population.name}", neuron_index, "${poprec.node.symbol}",  spikerecordbuffers_recv[buffer_offset].begin(), spikerecordbuffers_recv[buffer_offset].end(), tags );
            evtdata.spiketimes->set_scaling_factor(dt_float);
        }
        %endfor
    }



































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








#include "/home/mh735/from_Matt/BlueVec.cpp"


"""



from fixed_point_common import  CBasedFixedWriter, CBasedFixedWriterBlueVecOps

import hdfjive




















class CBasedEqnWriterFixedNetwork(object):
    def __init__(self, network, output_filename=None, output_c_filename=None, run=True, compile=True, CPPFLAGS=None, output_exec_filename=None, step_size=0.01, run_until=1.0, as_float=False):

        network.finalise()


        if output_filename is None:
            output_filename = 'neuronits.results.hdf'


        self.dt_float = step_size
        self.dt_upscale = int(np.ceil(np.log2(self.dt_float)))


        # Check all the components use the same floating point formats:
        # NBITS:
        nbits = set([ pop.component.annotation_mgr._annotators['fixed-point-format-ann'].nbits for pop in network.populations])
        assert len(nbits) == 1
        self.nbits = list(nbits)[0]

        #ENCODING OF TIME:
        time_upscale = set([pop.component._time_node.annotations['fixed-point-format'].upscale for pop in network.populations])
        print time_upscale
        assert len(time_upscale) == 1
        self.time_upscale = list(time_upscale)[0]


        self.dt_int = NodeFixedPointFormatAnnotator.encode_value_cls(self.dt_float, self.dt_upscale, self.nbits )


        #print
        #print ' ------ DT -------'
        #print 'dt_float', self.dt_float
        #print 'dt_int', self.dt_int
        #print 'dt_upscale', self.dt_upscale
        #print 'nbits', self.nbits
        #print
        #assert False


        # Make sure the events can be connected:
        evt_src_to_evtportconns = {}
        for evt_conn in network.event_port_connectors:
            key = (evt_conn.src_population, evt_conn.src_port)
            if not key in evt_src_to_evtportconns:
                evt_src_to_evtportconns[key] = []
            evt_src_to_evtportconns[key].append(evt_conn)


        t_stop = run_until
        n_steps = t_stop / self.dt_float
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



        code_per_electrical_projection = []

        for proj in network.electrical_synapse_projections:
            c = Template(c_electrical_projection_tmpl).render(
                                        projection=proj,
                                        **std_variables
                                            )
            code_per_electrical_projection.append(c)



        code_per_eventport_projection = []
        for proj in network.event_port_connectors:
            c = Template(c_event_projection_tmpl).render(
                                        projection=proj,
                                        **std_variables
                                            )
            code_per_eventport_projection.append(c)






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

        c_main_loop = Template(c_main_loop_tmpl).render(
                        ** std_variables
                        )

        popl_objs = Template(popl_obj_tmpl).render(
                        ** std_variables
                        )




        cfile = '\n'.join([c_prog_header] +  code_per_pop +  [popl_objs] + code_per_electrical_projection +  code_per_eventport_projection + cout_data_writers + [c_main_loop])

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
                                        additional_include_paths=[os.path.expanduser("~/hw/hdf-jive/include"), os.path.abspath('../../cpp/include/'), os.path.expanduser("~/hw/BlueVec/include/") ],
                                        additional_library_paths=[os.path.expanduser("~/hw/hdf-jive/lib/"), os.path.expanduser("~/hw/BlueVec/lib/")],
                                        libraries = ['gmpxx', 'gmp','hdfjive','hdf5','hdf5_hl', 'bv_proxy'],
                                        compile_flags=['-Wall  -Wfatal-errors -std=gnu++0x  -O2  -g -D_GLIBCXX_DEBUG ' + (CPPFLAGS if CPPFLAGS else '') ]
                                        ),
                                    run=run,
                                    output_filename=output_exec_filename or None,
                                    intermediate_filename = output_c_filename or None,
                                    )





