

f = open( 'testing_data.txt' )


modes = ['VALID UNIT',
         'INVALID UNIT', 
         'VALID QUANTITY',
         'INVALID QUANTITY', 
         'VALID UNIT CONVERSION' 
         ]



mode = modes[0]

data_catagories = dict( (m,[]) for m in modes ) 

for line in f:
    line = line.strip()
    if not line:
        continue

    # Change Mode?
    if line.startswith('#'):
        mode = line[1:].strip()
    # Store the line
    else:
        data_catagories[mode].append( line )



from units_wrapper import ParseUnitString
from units_core import UnitError

# Check the VALID UNITS:
for l in data_catagories['VALID UNIT']:
    print l,
    p = ParseUnitString(l)
    print '->', p



# Check the INVALID UNITS:
for l in data_catagories['INVALID UNIT']:

    try:
        print 'CHECKING:', l
        ParseUnitString(l)
    except UnitError as e:
        print 'Check INVALID OK'
        continue
    
    assert False, 'Invalid unit not flagged as invalid: %s'%l

    
# Check Valid Conversions:
for l in data_catagories['VALID UNIT CONVERSION']:
    
    print l
    lhs, rhs = l.split('=')
    l = ParseUnitString(lhs.strip())
    r = ParseUnitString(rhs.strip())
    print l,r
    assert l==r


