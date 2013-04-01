
import neurounits
import inspect


txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/simple_components.9ml" ).read()
txt = open( "/home/michael/hw_to_come/libs/NeuroUnits/src/test_data/l4-9ml/complex_component.9ml" ).read()
library_manager = neurounits.NeuroUnitParser.Parse9MLFile(txt)



print library_manager.components



def summarise_component(comp):
    print comp
    for k,v in comp.__dict__.items():
        if k[0] == '_':
            #continue
            pass
        print '  ', k,v
    print comp.__dict__
    
    params = inspect.getmembers(comp)
    for k in params:
        if k[0][0] == '_':
            continue
        try:
            print '  ', k
        except:
            pass
            
    for tr in comp.transitions:
        print tr
        for a in tr.actions:
            
            print ' ', a
    
for comp in library_manager.components:
    print
    summarise_component(comp)
    
	
