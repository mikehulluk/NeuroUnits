
import neurounits

txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ).read()
library_manager = neurounits.NeuroUnitParser.Parse9MLFile(txt)



print library_manager.components

for comp in library_manager.components:
	print comp
