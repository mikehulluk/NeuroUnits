


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




        int get_upscale_for_xindex(int index)
        {

            const int n_bits_recip_ln_two = 12;
            const int recip_ln_two_as_int =  recip_ln_two * pow(2.0, n_bits_recip_ln_two) ;
            IntType P = (upscale+1-n_bits_recip_ln_two-nbits_table) * -1;
            assert(get_value(P)>0);
            int result_int = ((recip_ln_two_as_int *(index - table_size_half) )>>get_value(P)) + 1; // * pow(2.0, -P); 


            /*
            cout << "\nexp(x): " << exp(xvalue);
            cout << "\nR1: " << result_fp;
            cout << "\nR2: " << result_int;
            cout << "\n\n" << std::flush;
            */
            if(0)
            {
                // Calculate with floating point:
                double table_cell_width = pow(2.0, upscale +1) / pow(2.0, nbits_table);
                double xvalue = (index - table_size_half) * table_cell_width;
                double fp = recip_ln_two * xvalue;
                int result_fp = (int) ceil(fp);
                assert( abs(result_fp-result_int) <=1);
            }

            return result_int;








        }


        LookUpTableExpPower2(int nbits_table, int upscale)
             : nbits_table(nbits_table), upscale(upscale), table_size(1<<(nbits_table)), table_size_half(1<<(nbits_table-1))
        {

            // Calculate the output values:
            for(int i = 0; i < table_size; i++)
            {
                //int x_value_int = index_to_int(i);
                cout << "x_int" << i-table_size_half << "\n";
                double x_value_double = (double)( i - table_size_half) * pow(2.0, upscale) / table_size_half;

                double res = exp(x_value_double);

                cout << "func(" << x_value_double << ") -> " << res << "\n";


                // We use a variable fixed_point format to encde the result, because the ranges with exponentials
                // are simply too great (-8,8) -> (0.000335463, 1808.04)
                //
                // The optimal fixed point value upscaling to get our value in the range (-1,1) will be
                // fp = ln2( exp(x) )
                // which turns out to be linear in x (:
                // fp =~ 1.4426 * x
                // Careful with rounding:
                //double fp_upscale_dbl = recip_ln_two * x_value_double;

                int fp_upscale = get_upscale_for_xindex(i);

                //cout << "\n  ++ Upscalings (int):" << fp_upscale;
                //cout << "  -- fixed_point upscale: " << fp_upscale << "\n";

                int res_as_int = FixedFloatConversion::from_float(res, fp_upscale);


                //// Doube check we are not loosing too much precision here:
                //double res_as_float = FixedFloatConversion::to_float(res_as_int, fp_upscale);
                //cout << "  -- Load/Save: " << res_as_float << "\n";
                //cout << "  -- As int: " << res_as_int << "\n";


                // Save the value:
                pData.push_back( IntType(res_as_int));

                if(_x_vals.size() > 0) assert( _x_vals.back() < x_value_double);
                _x_vals.push_back(x_value_double);
            }

            assert( (int)pData.size() == table_size);
            assert( (int)_x_vals.size() == table_size);



        }














        IntType get(IntType x_in, IntType up_x_in, IntType up_out_in)
        {
            const bool DEBUG = false;

            if(DEBUG)
            {
                cout << "\n";
                cout << "\nget()";
                cout << "\ntable_size: " << table_size;
                cout << "\ntable_size_half: " << table_size_half;
            }

            IntType x = IntType(x_in);
            IntType up_x = IntType(up_x_in);
            IntType up_out = IntType(up_out_in);

            const IntType nbit_variables = IntType(NBIT_VARIABLES);




            // For debugging:
            const double dbg_x_as_float = FixedFloatConversion::to_float(x_in, up_x_in) ;

            if(DEBUG)
            {
            cout << "\nx: " << x;
            cout << "\ndbg_as_float: " << dbg_x_as_float;
            assert( fabs(dbg_x_as_float) < pow(2.0, this->upscale) );
            }


            // 1. Calculate the X-indices to use to lookup in the table with:
            IntType rshift = -(up_x - nbit_variables -upscale+nbits_table);
            IntType table_index = (x>>rshift) + table_size_half;

            if(DEBUG)
            {
                cout << "\nTable index: " << table_index;

                assert( _x_vals[get_value(table_index)] <= dbg_x_as_float);
                assert( _x_vals[get_value(table_index+1)] > dbg_x_as_float);
            }


            // 2. Lookup the yvalues, and also account for differences in fixed point format:
            IntType yn =  pData[get_value(table_index)];
            IntType yn1 = pData[get_value(table_index)+1];


            // 2a.Find the x-values at the each:
            IntType xn  = (((x>>rshift)+0) << rshift);
            IntType xn1 = (((x>>rshift)+1) << rshift);

            if(DEBUG)
            {
                double xn_dbl = FixedFloatConversion::to_float(get_value(xn), up_x_in) ;
                double xn1_dbl = FixedFloatConversion::to_float(get_value(xn1), up_x_in);

                cout << "\nxn_dbl: " << xn_dbl;
                cout << "\nxn1_dbl: " << xn1_dbl;

                assert( xn_dbl <= dbg_x_as_float);
                assert( xn1_dbl > dbg_x_as_float);
            }

            int L1 = get_upscale_for_xindex(get_value(table_index));
            int L2 = get_upscale_for_xindex(get_value(table_index+1));

            IntType yn_upscale =   IntType( L1 );
            IntType yn1_upscale =  IntType( L2 );








            if(DEBUG)
            {
            // Double Check:
            double xn_dbl_old = FixedFloatConversion::to_float(get_value(xn), up_x_in) ;
            double xn1_dbl_old = FixedFloatConversion::to_float(get_value(xn1), up_x_in);
            IntType yn_upscale_old =  IntType( (int) ceil( recip_ln_two * xn_dbl_old ) );
            IntType yn1_upscale_old = IntType( (int) ceil( recip_ln_two * xn1_dbl_old ) );

            if(DEBUG)
            {
                cout << "\nyn_upscale_old/ yn_upscale: " << yn_upscale_old << "/" << yn_upscale ;
                cout << "\nyn1_upscale_old/ yn1_upscale: " << yn1_upscale_old << "/" << yn1_upscale ;
                cout << std::flush;
            }
            //assert( yn_upscale_old == yn_upscale);
            //assert( yn1_upscale_old == yn1_upscale);
            }








            if(DEBUG)
            {
                double yn_dbl = FixedFloatConversion::to_float( get_value(yn), get_value(yn_upscale));
                double yn1_dbl = FixedFloatConversion::to_float( get_value(yn1), get_value(yn1_upscale));

                cout << "\nyn_dbl: " << yn_dbl;
                cout << "\nyn1_dbl: " << yn1_dbl;

                assert( yn_dbl <= exp(dbg_x_as_float) );
                assert( yn1_dbl > exp(dbg_x_as_float) );
            }


            // 3. Perform the linear interpolation:
            IntType yn_rel_upscale = IntType(yn1_upscale-yn_upscale);
            assert(yn_rel_upscale>=0);
            IntType yn_rescaled = (yn>>yn_rel_upscale);

            long xymul = (long)get_value(yn1 - yn_rescaled) *  get_value(x-xn);
            return //get_value(
                    auto_shift(yn, yn_upscale-up_out)
                    +
                    auto_shift64(xymul, get_value(  yn1_upscale - up_out-rshift ) )
                    //);

;



        }






        int get_correct(int x, int up_x, int up_out)
        {
            cout << "\nget()";


            double fp_xout = FixedFloatConversion::to_float(x,up_x) ;
            cout << "\nActual X: " << fp_xout;
            cout << "\nActual Out: " << exp(fp_xout);

            return FixedFloatConversion::from_float( exp(fp_xout), up_out) ;
        }








};







