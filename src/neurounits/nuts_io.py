


import json
import neurounits
import copy
import math



class NutsIOValidationError(Exception):
    pass

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
            print 'Validating:', ln.line
            res = ln.validate()
            if not res:
                raise NutsIOValidationError('NUTS Validation failed: %s' % ln.line)

        print len(nuts_lines)







default_eps = 1.e-14

class NutsOptions():
    valid_attrs = {
        'type': None,
        'test-gnu-unit':True,
        'eps': default_eps
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









def compare_l1A(u1,u2, eps=None):
    return u1==u2
    #eps = eps if eps is not None else default_eps
    #return math.fabs( float(u1-u2) ) < eps
    #return u1==u2

def compare_l1B(u1,u2, eps=None):
    eps = eps if eps is not None else default_eps
    return math.fabs( (u1-u2).float_in_si() ) < eps

def compare_l2(u1,u2, eps=None):
    eps = eps if eps is not None else default_eps
    return math.fabs( (u1-u2).float_in_si() ) < eps

parse_func_lut = {
        'L1A':neurounits.NeuroUnitParser.Unit,
        'L1B':neurounits.NeuroUnitParser.QuantitySimple,
        'L2':neurounits.NeuroUnitParser.QuantityExpr,
        }

comp_func_lut = {
        'L1A': compare_l1A,
        'L1B': compare_l1B,
        'L2': compare_l2,
        }




class NutsIOLine(object):
    def __init__(self, line, lineno, options):

        line = line.strip()

        if line.startswith('!!'):
            self.line = line[2:]
            self.is_valid=False
        else:
            self.line = line
            self.is_valid=True
        self.lineno = lineno
        self.options=options


    def validate(self,):

        if self.is_valid:
            return self.test_valid()
        else:
            return self.test_invalid()


    def test_valid(self):
        parse_func = parse_func_lut[self.options.type]
        comp_func = comp_func_lut[self.options.type]
        if '==' in self.line:
            toks = self.line.split('==')

            for t in toks[1:]:
                print ' -- Checking: %s == %s' % tuple([toks[0],t])
                print self.options.__dict__
                are_equal = comp_func(
                        parse_func(toks[0]),
                        parse_func(t),
                        eps = self.options.eps
                        )
                if not are_equal:
                    return False
            return True

        if '!=' in self.line:
            toks = self.line.split('!=')
            assert len(toks) == 2
            print ' -- Checking: %s != %s' % tuple(toks)
            are_equal = comp_func(
                    parse_func(toks[0]),
                    parse_func(toks[1])
                    )
            if are_equal: 
                return False
            return True



        else:
            raise NotImplementedError()


    def test_invalid(self):
        parse_func = parse_func_lut[self.options.type]
        comp_func = comp_func_lut[self.options.type]
        for tok in self.line.split(','):
            try:
                print ' -- Checking: %s is invalid' % tok
                parse_func(tok)
                # An exception should be raised, so we shouldn't get here:!
                return False
            except Exception, e:
                print ' -- Exception raised (OK)!', e
                pass
        return True









