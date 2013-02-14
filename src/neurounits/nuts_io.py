
class NutsIO(object):

    @classmethod
    def load(cls, filename):
        _check_nuts_file(filename)




import json



class NutsOptions():
    valid_attrs = {
        'type': None,
        'test-gnu-unit':True,
        'eps':0.01
        }

    def __init__(self):
        for k,v in NutsOptions.valid_attrs.items():
            setattr(self,k,v)

    def update(self, line):
        #print 'Updating options:', line
        line = line.replace("'",'"')
        new_options = json.loads(line)
        for k,v in new_options.items():
            assert k in NutsOptions.valid_attrs, 'Invalid option: %s'%k
            setattr(self,k,v)



def compare_l1(u1,u2):
    return u1==u2

def compare_l2(u1,u2):
    return u1==u2

def compare_l3(u1,u2):
    #print 'Comparing:', u1,u2
    #print '==', u1,u2,u1==u2
    #print '-', u1-u2
    return u1==u2

import neurounits
parse_func_lut = {
        'L1':neurounits.NeuroUnitParser.Unit,
        'L2':neurounits.NeuroUnitParser.QuantitySimple,
        'L3':neurounits.NeuroUnitParser.QuantityExpr,
        }

comp_func_lut = {
        'L1': compare_l1,
        'L2': compare_l2,
        'L3': compare_l3,
        }


def check_line(line, options):

    parse_func = parse_func_lut[options.type]
    comp_func = comp_func_lut[options.type]

    print 'Checking', line.ljust(30),

    if '==' in line:
        toks = line.split('==')
        are_equal = True

        #for t in toks:
        #    print 'Parsing:',t
        #    parse_func(t)


        for t in toks[1:]:
            are_equal_comp = comp_func(
                    parse_func(toks[0]),
                    parse_func(t)
                    )
            are_equal = are_equal and are_equal_comp
        print are_equal






def _check_nuts_file(filename):
    print 'Checking nuts files', filename

    options = NutsOptions()

    with open(filename) as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            elif line.startswith('#@'):
                options.update(line[2:])
            elif line.startswith('#'):
                pass
            else:
                check_line(line,options)



