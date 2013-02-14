


import json
import neurounits
import copy




class NutsIO(object):

    @classmethod
    def load(cls, filename):
        options = NutsOptions()
        nuts_lines = []
        with open(filename) as f:
            for lineno,line in enumerate(f.readlines()):
                line = line.strip()
                if not line:
                    continue
                elif line.startswith('#@'):
                    options = copy.deepcopy(options)
                    options.update(line[2:])
                elif line.startswith('#'):
                    pass
                else:
                    nuts_lines.append( NutsIOLine(line=line, lineno=lineno, options=options) )
        return nuts_lines

    @classmethod
    def validate(cls, filename):
        print 'Checking nuts files', filename
        nuts_lines = cls.load(filename)

        for ln in nuts_lines:
            print ln.validate()
        print len(nuts_lines)








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
    return u1==u2

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




class NutsIOLine(object):
    def __init__(self, line, lineno, options):
        self.line = line
        self.lineno = lineno
        self.options=options


    def validate(self,):
        parse_func = parse_func_lut[self.options.type]
        comp_func = comp_func_lut[self.options.type]

        print 'Checking', self.line.ljust(30),

        if '==' in self.line:
            toks = self.line.split('==')
            are_equal = True

            for t in toks[1:]:
                are_equal_comp = comp_func(
                        parse_func(toks[0]),
                        parse_func(t)
                        )
                are_equal = are_equal and are_equal_comp
            print are_equal
        else:
            assert False










