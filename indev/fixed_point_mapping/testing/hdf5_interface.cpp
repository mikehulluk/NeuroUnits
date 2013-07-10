
#include "hdf5_interface.h"





#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>










class _HDF5Location
{
    string location;
    bool _is_absolute;
    public:
        _HDF5Location(const string& location_in)
        {
            string location = location_in;

            if( location[0] == '/')
            {
                location = location.substr(1, location.size() );
                _is_absolute = true;
            }
            else
            {
                _is_absolute = false;
            }


            if( location[location.size()-1] == '/') location = location.substr(1, location.size());
            this->location = location;
        }

        bool is_local() const
        {
            size_t sep_loc = location.find('/');
            return (sep_loc == string::npos);
        }

        bool is_absolute() const
        {
            return _is_absolute;
        }

        string get_local_path() const
        {
            size_t sep_loc = location.find('/');
            return location.substr(0,sep_loc);
        }

        string get_child_path() const
        {
            assert( !is_local() );
            size_t sep_loc = location.find('/');
            return location.substr(sep_loc+1, location.size());
        }
};








HDF5DataSet2DStd::HDF5DataSet2DStd( const string& name, HDF5GroupPtrWeak pParent, const HDF5DataSet2DStdSettings& settings)
    :name(name), settings(settings)
{
    cout << "\nCreating DataSet:" << name  << " \n";



    hsize_t data_dims[2] = {0, settings.size};
    hsize_t data_max_dims[2] = {H5S_UNLIMITED, settings.size} ;
    dataspace_id = H5Screate_simple(2, data_dims, data_max_dims);



    hsize_t chunk_dims[2] = {50, settings.size}; // I don't undersnat this line!
    hid_t prop = H5Pcreate(H5P_DATASET_CREATE);
    H5Pset_chunk (prop, 2, chunk_dims);
    dataset_id = H5Dcreate2 (pParent.lock()->group_id, name.c_str(), H5T_NATIVE_FLOAT, dataspace_id, H5P_DEFAULT, prop, H5P_DEFAULT);


    H5Pclose (prop);

}




HDF5DataSet2DStd::~HDF5DataSet2DStd()
{
    cout << "\nClosing DataSet:" << name  << " \n";
    H5Dclose(dataset_id);
    H5Sclose(dataspace_id);
}


void HDF5DataSet2DStd::append_buffer( float* pData )
{
    cout << "\nWritting to buffer";

    // How big is the array:?
    hsize_t dims[2], max_dims[2];
    hid_t dataspace = H5Dget_space(dataset_id);
    H5Sget_simple_extent_dims(dataspace, dims, max_dims);
    H5Sclose(dataspace);

    cout << "\nDims:" << dims[0] << ", " << dims[1] << "\n";
    assert(dims[1] ==settings.size);

    int curr_size = dims[0];





    // Extend the table:
    hsize_t new_data_dims[2] = {curr_size+1, dims[1] };
    H5Dextend (dataset_id, new_data_dims);

    // And copy:
    hid_t filespace = H5Dget_space(dataset_id);
    hsize_t offset[2] = {curr_size, 0};
    hsize_t count[2] = {1, dims[1]};
    H5Sselect_hyperslab(filespace, H5S_SELECT_SET, offset, NULL, count, NULL);
    hsize_t dim1[2] = {1,dims[1]};
    hid_t memspace = H5Screate_simple(2, dim1, NULL);
    H5Dwrite (dataset_id, H5T_NATIVE_FLOAT, memspace, filespace, H5P_DEFAULT, pData);

}

void HDF5DataSet2DStd::append_buffer( FloatBuffer fb )
{
    assert(fb.size() == this->settings.size);
    this->append_buffer(fb.get_data_pointer() );

}





