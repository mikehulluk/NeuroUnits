

class UnitError(ValueError):
    pass

class Unit(object):
    Bases = """meter kilogram second ampere kelvin mole candela """.split()
    BasesShort = """m kg s A K mol cd""".split()
    
    def __init__(self, meter=0, kilogram=0, second=0, ampere=0, kelvin=0 , mole=0, candela=0, powerTen =0):
        self.meter = meter
        self.kilogram = kilogram
        self.second = second
        self.ampere = ampere
        self.kelvin = kelvin
        self.mole = mole
        self.candela = candela
        self.powerTen = powerTen


    def __mul__(self, rhs):

        return Unit(
            meter = self.meter + rhs.meter,
            kilogram = self.kilogram + rhs.kilogram,
            second = self.second + rhs.second,
            ampere = self.ampere + rhs.ampere,
            kelvin = self.kelvin + rhs.kelvin,
            mole = self.mole + rhs.mole,
            candela = self.candela + rhs.candela,
            powerTen = self.powerTen +rhs.powerTen,
        )

    def __div__(self, rhs):

        return Unit(
            meter = self.meter - rhs.meter,
            kilogram = self.kilogram - rhs.kilogram,
            second = self.second - rhs.second,
            ampere = self.ampere - rhs.ampere,
            kelvin = self.kelvin - rhs.kelvin,
            mole = self.mole - rhs.mole,
            candela = self.candela - rhs.candela,
            powerTen = self.powerTen -rhs.powerTen,
        )

    def raise_to_power(self, p):
        return Unit(
            meter = self.meter *p,
            kilogram = self.kilogram *p ,
            second = self.second *p,
            ampere = self.ampere *p ,
            kelvin = self.kelvin *p,
            mole = self.mole *p ,
            candela = self.candela *p ,
            powerTen = self.powerTen *p,
        )


    def __str__(self,):
        s1 = "(10e%d)" % self.powerTen

        basis_short_LUT = dict ( zip( Unit.Bases, Unit.BasesShort) )
        basisCounts = dict( [ (b, getattr(self, b)) for  b in Unit.Bases ] ) 
        terms = [ "%s %d"%(basis_short_LUT[b], basisCounts[b]) for b in Unit.Bases if basisCounts[b] ] 
        s2 = ' '.join(terms)
        return "<Unit: " + s1 + " " + s2 + ">"

class Quantity(object):
    def __init__(self, magnitude, unit):
        self.magnitude = magnitude
        self.unit = unit

    def __str__(self):
        return '<Quantity: %s %s>'%(self.magnitude , self.unit)

    def __eq__(self, rhs):
        lhs_mag =self.magnitude * 10**self.unit.powerTen  
        rhs_mag = rhs.magnitude * 10** rhs.unit.powerTen  
        return  (lhs_mag== rhs_mag) and \
                (self.unit.meter == rhs.unit.meter) and \
                (self.unit.kilogram == rhs.unit.kilogram) and \
                (self.unit.second == rhs.unit.second) and \
                (self.unit.ampere == rhs.unit.ampere) and \
                (self.unit.kelvin == rhs.unit.kelvin) and \
                (self.unit.mole  == rhs.unit.mole) and \
                (self.unit.candela == rhs.unit.candela)

