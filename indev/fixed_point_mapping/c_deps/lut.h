

//(-5.2621269, 6.3751221)
#include <vector>
#include <iostream>
using namespace::std;


/*

class LookUpTable
{

    vector<double> pData;
    double step_size;
    double min_value;
    double max_value;
public:
        LookUpTable(vector<double> pData, double min_value, double max_value)
            : pData(pData), step_size( (max_value-min_value) / pData.size() ), min_value(min_value), max_value(max_value)
        {

        }

        double get(double x)
        {
            cout << "\nget(" << x << ")" << "\n";

            assert( x > min_value && x < max_value);
            double index_float = (x - min_value ) / step_size;

            size_t index_int = (size_t) index_float;
            double offset_float = index_float - index_int;

            cout << "Offset float: " << offset_float << "\n";
            assert(offset_float >= 0 && offset_float < 1.0 );

            double y1 = pData.at(index_int);
            double y2 = pData.at(index_int+1);

            double y2_delta = y2 - y1;

            double res = y1 + y2_delta * offset_float;

            return res;
        }


};



class LookUpTableExp
{
    LookUpTable table;

    static vector<double> _build_data(size_t size, double min_value, double max_value)
    {
        vector<double> interplpts;

        double step_size = (max_value-min_value) / size;

        for(size_t i=0;i<size;i++)
        {
            double x = i*step_size + min_value;

            double res = exp(x);
            interplpts.push_back(res);
        }


        return interplpts;
    }

public:
    LookUpTableExp(size_t size, double min_value, double max_value)
        : table( _build_data(size, min_value, max_value), min_value, max_value )
    { }

    double get(float x)
    {

        cout << "Getting Exp " << x <<" \n";
        double x1 =  exp(x);
        double x2 = table.get(x);
        cout << "x1: " << x1 << "\n";
        cout << "x2: " << x2 << "\n";

        double diff = x1-x2;
        if (diff < 0.0) diff = -diff;

        assert (diff/x2 < 0.001);

        return x2;
    }
};




*/





#include <numeric>

#include <algorithm>
#include <cmath>


double my_fabs(double x) { return fabs(x); }

const float recip_ln_two = 1.44269504;


template<typename MathFunction>
class LookUpTablePower2
{

    vector<int> pData;
    vector<double> _x_vals;
    size_t nbits_table;
    size_t upscale;
    const size_t table_size;
    const size_t table_size_half;


public:


        // The table is symmetrical about zero:
        size_t int_to_index( int my_int)
        {
            //int min_val = (1<< (this->nbits_table-1));
            return my_int + table_size_half;

        }

        size_t index_to_int( int index)
        {

            //int min_val = (1<< (this->nbits_table-1));
            return index - table_size_half;

        }


        LookUpTablePower2(size_t nbits_table, int upscale)
             : nbits_table(nbits_table), upscale(upscale), table_size(1<<(nbits_table)), table_size_half(1<<(nbits_table-1))


