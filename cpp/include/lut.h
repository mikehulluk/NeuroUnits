


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



typedef int IntType;





template<int NBIT_VARIABLES>
class LookUpTableExpPower2
{


	typedef mh::FixedFloatConversion<NBIT_VARIABLES> FixedFloatConversion;

    vector<int> pData;
    vector<double> _x_vals;
    size_t nbits_table;
    size_t upscale;
    const size_t table_size;
    const size_t table_size_half;


public:




        LookUpTableExpPower2(size_t nbits_table, int upscale)
             : nbits_table(nbits_table), upscale(upscale), table_size(1<<(nbits_table)), table_size_half(1<<(nbits_table-1))


        {



            //double upscale_factor_in =  pow(2.0, upscale);

            // Calculate the output values:
            for(int i = 0; i < (int) table_size; i++)
            {
                //int x_value_int = index_to_int(i);
                cout << "x_int" << i-(int)table_size_half << "\n";
                double x_value_double = (double)( i - (int) table_size_half) * pow(2.0, upscale) / table_size_half;

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
                double fp_upscale_dbl = recip_ln_two * x_value_double;
                
                int fp_upscale =  (int) ceil( fp_upscale_dbl );
                
                
                cout << "\n  ++ Upscalings (dbl):" << fp_upscale_dbl;
                cout << "\n  ++ Upscalings (int):" << fp_upscale;
                
                cout << "  -- fixed_point upscale: " << fp_upscale << "\n";

                int res_as_int = FixedFloatConversion::from_float(res, fp_upscale);


                // Doube check we are not loosing too much precision here:
                double res_as_float = FixedFloatConversion::to_float(res_as_int, fp_upscale);
                cout << "  -- Load/Save: " << res_as_float << "\n";
                cout << "  -- As int: " << res_as_int << "\n";


                // Save the value:
               pData.push_back(res_as_int);

               if(_x_vals.size() > 0) assert( _x_vals.back() < x_value_double);
               _x_vals.push_back(x_value_double);
            }

            assert(pData.size() == table_size);
            assert(_x_vals.size() == table_size);



        }
        
        
        
        
        
        int get2(int x, int up_x, int up_out)
        {
            cout << "\nget()";


            double fp_xout = FixedFloatConversion::to_float(x,up_x) ;
            cout << "\nActual X: " << fp_xout;
            cout << "\nActual Out: " << exp(fp_xout);
            
            return FixedFloatConversion::from_float( exp(fp_xout), up_out) ;
		}
        
        

