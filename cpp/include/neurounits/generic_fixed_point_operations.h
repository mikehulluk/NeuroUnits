#ifndef  __FIXED_POINT_OPS_H__
#define  __FIXED_POINT_OPS_H__












namespace deprecated_to_inline_tmpl_fp_ops
{
    
    
    template<int VAR_NBITS>
    inline IntType do_add_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
    {
        typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
        
        IntType res_int = auto_shift(v1, up1-up_local) + auto_shift(v2, up2-up_local);

        #if USE_HDF && SAVE_HDF5_INT && SAVE_HDF5_PER_OPERATION
        if( expr_id != -1)
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value32(v1) | (T_hdf5_type_int) get_value32(v2) | (T_hdf5_type_int) get_value32(res_int) ) ;
        }
        #endif

        #if CALCULATE_FLOAT
        {
            double res_fp_fl = FixedFloatConversion::to_float(v1,up1) + FixedFloatConversion::to_float(v2,up2);
            IntType res_fp = IntType(FixedFloatConversion::from_float(res_fp_fl, up_local));

            if( CHECK_INT_FLOAT_COMPARISON )
            {
                IntType diff = res_int - res_fp;
                //cout << "diff" << diff << "\n" << flush; 
                if(diff <0) diff = -diff;
                //cout << "\ndiff: " << diff << std::flush;
                assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
            }
            
            #if USE_HDF && SAVE_HDF5_FLOAT  && SAVE_HDF5_PER_OPERATION
            if( expr_id != -1)
            {
                HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                        DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
            }
            #endif
        }
        #endif


        return res_int;
    }

    template<int VAR_NBITS>
    inline IntType do_sub_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
    {
        typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
        IntType res_int = auto_shift(v1, up1-up_local) - auto_shift(v2, up2-up_local);

        #if USE_HDF && SAVE_HDF5_INT && SAVE_HDF5_PER_OPERATION

        if( expr_id != -1)
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value32(v1) | (T_hdf5_type_int) get_value32(v2) | (T_hdf5_type_int) get_value32(res_int) ) ;
        }
        #endif

        #if CALCULATE_FLOAT
        {
            double res_fp_fl = FixedFloatConversion::to_float(v1,up1) - FixedFloatConversion::to_float(v2,up2);
            IntType res_fp = IntType(FixedFloatConversion::from_float(res_fp_fl, up_local));

            if( CHECK_INT_FLOAT_COMPARISON )
            {
                IntType diff = res_int - res_fp;
                //cout << "diff" << diff << "\n" << flush; 
                if(diff <0) diff = -diff;
                assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
            }

            #if USE_HDF && SAVE_HDF5_FLOAT && SAVE_HDF5_PER_OPERATION
            if( expr_id != -1)
            {
                HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/double/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                        DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
            }
            #endif
        }
        #endif

        return res_int;
    }

    template<int VAR_NBITS>
    inline IntType do_mul_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
    {
        typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
        
        // Need to promote to 64 bit:
        NativeInt64 v12 = (NativeInt64) get_value32(v1) * (NativeInt64) get_value32(v2);
        IntType res_int = inttype32_from_inttype64<IntType>( auto_shift64(v12, get_value32(up1+up2-up_local-(VAR_NBITS-1)) ) ) ;



        #if USE_HDF && SAVE_HDF5_INT && SAVE_HDF5_PER_OPERATION

        if( expr_id != -1)
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value32(v1) | (T_hdf5_type_int) get_value32(v2) | (T_hdf5_type_int) get_value32(res_int) ) ;
        }
        #endif

        #if CALCULATE_FLOAT
        {
            double res_fp_fl = FixedFloatConversion::to_float(v1,up1) * FixedFloatConversion::to_float(v2,up2);
            IntType res_fp = IntType(FixedFloatConversion::from_float(res_fp_fl, up_local));

            if( CHECK_INT_FLOAT_COMPARISON )
            {
                IntType diff = res_int - res_fp;
                //cout << "diff" << diff << "\n" << flush; 
                if(diff <0) diff = -diff;
                assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
            }

            #if USE_HDF && SAVE_HDF5_FLOAT && SAVE_HDF5_PER_OPERATION
            if( expr_id != -1)
            {
                HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/double/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                        DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
            }
            #endif
        }
        #endif

        

        return res_int;

    }


    template<int VAR_NBITS>
    inline IntType do_div_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
    {
        typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
        
        NativeInt64 v1_L = (NativeInt64) get_value32(v1);
        NativeInt64 v2_L = (NativeInt64) get_value32(v2);

        v1_L = auto_shift64(v1_L, (VAR_NBITS-1) );
        NativeInt64 v = v1_L/v2_L;
        v = auto_shift64(v, get_value32( up1-up2 - up_local) );
        if (! ( v < (1<<(VAR_NBITS) ) ) )
        {
            cout << "\n Error in Division (overflows target):";
            cout << "\n Expr ID: " << expr_id;
            cout << "\n Nom: " << FixedFloatConversion::to_float(v1,up1);
            cout << "\n Denim: " << FixedFloatConversion::to_float(v2,up2);
            cout << "\n Result: (upscale) " << up_local;
            cout << "\n (int-max) " << (1l<<24);
            cout << "\n Result: (int) " << v;
            cout << "\n Result: (float) " << FixedFloatConversion::to_float(v, up_local);
            cout << "\n" << std::flush;

            assert(0);
        }
        IntType res_int = inttype32_from_inttype64<IntType>(v);
        


        #if USE_HDF && SAVE_HDF5_INT && SAVE_HDF5_PER_OPERATION

        if( expr_id != -1)
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value32(v1) | (T_hdf5_type_int) get_value32(v2) | (T_hdf5_type_int) get_value32(res_int) ) ;
        }
        #endif

        #if CALCULATE_FLOAT
        {
            double res_fp_fl = FixedFloatConversion::to_float(v1,up1) / FixedFloatConversion::to_float(v2,up2);
            IntType res_fp = IntType(FixedFloatConversion::from_float(res_fp_fl, up_local));

            if( CHECK_INT_FLOAT_COMPARISON )
            {
                IntType diff = res_int - res_fp;
                //cout << "diff" << "\n" << diff << flush; 
                if(diff <0) diff = -diff;
                assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT );
            }

            #if USE_HDF && SAVE_HDF5_FLOAT && SAVE_HDF5_PER_OPERATION
            if( expr_id != -1)
            {
                HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                        DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
            }
            #endif
        }
        #endif


        return res_int;

    }
    template<int VAR_NBITS, typename EXPLUT_TYPE>
    inline 
    IntType int_exp(IntType v1, IntType up1, IntType up_local, IntType expr_id, const EXPLUT_TYPE& exponential_lut)
    {
        typedef mh::FixedFloatConversion<VAR_NBITS> FixedFloatConversion;
        
        IntType res_int = exponential_lut.get( v1, up1, up_local );


        #if USE_HDF && SAVE_HDF5_INT && SAVE_HDF5_PER_OPERATION

        if( expr_id != -1)
        {
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/int/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                DataBuffer<T_hdf5_type_int>() | (T_hdf5_type_int) get_value32(v1) | (T_hdf5_type_int) get_value32(res_int) ) ;
        }
        #endif
        
        #if CALCULATE_FLOAT
        {
            double res_fp_fl = exp( FixedFloatConversion::to_float(v1,up1) );
            IntType res_fp = IntType(FixedFloatConversion::from_float( res_fp_fl, up_local));
            assert(0); //DEBUGGING disabled
            
            if( CHECK_INT_FLOAT_COMPARISON_FOR_EXP )
            {
                IntType diff = res_int - res_fp;
                cout << "diff" << "\n" << diff << flush; 
                if(diff <0) diff = -diff;
                assert( diff< ACCEPTABLE_DIFF_BETWEEN_FLOAT_AND_INT_FOR_EXP );
            }
            
            #if USE_HDF && SAVE_HDF5_FLOAT && SAVE_HDF5_PER_OPERATION
            if( expr_id != -1)
            {
            // -- Floating point version:
                HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) |  (T_hdf5_type_float) (res_fp_fl) ) ;
            }
            #endif
        }
        #endif
        
        return res_int;
    }
}








