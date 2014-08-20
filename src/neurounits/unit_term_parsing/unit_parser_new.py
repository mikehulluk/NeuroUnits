

from ..unit_errors import UnitError#, InvalidUnitTermError

import numpy as np

class UnitTermParser(object):
    def __init__(self, backend, ):
        self.backend=backend

        self.LUT = {}
        
        self._short_power_of_ten_prefixes = {}
        self._long_power_of_ten_prefixes = {}
        self._shortforms = {}
        self._longforms = {}
        self._add_default_basic_units()



    def _add_default_basic_units(self,):
        self._shortforms['m'] = lambda backend: backend.Unit(meter=1)
        self._shortforms['g'] = lambda backend: backend.Unit(kilogram=1, powerTen=-3)
        self._shortforms['s'] = lambda backend: backend.Unit(second=1)
        self._shortforms['A'] = lambda backend: backend.Unit(ampere=1)
        self._shortforms['K'] = lambda backend: backend.Unit(kelvin=1)
        self._shortforms['mol']=  lambda backend: backend.Unit(mole=1)
        self._shortforms['cd'] = lambda backend: backend.Unit(candela=1)

        self._longforms['meter'] =  lambda backend: backend.Unit(meter=1)
        self._longforms['gram'] =   lambda backend: backend.Unit(kilogram=1, powerTen=-3)
        self._longforms['second'] = lambda backend: backend.Unit(second=1)
        self._longforms['amp'] =    lambda backend: backend.Unit(ampere=1)
        self._longforms['kelvin'] = lambda backend: backend.Unit(kelvin=1)
        self._longforms['mole']=    lambda backend: backend.Unit(mole=1)
        self._longforms['candela'] = lambda backend: backend.Unit(candela=1)

    def parse(self, unitterm):
        unitterm = unitterm.strip()
        # Lets cache the lookup result:
        if not unitterm in self.LUT:
            self.LUT[unitterm] = self._resolve_unitterm(unitterm)

        return self.LUT[unitterm](self.backend)


    def _resolve_unitterm(self, unitterm):
        #from ..unit_errors import UnitError

        lf = self._try_find_longform(unitterm)
        sf = self._try_find_shortform(unitterm)
    
        if lf and sf:
            raise UnitError('Unable to decipher %s (Can be interpretted as long and shortforms!)' % unitterm)
        if not lf and not sf:
            raise UnitError('Unable to decipher %s (No forms!)' % unitterm)

        if lf:
            return lf
        else:
            return sf


    def _try_find_longform(self, unitterm):
        return self._try_find_form(
                unitterm=unitterm,
                prefix_dict=self._long_power_of_ten_prefixes,
                units_dict=self._longforms)

    def _try_find_shortform(self, unitterm):
        return self._try_find_form(
                unitterm=unitterm,
                prefix_dict=self._short_power_of_ten_prefixes,
                units_dict=self._shortforms)

    def _try_find_form(self, unitterm, prefix_dict, units_dict):
        print 'units_dict:', units_dict
        # Simple case, its an unprefixed type
        if unitterm in units_dict:
            return units_dict[unitterm]

        # Make a list of potential suffixes:
        potential_suffixes = []
        for u,uv in units_dict.items():
            if unitterm.endswith(u):
                potential_suffixes.append( (unitterm[:len(unitterm)-len(u)], u,uv) )
        if not potential_suffixes:
            return 


        potential_units = []
        for prefix, suffix, suffix_functor in potential_suffixes:
            print 'Prefix:', prefix
            if not prefix in prefix_dict:
                continue
            potential_units.append((prefix_dict[prefix], suffix_functor ))

        if len(potential_units) == 0:
            return None
        if len(potential_units) > 1:
            raise UnitError("...")
        else:
            prefix_func, suffix_func = potential_units[0]
            return lambda backend: prefix_func(backend) * suffix_func(backend)


    def add_unit_def(self, longforms, shortforms, equivalent_dim):
        thevars=(longforms, shortforms, equivalent_dim)
        print 'Adding new unit definition:', thevars
        e = equivalent_dim
        pot = 0
        if equivalent_dim.float_in_si() != 1.0:
            pot = int( np.log10(equivalent_dim.float_in_si())) 
            assert equivalent_dim.float_in_si() / 10**pot == 1.0

        func = lambda backend : backend.Unit(
                meter=e.unit.meter,
                kilogram = e.unit.kilogram,
                second = e.unit.second,
                ampere = e.unit.ampere,
                kelvin = e.unit.kelvin,
                mole  = e.unit.mole,
                candela = e.unit.candela,
                powerTen=pot)

        for l in longforms:
            assert not l in self._longforms
            self._longforms[l] = func
        for l in shortforms:
            assert not l in self._shortforms
            self._shortforms[l] = func


    def add_unitprefix_def(self, longforms, shortforms, pot):
        #thevars = (longforms, shortforms, pot)
        #print 'Adding new unit definition:', thevars

        for l in longforms:
            assert not l in self._long_power_of_ten_prefixes
            self._long_power_of_ten_prefixes[l] = lambda backend: backend.Unit(powerTen=pot)
        for l in shortforms:
            print l
            assert not l in self._short_power_of_ten_prefixes
            self._short_power_of_ten_prefixes[l] = lambda backend: backend.Unit(powerTen=pot)