        int get(int x, int up_x, int up_out)
        {
            cout << "\nget()";


            double fp_xout = FixedFloatConversion::to_float(x,up_x) ;
            cout << "\nActual X: " << fp_xout;
            cout << "\nActual Out: " << exp(fp_xout);



            // 1. Convert the x to an index
            /*
            size_t index_0 = 0;
            while( _x_vals[index_0+1] < fp_xout  && index_0+1 < _x_vals.size() )
            {
                index_0++;
            }
            assert( fp_xout > _x_vals[index_0] &&  fp_xout <= _x_vals[index_0+1] );
            cout << "\n -- index_0: " << index_0;
            */

            int right_shift1 = NBIT_VARIABLES - up_x - 2;
            int index_0_signed = (x>>right_shift1) + table_size_half;
            size_t index_0 = index_0_signed;

            if(0)
            {
                // Float check:
                double orig_x_neg_1_to_1 = FixedFloatConversion::to_float(x, up_x) / table_size_half;
                double orig_index_0_fl = (( orig_x_neg_1_to_1 + 0.5 ) * table_size );
                size_t orig_index_0 = (int)  orig_index_0_fl;
                assert(index_0 == orig_index_0);
            }
            cout << "\n -->> index_0 (int): " << index_0;


            // 2. Look up yn and y+1, possibily need to scale
            //float xn = _x_vals[index_0];
            //float xn1 = _x_vals[index_0+1];


             // : nbits_table(nbits_table), upscale(upscale), table_size(1<<(nbits_table)), table_size_half(1<<(nbits_table-1))

            int upscale_int = upscale;
            int nbits_table_int = nbits_table;
            //double xn =  (double)( (int)index_0 - (int) table_size_half) * pow(2.0, upscale_int) / table_size_half;
            //double xn1 = (double)( (int)(index_0+1) - (int) table_size_half) * pow(2.0, upscale_int) / table_size_half;
            //#double xn =  (double)( (int)index_0 - (int) table_size_half) * pow(2.0, upscale_int- (nbits_table_int-1)) ; /// table_size_half;
            //double xn1 = (double)( (int)(index_0+1) - (int) table_size_half) * pow(2.0, upscale_int- (nbits_table_int-1)); // / table_size_half;


            // Calculate the scaling powers:
            //double xn_new =  (double)( (int)index_0 - (int) table_size_half) * pow(2.0, upscale_int- (nbits_table_int-1)) ;
            //double xn1_new =  xn_new + pow(2.0, upscale_int- (nbits_table_int-1)) ;

            //double xn_new =  (double)( (int)index_0 * pow(2.0, upscale_int- (nbits_table_int-1)) ) - (int) table_size_half * pow(2.0, upscale_int- (nbits_table_int-1)) ;
            // It makes sense to encode our estimates for xn, xn1 in the upscale of the table:

            int right_shift = nbits_table_int - upscale_int -1 ;
            assert(right_shift > 0);

            //// Lets upscale so that we keep as much precision as possible:
            //int manual_upscale = -right_shift + (NBIT_VARIABLES-1 - nbits_table) ;
            ////double xn_new =  (double)( (int)index_0 * pow(2.0, -right_shift) ) - pow(2.0, upscale_int) ;
            //double xn_new =  (double)( (int)index_0 * pow(2.0, -right_shift+manual_upscale) ) - pow(2.0, upscale_int+manual_upscale) ;
            //double xn1_new =  xn_new + pow(2.0, upscale_int- (nbits_table_int-1) + manual_upscale) ;



            // Lets upscale so that we keep as much precision as possible:
            int manual_upscale = -right_shift + (NBIT_VARIABLES-1 - nbits_table) ;
            assert(-right_shift+manual_upscale > 0);


            //int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - pow(2.0, upscale_int+manual_upscale) ;
            //int xn1_new =  xn_new + pow(2.0, upscale_int- (nbits_table_int-1) + manual_upscale) ;
            int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - (1<<(upscale_int+manual_upscale) );
            int xn1_new =  xn_new + (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;





            cout << "\n =====>> xn_new: " << xn_new;


            // How do we represent ln(2) as an integer?
            int recip_ln_two_nbits = 10; //4096 ~ (5dp??)
            int recip_ln_two_int = recip_ln_two * (1<<recip_ln_two_nbits);

            //int fp_upscale_n = int( recip_ln_two  *  xn_new * pow(2.0, -manual_upscale) );
            //int fp_upscale_n1 = int( recip_ln_two *  xn1_new * pow(2.0, -manual_upscale) );

            // TODO: Check here - are we getting close to integer overflow??
            int fp_upscale_n =  ceil( recip_ln_two_int *  xn_new *  pow(2.0, -(manual_upscale+recip_ln_two_nbits)) );
            int fp_upscale_n1 = ceil( recip_ln_two_int *  xn1_new * pow(2.0, -(manual_upscale+recip_ln_two_nbits)) );

            //int fp_upscale_n =  auto_shift(recip_ln_two_int *  xn_new, -(manual_upscale+recip_ln_two_nbits)) ;
            //int fp_upscale_n1 = auto_shift(recip_ln_two_int *  xn1_new,  -(manual_upscale+recip_ln_two_nbits)) ;


            int yn = pData[index_0];
            int yn1 = pData[index_0+1] ;




            cout << "\n -- y_n int: " << yn;
            cout << "\n -- y_n1 int: " << yn1;
            cout << "\n -- y_n Scaling int: " << fp_upscale_n;
            cout << "\n -- y_n1 Scaling int: " << fp_upscale_n1;



            // Its possible that the two y values have different fixed point representations, so we should use the larger power,
            // which will be the one for yn+1.
            int working_upscale = fp_upscale_n1;


            // prop_to_next will be between zero and one in float, to lets map that to integers
            //float prop_to_next = ( (to_float(x,up_x) - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) ;


            //double res =  ( double(x) * pow(2.0, up_x) / double(range_max) )

            int prop_to_next = ( (( double(x) * pow(2.0, up_x) / double(FixedFloatConversion::cl_range_max) )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * FixedFloatConversion::cl_range_max ;

            //float yn_fl = to_float(yn, fp_upscale_n);
            //float yn1_fl = to_float(yn1, fp_upscale_n1);


            //( double(yn) * pow(2.0, fp_upscale_n) / double(range_max) )
            //( double(yn1) * pow(2.0, fp_upscale_n1) / double(range_max) )
            //
            double dbl_range_max = FixedFloatConversion::cl_range_max;
            //float y_out = ( double(yn) * pow(2.0, fp_upscale_n) / dbl_range_max )
            //              +
            //              ( ((  ( double(yn1) * pow(2.0, fp_upscale_n1) / double(range_max) ) - ( double(yn) * pow(2.0, fp_upscale_n) / double(range_max) ) ) * prop_to_next) / range_max);
            //double y_out = ( double(yn) * pow(2.0, fp_upscale_n)  ) + ( (double) ((  ( double(yn1) * pow(2.0, fp_upscale_n1)) - ( double(yn) * pow(2.0, fp_upscale_n) ) ) * prop_to_next) );

            //float y_out = ( yn * pow(2.0, fp_upscale_n) / dbl_range_max
            //              +
            //              ( ((  ( yn1 * pow(2.0, fp_upscale_n1) / dbl_range_max ) - ( yn * pow(2.0, fp_upscale_n) / dbl_range_max ) ) * prop_to_next) / dbl_range_max) );

            //float y_out = (
            //                ( yn * pow(2.0, fp_upscale_n) / dbl_range_max
            //                +
            //                ( ((  ( yn1 * pow(2.0, fp_upscale_n1) / dbl_range_max ) - ( yn * pow(2.0, fp_upscale_n) / dbl_range_max ) ) * prop_to_next) / dbl_range_max) )
            //              );

            float y_out = (
                            ( yn * pow(2.0, fp_upscale_n)
                          +
                            ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) ) * prop_to_next) / dbl_range_max) )
                          ) / dbl_range_max ;

