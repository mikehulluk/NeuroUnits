#ifndef __FIXED_POINT_OPS_H__
#define __FIXED_POINT_OPS_H__



namespace tmpl_fp_ops
{
    


inline
IntType do_add_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

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
        float res_fp_fl = FixedFloatConversion::to_float(v1,up1) + FixedFloatConversion::to_float(v2,up2);
        IntType res_fp = IntType(FixedFloatConversion::from_float(res_fp_fl, up_local));

        if( CHECK_INT_FLOAT_COMPARISON )
        {
            IntType diff = res_int - res_fp;
            //cout << "diff" << diff << "\n" << flush; 
            if(diff <0) diff = -diff;
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

inline
IntType do_sub_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

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
        float res_fp_fl = FixedFloatConversion::to_float(v1,up1) - FixedFloatConversion::to_float(v2,up2);
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
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
        #endif
    }
    #endif

    return res_int;
}
inline
IntType do_mul_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{
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
        float res_fp_fl = FixedFloatConversion::to_float(v1,up1) * FixedFloatConversion::to_float(v2,up2);
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
            HDFManager::getInstance().get_file(output_filename)->get_dataset((boost::format("simulation_fixed/float/operations/op%s")% get_value32(expr_id) ).str())->append_buffer(
                    DataBuffer<T_hdf5_type_float>() | (T_hdf5_type_float) (FixedFloatConversion::to_float(v1,up1)) | (T_hdf5_type_float) (FixedFloatConversion::to_float(v2,up2)) | (T_hdf5_type_float) (res_fp_fl) ) ;
        }
        #endif
    }
    #endif

    

    return res_int;

}


inline
IntType do_div_op(IntType v1, IntType up1, IntType v2, IntType up2, IntType up_local, IntType expr_id)
{

    NativeInt64 v1_L = (NativeInt64) get_value32(v1);
    NativeInt64 v2_L = (NativeInt64) get_value32(v2);

    v1_L = auto_shift64(v1_L, (VAR_NBITS-1) );
    NativeInt64 v = v1_L/v2_L;
    v = auto_shift64(v, get_value32( up1-up2 - up_local) );
    assert( v < (1<<(VAR_NBITS) ) );
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
        float res_fp_fl = FixedFloatConversion::to_float(v1,up1) / FixedFloatConversion::to_float(v2,up2);
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

template<typename EXPLUT_TYPE>
inline IntType int_exp(IntType v1, IntType up1, IntType up_local, IntType expr_id, EXPLUT_TYPE exponential_lut)
{
    //IntType res_int = lookuptables.exponential.get( v1, up1, up_local );
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
        float res_fp_fl = exp( FixedFloatConversion::to_float(v1,up1) );
        IntType res_fp = IntType(FixedFloatConversion::from_float( res_fp_fl, up_local));
        
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






#endif
