

#include "hdf5_interface.h"




int main()
{

HDFManager::getInstance().remove_file("myfile.hdf");
HDFManager::getInstance().get_file("myfile.hdf");
HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO");
HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO/Hello/Checkit-out");

HDF5GroupPtr pGroup = HDFManager::getInstance().get_file("myfile.hdf")->get_group("/SimulationResults/NONO/Hello/Checkit-out");
pGroup->create_dataset("d1", HDF5DataSet2DStdSettings(4) );
pGroup->get_dataset("d1");

cout << "\n     **** FINISHED OK **** \n";
}