            int res_int_proper_old = FixedFloatConversion::from_float(y_out, up_out);


            //int res_int_proper =
            //    ((
            //                ( yn * pow(2.0, fp_upscale_n)
            //              +
            //                ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) ) * prop_to_next) / dbl_range_max) )
            //              ) / dbl_range_max ) *
            //    (double(range_max) / pow(2.0, up_out) );

            //int res_int_proper =  ( yn * pow(2.0, fp_upscale_n) + ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) ) * prop_to_next) / dbl_range_max) ) / pow(2.0, up_out) ;


            //int prop_to_next2 = ( (( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * dbl_range_max ;
            //int res_int_proper =  ( yn * pow(2.0, fp_upscale_n) + ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) )
            //                        * prop_to_next2
            //                       ) / dbl_range_max) ) / pow(2.0, up_out) ;

            //int prop_to_next2 = (( (( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * dbl_range_max );
            //int res_int_proper =  ( yn * pow(2.0, fp_upscale_n) + ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) )
            //                        * (( (( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * dbl_range_max )
            //                       ) / dbl_range_max) ) / pow(2.0, up_out) ;

            //OK:
            //int res_int_proper =  ( yn * pow(2.0, fp_upscale_n) + ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) ) * (( (( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * dbl_range_max )) / dbl_range_max) ) / pow(2.0, up_out) ;
            //


            //int res_int_proper =  ( yn * pow(2.0, fp_upscale_n) + ( ((  ( yn1 * pow(2.0, fp_upscale_n1)  ) - ( yn * pow(2.0, fp_upscale_n)  ) ) * (( (( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) ) ) * dbl_range_max )) / dbl_range_max) ) / pow(2.0, up_out) ;

            // OK
            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //int res_int_proper =  ( yn * N0 + ( ((  ( yn1 * N1  ) - ( yn * N0  ) ) * (((( x * pow(2.0, up_x) / dbl_range_max )  - (xn_new* M1 )) / ((xn1_new-xn_new) * M1 ) ) * dbl_range_max )) / dbl_range_max) ) / pow(2.0, up_out) ;


            // OK:
            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //int res_int_proper =(yn*N0+((( yn1*N1 - yn*N0 )*((((x*pow(2.0,up_x)/dbl_range_max)-(xn_new*M1))/((xn1_new-xn_new)*M1))*dbl_range_max))/dbl_range_max))/pow(2.0,up_out);

           // // OK:
           // double M1 = pow(2.0, -manual_upscale);
           // double N0 = pow(2.0, fp_upscale_n);
           // double N1 = pow(2.0, fp_upscale_n1);

           // int x_diff = xn1_new-xn_new; // THIS IS PROBABLY FIXED!


           // int res_int_proper =(yn*N0+((( yn1*N1 - yn*N0 )*
           //                 ((
           //                         ( x*pow(2.0,up_x)/dbl_range_max - xn_new*M1 )  / ( x_diff*M1))*dbl_range_max) ) /dbl_range_max)) / pow(2.0,up_out);
           //

            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //double P =  pow(2.0, -up_out);

