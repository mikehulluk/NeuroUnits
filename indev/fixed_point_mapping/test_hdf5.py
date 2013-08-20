



from hdfjive import HDF5SimulationResultFile
results = HDF5SimulationResultFile("output.hd5")

r = results.filter("ALL{i_nmda}")
print r