template<int NBITS_, typename IType_>
class FixedPointOp
{
public:
    static const int NBITS = NBITS_;
    typedef IType_ IType;



    static inline IType do_add_op(IType v1, IType up1, IType v2, IType up2, IType up_local, IType expr_id)
    {
        return deprecated_to_inline_tmpl_fp_ops::do_add_op<NBITS>(v1, up1, v2, up2, up_local, expr_id);
    }

    static inline IType do_sub_op(IType v1, IType up1, IType v2, IType up2, IType up_local, IType expr_id)
    {
        return deprecated_to_inline_tmpl_fp_ops::do_sub_op<NBITS>(v1, up1, v2, up2, up_local, expr_id);
    }

    static inline IType do_mul_op(IType v1, IType up1, IType v2, IType up2, IType up_local, IType expr_id)
    {
        return deprecated_to_inline_tmpl_fp_ops::do_mul_op<NBITS>(v1, up1, v2, up2, up_local, expr_id);
    }

    static inline
    IType do_div_op(IType v1, IType up1, IType v2, IType up2, IType up_local, IType expr_id)
    {
        return deprecated_to_inline_tmpl_fp_ops::do_div_op<NBITS>(v1, up1, v2, up2, up_local, expr_id);
    }
    
    template<typename EXPLUT_TYPE>
    static inline IType int_exp(IType v1, IType up1, IType up_local, IType expr_id, const EXPLUT_TYPE& exponential_lut)
    {
        return deprecated_to_inline_tmpl_fp_ops::int_exp<NBITS,EXPLUT_TYPE>(v1, up1, up_local, expr_id, exponential_lut);
    }
};





#endif