            //int x_diff = xn1_new-xn_new; // THIS IS PROBABLY FIXED!


            //int res_int_proper =(yn*N0+
            //        (
            //            //(( yn1*N1 - yn*N0 )* (( ( x*pow(2.0,up_x)/dbl_range_max - xn_new*M1 )  / (x_diff*M1))*dbl_range_max) ) /dbl_range_max
            //            ((( yn1*N1 - yn*N0 )* (( ( x*pow(2.0,up_x)/dbl_range_max - xn_new*M1 )  / (x_diff*M1))) ) )
            //        )
            //
            //        ) * P ;

            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //double P =  pow(2.0, -up_out);
            //double X = pow(2.0, up_x-(nbits-1));

            //int x_diff = xn1_new-xn_new; // THIS IS PROBABLY FIXED!


            //int res_int_proper =(yn*N0+
            //        (
            //            ((( yn1*N1 - yn*N0 )*((( x*X - xn_new*M1) / (x_diff*M1)))))
            //        )
            //
            //        ) * P ;

            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //double P =  pow(2.0, -up_out);
            //double X = pow(2.0, up_x-(nbits-1));

            //int x_diff = xn1_new-xn_new; // THIS IS PROBABLY FIXED!


            //int res_int_proper =(yn*N0+
            //        (
            //            //( yn1*N1 - yn*N0 )*((( x*X - xn_new*M1) / (x_diff*M1)))
            //            ( yn1*N1 - yn*N0 )*( x*X - xn_new*M1) / x_diff / M1
            //        )
            //
            //        ) * P ;
            //
            //

            //int right_shift = nbits_table_int - upscale_int -1 ;
            //int manual_upscale = -right_shift + (nbits-1 - nbits_table) ;
            
            //int manual_upscale =  upscale_int  + nbits  - 2* nbits_table_int ;
            assert(manual_upscale ==  ( upscale_int  + NBIT_VARIABLES  - 2* nbits_table_int ) ) ;

            //double M1 = pow(2.0, -manual_upscale);
            //double N0 = pow(2.0, fp_upscale_n);
            //double N1 = pow(2.0, fp_upscale_n1);
            //double P =  pow(2.0, -up_out);
            //double X = pow(2.0, up_x-(nbits-1));

            //double X_OVER_M1 = pow(2.0, up_x-(nbits-1) + manual_upscale ); //X / M1;
            //double X_OVER_M1 = pow(2.0, up_x - nbits +1  + upscale_int  + nbits  - 2* nbits_table_int  ); //X / M1;
            
            int X_OVER_M1_pow = up_x +1  + upscale_int   - 2* nbits_table_int ; //X / M1;
            double X_OVER_M1 = pow(2.0, X_OVER_M1_pow ); //X / M1;
           
            //double N1P = pow(2.0, fp_upscale_n1 - up_out);
            //int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - (1<<(upscale_int+manual_upscale) );

            
            int diffN = fp_upscale_n1 - fp_upscale_n;
            assert (diffN >= 0);

            //double N0 = pow(2.0, fp_upscale_n); =  pow(2.0, fp_upscale_n1) / pow(2.0, diffN); = N1 /pow(2.0,diffN);

            //int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - (1<<(upscale_int+manual_upscale) );
            //int xn1_new =  xn_new + (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;
            //int x_diff = xn1_new-xn_new; // THIS IS PROBABLY FIXED!

            //int x_diff = (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;
            //int res_int_proper =(yn*N0+ ( ( yn1*N1 - yn*N0 )*( x*X - xn_new*M1) / x_diff / M1) ) * P ;


            // OK, so yn and yn1 are big integer, because they are stored near total resolution:
            //int x_diff = (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;
            //int x_diff = 1<< (2 * upscale_int + 1 + nbits  - 3* nbits_table)  ;

            //double N1P_OVER_xdiff =  pow(2.0, fp_upscale_n1 - up_out) / pow(2.0, 2 * upscale_int + 1 + nbits  - 3* nbits_table);
            //double N1P_OVER_xdiff =  pow(2.0, (fp_upscale_n1 - up_out) -(2 * upscale_int + 1 + nbits  - 3* nbits_table_int));
            int N1P_OVER_xdiff_pow =  fp_upscale_n1 - up_out -2 * upscale_int - 1 - NBIT_VARIABLES  + 3* nbits_table_int;
            //double N1P_OVER_xdiff =  pow(2.0, N1P_OVER_xdiff_pow);
            
