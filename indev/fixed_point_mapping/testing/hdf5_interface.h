




#include "hdf5.h"
#include <hdf5_hl.h>




#include <boost/shared_ptr.hpp>
#include <boost/weak_ptr.hpp>
#include <string>
#include <vector>
#include <map>
#include <boost/enable_shared_from_this.hpp>
using namespace std;



// Signal Errors:
herr_t my_hdf5_error_handler (void *unused);





// Forward declarations:
class HDF5Group;
class HDF5File;
class HDF5DataSet2DStd;


typedef boost::shared_ptr<HDF5File> HDF5FilePtr;
typedef boost::weak_ptr<HDF5File> HDF5FilePtrWeak;
typedef boost::shared_ptr<HDF5Group> HDF5GroupPtr;
typedef boost::weak_ptr<HDF5Group> HDF5GroupPtrWeak;

typedef boost::shared_ptr<HDF5DataSet2DStd> HDF5DataSet2DStdPtr;




//template<typename T> class DataBuffer;



template< typename T>
class DataBuffer
{
public:
    vector<T> _data;

    inline T* get_data_pointer() {  return &(this->_data[0]); }
    inline size_t size() { return this->_data.size(); }
};

template<typename TYPE>
DataBuffer<TYPE> operator|(DataBuffer<TYPE> buff, TYPE data)
{
    buff._data.push_back(data);
    return buff;
}

typedef DataBuffer<float> FloatBuffer;
typedef FloatBuffer FB;








class HDF5DataSet2DStdSettings
{
public:
    int size;
    HDF5DataSet2DStdSettings(int size)
        : size(size)
    {}


};




class HDF5DataSet2DStd : public  boost::enable_shared_from_this<HDF5DataSet2DStd>
{
    const string name;
    hid_t dataset_id;
    hid_t dataspace_id;
    HDF5DataSet2DStdSettings settings;
public:
    HDF5DataSet2DStd( const string& name, HDF5GroupPtrWeak pParent, const HDF5DataSet2DStdSettings& settings);
    ~HDF5DataSet2DStd();

    void append_buffer( float* pData );
    void append_buffer( FloatBuffer fb );
};






class HDF5Group : public boost::enable_shared_from_this<HDF5Group>
{
public:
    const string location;
    hid_t group_id;

    HDF5FilePtrWeak fileptr;

    bool is_root();




public:
    HDF5Group(const string& location,  HDF5FilePtrWeak fileptr,  HDF5GroupPtrWeak parentptr);
    ~HDF5Group();

    typedef map<const string, HDF5GroupPtr> GroupPtrMap;
    GroupPtrMap groups;

    HDF5GroupPtr get_subgroup(const string& location);
    HDF5GroupPtr get_subgrouplocal(const string& location);


    typedef map<const string, HDF5DataSet2DStdPtr> DatasetPtrMap;
    DatasetPtrMap datasets;
    HDF5DataSet2DStdPtr create_dataset(const string& name, const HDF5DataSet2DStdSettings& settings);
    HDF5DataSet2DStdPtr get_dataset(const string& name);
    HDF5GroupPtr get_datasetlocal(const string& location);



};














class HDF5File : public boost::enable_shared_from_this<HDF5File>
{
    HDF5GroupPtr root_group;
public:
    const string filename;
    hid_t file_id;

public:
    HDF5File(const string& filename);
    ~HDF5File();
    void init();


    HDF5GroupPtr get_group(const string& location);
    HDF5DataSet2DStdPtr get_dataset(const string& location);
};






















class HDFManager
{
    public:
        static HDFManager& getInstance()
        {
            static HDFManager instance;
            return instance;
        }

    private:
        HDFManager(HDFManager const&);     // Don't Implement.
        void operator=(HDFManager const&); // Don't implement


        HDFManager()
        {
            H5Eset_auto (my_hdf5_error_handler, NULL);
        }
        ~HDFManager()
        {
            cout << "\n~HDFManager:";
        }


    private:

    typedef map<const string, HDF5FilePtr> FilePtrMap;
    FilePtrMap files;


    // Operations:
    public:
    HDF5FilePtr get_file(const string& filename)
    {
        // Create the new file object, if it doesn't exist:
        if( files.find(filename) == files.end() )
        {
            // Create the new file object:
            files[filename] = HDF5FilePtr( new HDF5File(filename) );
        }

        return files[filename];


    }

    void remove_file(const string& filename)
    {

    }


};







