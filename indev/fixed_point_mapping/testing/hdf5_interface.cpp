
#include "hdf5_interface.h"









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
    //H5Pclose (dataspace_id);


}




HDF5DataSet2DStd::~HDF5DataSet2DStd()
{
    cout << "\nClosing DataSet:" << name  << " \n";
    H5Dclose(dataset_id);
    H5Sclose(dataspace_id);
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

    string location = location_in;

    // Sanity checks:
    assert(location[0] != '/' or is_root()); // Looking up absolute path on non-root node

    // Drop opening '/'
    if( location[0] == '/') location = location.substr(1, location.size() );
    // Drop final '/'
    if( location[location.size()-1] == '/') location = location.substr(1, location.size());

    size_t sep_loc = location.find('/');
    if(sep_loc != string::npos)
    {
        string sg = location.substr(0,sep_loc);
        string sg_child = location.substr(sep_loc+1, location.size());
        //cout << "\nSplitting:" << location << " -> " << sg << " and " << sg_child << "\n";
        return this->get_subgrouplocal(sg)->get_subgroup(sg_child);
    }

    else
    {
        return this->get_subgrouplocal(location);
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

    assert( datasets.find(name) != datasets.end() );
    return datasets[name];
}


HDF5GroupPtr HDF5Group::get_datasetlocal(const string& location)
{


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





herr_t my_hdf5_error_handler (void *unused)
{
   fprintf (stderr, "An HDF5 error was detected. Bye.\n");
   assert(0);
   exit (1);
}