HDF5Group::HDF5Group(const string& location, HDF5FilePtrWeak fileptr,  HDF5GroupPtrWeak parentptr)
    :location(location), fileptr(fileptr)
{

    if( is_root() )
    {
        cout << "\nCreating Root Group: " << location;
    }
    else
    {
        cout << "\nCreating Group: " << location;

        HDF5GroupPtr parent = parentptr.lock();
        if(parent->is_root() )
        {
            group_id = H5Gcreate2(fileptr.lock()->file_id, location.c_str(), H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
        }
        else
        {
            group_id = H5Gcreate2(parent->group_id, location.c_str(), H5P_DEFAULT, H5P_DEFAULT, H5P_DEFAULT);
        }
    }

}

HDF5Group::~HDF5Group()
{
    datasets.clear();
    groups.clear();

    cout << "\nShutting down group: " << location << "\n";
    if(!is_root())
    {
        H5Gclose(group_id);
    }


}




HDF5GroupPtr HDF5Group::get_subgroup(const string& location_in)
{
    cout << "\nGetting Group: " << location << "\n";



    _HDF5Location loc(location_in);

    // Sanity checks:
    if( loc.is_absolute() ) assert(this->is_root() );

    if(loc.is_local())
    {
        return this->get_subgrouplocal(loc.get_local_path());
    }
    else
    {
        return this->get_subgrouplocal(loc.get_local_path())->get_subgroup(loc.get_child_path());
    }

}



HDF5GroupPtr HDF5Group::get_subgrouplocal(const string& location)
{

    assert( location.find("/") == string::npos );

    if( groups.find(location) == groups.end() )
    {
        fileptr.lock();
        groups[location] = HDF5GroupPtr( new HDF5Group(location, fileptr,  HDF5GroupPtrWeak(shared_from_this()) ) );
    }

    return groups[location];
}



bool HDF5Group::is_root()
{
    return this->location == "/";
}






HDF5DataSet2DStdPtr HDF5Group::create_dataset(const string& name, const HDF5DataSet2DStdSettings& settings)
{
    assert( datasets.find(name) == datasets.end() );

    datasets[name] = HDF5DataSet2DStdPtr( new HDF5DataSet2DStd(name, HDF5GroupPtrWeak(shared_from_this()), settings ) );
    return datasets[name];

}


HDF5DataSet2DStdPtr HDF5Group::get_dataset(const string& name)
{
    _HDF5Location loc(name);
    // Sanity checks:
    if( loc.is_absolute() ) assert(this->is_root() );


    if(loc.is_local())
    {
        cout << "Looking for dataset: " << loc.get_local_path() << "\n";
        assert( datasets.find(loc.get_local_path()) != datasets.end() );
        return datasets[loc.get_local_path()];
    }
    else
    {
        return this->get_subgrouplocal(loc.get_local_path())->get_dataset(loc.get_child_path());
    }

}















void HDF5File::init()
{
        root_group = HDF5GroupPtr( new HDF5Group("/",  HDF5FilePtrWeak(this->shared_from_this() ), HDF5GroupPtrWeak()  ) );
}


HDF5File::HDF5File(const string& filename)
        : filename(filename)
{
        cout << "HDFFile( " << filename << " )";
        file_id = H5Fcreate(filename.c_str(), H5F_ACC_TRUNC, H5P_DEFAULT, H5P_DEFAULT);
}


HDF5File::~HDF5File()
{
    cout << "\nClosing HDF file: " << filename << "\n";
    cout << "\n - Releasing groups: ";
    root_group.reset();

    cout << "\n - Releasing handle";
    H5Fclose(this->file_id);
}


HDF5GroupPtr HDF5File::get_group(const string& location)
{

    if(!root_group)
    {
        init();
    }

    return this->root_group->get_subgroup(location);

}


HDF5DataSet2DStdPtr HDF5File::get_dataset(const string& location)
{
    if(!root_group)
    {
        init();
    }

    return this->root_group->get_dataset(location);
}






herr_t my_hdf5_error_handler (void *unused)
{
   fprintf (stderr, "An HDF5 error was detected. Bye.\n");
   assert(0);
   exit (1);
}
