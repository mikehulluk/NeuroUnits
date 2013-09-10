


#include <vector>
#include <iostream>
#include <assert.h>
#include <numeric>
#include <algorithm>
#include <cmath>

using namespace::std;

double my_fabs(double x) { return fabs(x); }

const double recip_ln_two = 1.44269504;





#include "float_utils.h"
using mh::auto_shift;
using mh::auto_shift64;


#include "safe_int.h"






double pow(double a, NativeInt64 b)
{
    return pow(a, (double)b);

}














template<int NBIT_VARIABLES, typename IntType>
class LookUpTableExpPower2
{


    typedef mh::FixedFloatConversion<NBIT_VARIABLES> FixedFloatConversion;

    vector<IntType> pData;
    vector<double> _x_vals;
    const IntType nbits_table;
    const IntType upscale;
    const int table_size;
    const int table_size_half;


public:




        NativeInt32 get_upscale_for_xindex(NativeInt32 index) const
        {

            const NativeInt32 n_bits_recip_ln_two = 12;
            const NativeInt32 recip_ln_two_as_int =  NativeInt32( ceil(recip_ln_two * pow(2.0, n_bits_recip_ln_two) ) );
            IntType P = (upscale+1-n_bits_recip_ln_two-nbits_table) * -1;
            assert(get_value32(P)>0);
            NativeInt32 result_int = ((recip_ln_two_as_int *(index - table_size_half) )>>get_value32(P)) + 1; // * pow(2.0, -P);

            #if DEBUG
                // Calculate with floating point:
                double table_cell_width = pow(2.0, upscale +1) / pow(2.0, nbits_table);
                double xvalue = (index - table_size_half) * table_cell_width;
                double fp = recip_ln_two * xvalue;
                NativeInt32 result_fp = (NativeInt32) ceil(fp);
                assert( abs(result_fp-result_int) <=1);
            #endif 

            return result_int;

        }


        LookUpTableExpPower2(int nbits_table, int upscale)
             : nbits_table(nbits_table), upscale(upscale), table_size(1<<(nbits_table)), table_size_half(1<<(nbits_table-1))
        {

            // Calculate the output values:
            for(NativeInt32 i = 0; i < table_size; i++)
            {
                //int x_value_int = index_to_int(i);
                cout << "x_int" << i-table_size_half << "\n";
                double x_value_double = (double)( i - table_size_half) * pow(2.0, upscale) / table_size_half;

                double res = exp(x_value_double);

                cout << "func(" << x_value_double << ") -> " << res << "\n";

                // We use a variable fixed_point format to encde the result, because the ranges with exponentials
                // are simply too great (-8,8) -> (0.000335463, 1808.04)
                NativeInt32 fp_upscale = get_upscale_for_xindex(i);
                NativeInt32 res_as_int = FixedFloatConversion::from_float(res, fp_upscale);

                // Save the value:
                cout << "\nres_as_int: " << res_as_int << "\n" << flush;
                pData.push_back( IntType(res_as_int));

                if(_x_vals.size() > 0) assert( _x_vals.back() < x_value_double);
                _x_vals.push_back(x_value_double);
            }

            assert( (NativeInt32)pData.size() == table_size);
            assert( (NativeInt32)_x_vals.size() == table_size);

        }