            //int res_int_proper =(yn*N0+ ( ( yn1*N1 - yn*N0 )*( x*X - xn_new*M1) / x_diff / M1) ) * P ;
            //int res_int_proper = P*yn*N0 + (int)(P * (yn1*N1 - yn*N0 )*(x*X - xn_new*M1) / x_diff / M1 );


            //int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - (1<<(upscale_int+manual_upscale) );
            //int xn1_new =  xn_new + (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;

            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int)(P * (yn1*N1 - yn*N0 )*(x*X - xn_new*M1) / x_diff / M1 );
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int)(P * (yn1*N1 - yn*N0 )*(x*X - xn_new*M1) / x_diff / M1 );
            //
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) (P * (yn1*N1 - yn*N0 )*(x*X/M1 - xn_new) / x_diff );
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) (P * (yn1*N1 - yn*N1/pow(2.0,diffN) )*(x*X/M1 - xn_new) / x_diff );
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) (P * N1 * (yn1 - (yn>>diffN) )*(x*X/M1 - xn_new) / x_diff );
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) (P * N1 * (yn1 - (yn>>diffN) )*(x*X_OVER_M1 - xn_new) / x_diff );

            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) ((yn1 - (yn>>diffN) )*(x*X_OVER_M1 - xn_new) * N1P/ x_diff );
            //
            cout << "\nDEBUG: x: " << x ;
            cout << "\nDEBUG: X_OVER_M1: " << X_OVER_M1 ;
            
            
            double v1 = x*X_OVER_M1;
            int v2 = auto_shift( x, X_OVER_M1_pow);
            cout << "\nDEBUG: v1: " << v1;
            cout << "\nDEBUG: v2: " << v2;
            

            

            cout << "\n";
            //assert(0);

            
            // ** SOURCE OF TRUNCATION ERRORS! **
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) ((yn1 - (yn>>diffN) )*(x*X_OVER_M1 - xn_new) * N1P_OVER_xdiff );
            //int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + (int) (((long)(yn1 - (yn>>diffN) )*(long)(v2 - xn_new)) * N1P_OVER_xdiff );
            int res_int_proper = auto_shift(yn, fp_upscale_n-up_out) + auto_shift64(((long)(yn1 - (yn>>diffN) )*(long)(v2 - xn_new)), N1P_OVER_xdiff_pow );



            cout << "\n** OLD:" <<  res_int_proper_old;
            cout << "\n** NEW:" << res_int_proper;
            cout << "\n";
            
            
            assert ( res_int_proper_old == res_int_proper || fabs(res_int_proper-res_int_proper_old) < 3 || fabs(res_int_proper-res_int_proper_old)/ (double) res_int_proper <= 6.e-2 );


            cout << "\n -- prop to next: " << prop_to_next;
            cout << "\nworking_upscale" << working_upscale;






            {
            float prop_to_next = (fp_xout - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) );
            float yn_fl = FixedFloatConversion::to_float(yn, fp_upscale_n);
            float yn1_fl = FixedFloatConversion::to_float(yn1, fp_upscale_n1);
            cout << "\n -- yn_f1:" << yn_fl;
            cout << "\n -- yn1_f1:" << yn1_fl;
            float y_out = yn_fl + (yn1_fl-yn_fl) * prop_to_next;
            int res_int_proper = FixedFloatConversion::from_float(y_out, up_out);
            cout << "\n -- Interpolated y :" << y_out;
            cout << "\nBLAH" << res_int_proper;
            }





            // OK, lets linearly interpolate between these values:
            // 3. Interpolate between yn and yn+1
            //float prop_to_next = (fp_xout - xn) / (xn1-xn);
            //float prop_to_next = (fp_xout - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) );
            //cout << "\n -- prop to next: " << prop_to_next;


            //float y_out = yn_fl + (yn1_fl-yn_fl) * prop_to_next;


            //cout << "\n -- Interpolated y :" << y_out;



            //cout << "\n\n";

            //int res_int_proper = from_float(y_out, up_out);




            int res_int = FixedFloatConversion::from_float(exp(fp_xout), up_out);


            // Validate:
            int diff = res_int_proper - res_int;
            if(diff < 0) diff = -diff;
            float error = ((float)diff / res_int_proper);
            cout << "\n -- Error y: " << error * 100. << "%";
            cout << "\n  -- diff: " << diff;
            cout << "\n\n";

            //assert(diff <10 || ( (float) diff / res_int_proper) < 0.1e-2);

            //assert(diff <10 || ( (float) diff / res_int_proper) < 15.e-2);




            return res_int_proper;

        }
};



//typedef LookUpTablePower2 LookUpTableExpPower2;