        {



            //double upscale_factor_in =  pow(2.0, upscale);

            // Calculate the output values:
            for(int i = 0; i < (int) table_size; i++)
            {
                //int x_value_int = index_to_int(i);
                cout << "x_int" << i-(int)table_size_half << "\n";
                double x_value_double = (double)( i - (int) table_size_half) * pow(2.0, upscale) / table_size_half;

                double res = MathFunction::get_value(x_value_double);

                cout << "func(" << x_value_double << ") -> " << res << "\n";


                // We use a variable fixed_point format to encde the result, because the ranges with exponentials
                // are simply too great (-8,8) -> (0.000335463, 1808.04)
                //
                // The optimal fixed point value upscaling to get our value in the range (-1,1) will be
                // fp = ln2( exp(x) )
                // which turns out to be linear in x (:
                // fp =~ 1.4426 * x
                int fp_upscale = recip_ln_two * x_value_double;
                cout << "  -- fixed_point upscale: " << fp_upscale << "\n";

                int res_as_int = from_float(res, fp_upscale);


                // Doube check we are not loosing too much precision here:
                double res_as_float = to_float(res_as_int, fp_upscale);
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

        int get(int x, int up_x, int up_out)
        {
            cout << "\nget()";


            double fp_xout = to_float(x,up_x) ;
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

            int right_shift1 = nbits - up_x - 2;
            int index_0_signed = (x>>right_shift1) + table_size_half;
            size_t index_0 = index_0_signed;

            if(0)
            {
                // Float check:
                double orig_x_neg_1_to_1 = to_float(x, up_x) / table_size_half;
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
            //int manual_upscale = -right_shift + (nbits-1 - nbits_table) ;
            ////double xn_new =  (double)( (int)index_0 * pow(2.0, -right_shift) ) - pow(2.0, upscale_int) ;
            //double xn_new =  (double)( (int)index_0 * pow(2.0, -right_shift+manual_upscale) ) - pow(2.0, upscale_int+manual_upscale) ;
            //double xn1_new =  xn_new + pow(2.0, upscale_int- (nbits_table_int-1) + manual_upscale) ;


            
            // Lets upscale so that we keep as much precision as possible:
            int manual_upscale = -right_shift + (nbits-1 - nbits_table) ;
            assert(-right_shift+manual_upscale > 0);
            //int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - pow(2.0, upscale_int+manual_upscale) ;
            //int xn1_new =  xn_new + pow(2.0, upscale_int- (nbits_table_int-1) + manual_upscale) ;
            int xn_new =  ( index_0<<(-right_shift+manual_upscale) )  - (1<<(upscale_int+manual_upscale) );
            int xn1_new =  xn_new + (1<< (upscale_int- (nbits_table_int-1) + manual_upscale) ) ;





            cout << "\n =====>> xn_new: " << xn_new;

            int fp_upscale_n = int( recip_ln_two  *  xn_new * pow(2.0, -manual_upscale) );
            int fp_upscale_n1 = int( recip_ln_two *  xn1_new * pow(2.0, -manual_upscale) );




            int yn = pData[index_0];
            int yn1 = pData[index_0+1];




            cout << "\n -- y_n int: " << yn;
            cout << "\n -- y_n1 int: " << yn1;
            cout << "\n -- y_n Scaling int: " << fp_upscale_n;
            cout << "\n -- y_n1 Scaling int: " << fp_upscale_n1;




            float yn_fl = to_float(yn, fp_upscale_n);
            float yn1_fl = to_float(yn1, fp_upscale_n1);

            // OK, lets linearly interpolate between these values:
            // 3. Interpolate between yn and yn+1
            //float prop_to_next = (fp_xout - xn) / (xn1-xn);
            float prop_to_next = (fp_xout - (xn_new* pow(2.0, -manual_upscale) ) ) / ((xn1_new-xn_new) * pow(2.0, -manual_upscale) );
            cout << "\n -- prop to next: " << prop_to_next;
            float y_out = yn_fl + (yn1_fl-yn_fl) * prop_to_next;


            cout << "\n -- yn_f1:" << yn_fl;
            cout << "\n -- yn1_f1:" << yn1_fl;
            cout << "\n -- Interpolated y :" << y_out;


            //cout << "\n";
            //assert( index == index_0);

            cout << "\n\n";

            int res_int_proper = from_float(y_out, up_out);




            int res_int = from_float(exp(fp_xout), up_out);


            // Validate:
            int diff = res_int_proper - res_int;
            if(diff < 0) diff = -diff;
            float error = ((float)diff / res_int_proper);
            cout << "\n -- Error y: " << error * 100. << "%";
            cout << "\n  -- diff: " << diff;
            cout << "\n\n";

            //assert(diff <10 || ( (float) diff / res_int_proper) < 0.1e-2);

            assert(diff <10 || ( (float) diff / res_int_proper) < 5.e-2);




            return res_int_proper;








        }
};



class ExpFunc
{
public:
    static double get_value(double x)
    {
        return exp(x);
    }

};


typedef LookUpTablePower2<ExpFunc> LookUpTableExpPower2;