        IntType get(IntType x_in, IntType up_x_in, IntType up_out_in) const
        {

            #if DEBUG
            cout << "\n";
            cout << "\nget()";
            cout << "\ntable_size: " << table_size;
            cout << "\ntable_size_half: " << table_size_half;
            #endif

            IntType x = IntType(x_in);
            IntType up_x = IntType(up_x_in);
            IntType up_out = IntType(up_out_in);

            const IntType nbit_variables = IntType(NBIT_VARIABLES);




            // For debugging:
            #if DEBUG
            const double dbg_x_as_float = FixedFloatConversion::to_float(x_in, up_x_in) ;
            cout << "\nx: " << x;
            cout << "\ndbg_as_float: " << dbg_x_as_float;

            // Added an additional '-1', but not yet tested!
            assert( fabs(dbg_x_as_float) < pow(2.0, this->upscale-1) );
            #endif



            // 1. Calculate the X-indices to use to lookup in the table with:
            IntType rshift = -(up_x - nbit_variables -upscale+nbits_table);
            IntType table_index = (x>>rshift) + table_size_half;

            #if DEBUG
            cout << "\nTable index: " << table_index;
            assert( _x_vals[get_value32(table_index)] <= dbg_x_as_float);
            assert( _x_vals[get_value32(table_index+1)] > dbg_x_as_float);
            #endif


            // 2. Lookup the yvalues, and also account for differences in fixed point format:
            IntType yn =  pData[get_value32(table_index)];
            IntType yn1 = pData[get_value32(table_index)+1];


            // 2a.Find the x-values at the each:
            IntType xn  = (((x>>rshift)+0) << rshift);

            #if DEBUG
            IntType xn1 = (((x>>rshift)+1) << rshift);
            double xn_dbl = FixedFloatConversion::to_float(get_value32(xn), up_x_in) ;
            double xn1_dbl = FixedFloatConversion::to_float(get_value32(xn1), up_x_in);
            cout << "\nxn_dbl: " << xn_dbl;
            cout << "\nxn1_dbl: " << xn1_dbl;
            assert( xn_dbl <= dbg_x_as_float);
            assert( xn1_dbl > dbg_x_as_float);
            #endif

            NativeInt32 L1 = get_upscale_for_xindex(get_value32(table_index));
            NativeInt32 L2 = get_upscale_for_xindex(get_value32(table_index+1));

            IntType yn_upscale =   IntType( L1 );
            IntType yn1_upscale =  IntType( L2 );








            #if DEBUG
            // Double Check:
            double xn_dbl_old = FixedFloatConversion::to_float(get_value32(xn), up_x_in) ;
            double xn1_dbl_old = FixedFloatConversion::to_float(get_value32(xn1), up_x_in);
            IntType yn_upscale_old =  IntType( (NativeInt32) ceil( recip_ln_two * xn_dbl_old ) );
            IntType yn1_upscale_old = IntType( (NativeInt32) ceil( recip_ln_two * xn1_dbl_old ) );

            cout << "\nyn_upscale_old/ yn_upscale: " << yn_upscale_old << "/" << yn_upscale ;
            cout << "\nyn1_upscale_old/ yn1_upscale: " << yn1_upscale_old << "/" << yn1_upscale ;
            cout << std::flush;
            //assert( yn_upscale_old == yn_upscale);
            //assert( yn1_upscale_old == yn1_upscale);
            #endif








            #if DEBUG
            double yn_dbl = FixedFloatConversion::to_float( get_value32(yn), get_value32(yn_upscale));
            double yn1_dbl = FixedFloatConversion::to_float( get_value32(yn1), get_value32(yn1_upscale));

            cout << "\nyn_dbl: " << yn_dbl;
            cout << "\nyn1_dbl: " << yn1_dbl;

            assert( yn_dbl <= exp(dbg_x_as_float) );
            assert( yn1_dbl > exp(dbg_x_as_float) );

            assert(0); // Debugging disabled!?
            #endif





            // 3. Perform the linear interpolation:
            IntType yn_rel_upscale = IntType(yn1_upscale-yn_upscale);
            assert(yn_rel_upscale>=0);
            IntType yn_rescaled = (yn>>yn_rel_upscale);

            NativeInt64 xymul = get_value64(yn1 - yn_rescaled) *  get_value32(x-xn);
            return (
                    auto_shift(yn, yn_upscale-up_out)
                    +
                    auto_shift64(xymul, get_value32(  yn1_upscale - up_out-rshift ) )
                    );

;



        }






        //NativeInt32 get_correct(NativeInt32 x, NativeInt32 up_x, NativeInt32 up_out)
        //{
        //    cout << "\nget()";


        //    double fp_xout = FixedFloatConversion::to_float(x,up_x) ;
        //    cout << "\nActual X: " << fp_xout;
        //    cout << "\nActual Out: " << exp(fp_xout);

        //    return FixedFloatConversion::from_float( exp(fp_xout), up_out) ;
        //}








};







