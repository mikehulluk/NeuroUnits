

#include "hdf5_interface.h"




int main()
{

HDFManager::getInstance().remove_file("myfile.hdf");
HDFManager::getInstance().get_file("myfile.hdf");
HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO");
HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO/Hello/Checkit-out");

HDF5GroupPtr pGroup = HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO/Hello/Checkit-out");
pGroup->create_dataset("d1", HDF5DataSet2DStdSettings(4) );
HDF5DataSet2DStdPtr ds = pGroup->get_dataset("d1");

float data[] = {2.4, .3,4, 4.6, 9.6} ;
ds->append_buffer(data);
ds->append_buffer(data);
ds->append_buffer(data);
ds->append_buffer(data);
ds->append_buffer(FB() | 2.4f | 4.6f | 9.6f | 4.5f );
ds->append_buffer(FB() | 2.4f | 4.6f | 4.5f | 9.6f );


HDFManager::getInstance().get_file("myfile.hdf")->get_dataset("/SimulationResults/NONO/Hello/Checkit-out/d1")->append_buffer( FB() | 1.1f | 2.2f | 3.3f | 4.4f );


cout << "\n     **** FINISHED OK **** \n";
}




