#-------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#  - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
from bases import ParsingBackendBase
from neurounits.unit_errors import UnitMismatchError


class MHUnitBackend(ParsingBackendBase):
    @classmethod
    def Quantity(cls, magnitude, unit):
        return MMQuantity(magnitude=magnitude, unit=unit)

    @classmethod
    def Unit(cls, meter=0,kilogram=0,second=0,ampere=0,kelvin=0,mole=0,candela=0, powerTen=0):
        return MMUnit(meter=meter, 
                kilogram=kilogram,
                second=second,
                ampere=ampere,
                kelvin=kelvin,
                mole=mole,
                candela=candela,
                powerTen=powerTen)




class MMUnit(object):
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
        assert isinstance( rhs, MMUnit)

        return MMUnit(
            meter = self.meter + rhs.meter,
            kilogram = self.kilogram + rhs.kilogram,
            second = self.second + rhs.second,
            ampere = self.ampere + rhs.ampere,
            kelvin = self.kelvin + rhs.kelvin,
            mole = self.mole + rhs.mole,
            candela = self.candela + rhs.candela,
            powerTen = self.powerTen + rhs.powerTen,
        )

    def __div__(self, rhs):
        if not isinstance( rhs, MMUnit):
            raise ValueError("Can't divide by non-unit! %s"%type(rhs))
        assert isinstance( rhs, MMUnit)

        return MMUnit(
            meter = self.meter - rhs.meter,
            kilogram = self.kilogram - rhs.kilogram,
            second = self.second - rhs.second,
            ampere = self.ampere - rhs.ampere,
            kelvin = self.kelvin - rhs.kelvin,
            mole = self.mole - rhs.mole,
            candela = self.candela - rhs.candela,
            powerTen = self.powerTen - rhs.powerTen,
        )

    def __pow__(self, p):
        return self._raise_to_power(p)

    def _raise_to_power(self, p):
        return MMUnit(
            meter = self.meter * p,
            kilogram = self.kilogram * p ,
            second = self.second * p,
            ampere = self.ampere * p ,
            kelvin = self.kelvin * p,
            mole = self.mole * p ,
            candela = self.candela * p ,
            powerTen = self.powerTen * p,
        )




    def detail_str(self,):
        s1 = "(10e%d)" % self.powerTen

        basis_short_LUT = dict ( zip( MMUnit.Bases, MMUnit.BasesShort) )
        basisCounts = dict( [ (b, getattr(self, b)) for  b in MMUnit.Bases ] ) 
        terms = [ "%s %d"%(basis_short_LUT[b], basisCounts[b]) for b in MMUnit.Bases if basisCounts[b] ] 
        s2 = ' '.join(terms)
        return "%s %s"%(s1,s2)
    
    
    def __str__(self):
        return "<MMUnit: " + self.detail_str() + ">"



    def is_dimensionless(self, allow_non_zero_power_of_ten):
        
        dimensionless = ( self.meter==0 and self.kilogram==0 and self.second==0 and self.ampere==0 and self.kelvin==0 and self.mole == 0 and self.candela==0)
        if allow_non_zero_power_of_ten:
            return dimensionless
        else:
            return dimensionless and (self.powerTen == 0) 
        

    def check_compatible(self, u1):
        if not self.is_compatible(u1):
            raise UnitMismatchError(self, u1)
        

    def is_compatible(self, u1):
        u = self / u1
        return u.is_dimensionless(allow_non_zero_power_of_ten=True)

    def unit_to_si(self):
        return MMUnit(meter=self.meter, kilogram=self.kilogram, second=self.second, ampere=self.ampere,kelvin=self.kelvin,candela=self.candela) 


    def FormatLatex(self, inc_powerten=True):
        s1 = "(10e%d)" % self.powerTen if inc_powerten else ""

        basis_short_LUT = dict ( zip( MMUnit.Bases, MMUnit.BasesShort) )
        basisCounts = dict( [ (b, getattr(self, b)) for  b in MMUnit.Bases ] ) 
        terms = [ "%s^{%d}"%(basis_short_LUT[b], basisCounts[b]) for b in MMUnit.Bases if basisCounts[b] ] 
        s2 = '\cdot '.join(terms)
        return "%s %s"%(s1,s2)
        
    


    def as_quanitites_unit(self):
        import quantities as pq
        convs = ( ( self.meter, pq.m ),
                  ( self.kilogram, pq.kg ),
                  ( self.second, pq.s ),
                  
                  ( self.ampere, pq.ampere ),
                  ( self.kelvin, pq.kelvin ),
                  ( self.mole, pq.mole ),
                  ( self.candela, pq.candela ),
                 )
        res = pq.dimensionless
        for (n,u) in convs:
            if n==0:
                continue
            res = res * u**n
        return res * 10**self.powerTen
    
    



class MMQuantity(object):
    def __init__(self, magnitude, unit):
        self.magnitude = magnitude
        self.unit = unit

    def get_units(self):
        return self.unit
    units = property(get_units)

    def __str__(self):
        if self.unit.is_dimensionless(allow_non_zero_power_of_ten=False):
            dim=""
        else:
            dim= self.unit.detail_str()
        #return
        return '%s %s'%(self.magnitude , dim)
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

    def __mul__(self, rhs):
        if isinstance(rhs, MMUnit):
            rhs = MMQuantity(1.0,rhs)
        return MMQuantity( self.magnitude*rhs.magnitude,  self.unit*rhs.unit) 
    def __div__(self, rhs):
        if isinstance(rhs, MMUnit):
            rhs = MMQuantity(1.0,rhs)
        return MMQuantity( self.magnitude/rhs.magnitude,  self.unit/rhs.unit) 


    def __add__(self, rhs):
        if isinstance(rhs, MMUnit):
            rhs = MMQuantity(1.0,rhs)
        assert isinstance( rhs, MMQuantity)
        rhs_conv = rhs.rescale(self.unit)
        return MMQuantity( self.magnitude + rhs_conv.magnitude, self.unit)

    def __sub__(self, rhs):
        if isinstance(rhs, MMUnit):
            rhs = MMQuantity(1.0,rhs)
        assert isinstance( rhs, MMQuantity)
        rhs_conv = rhs.rescale(self.unit)
        return MMQuantity( self.magnitude - rhs_conv.magnitude, self.unit)
        
    def __pow__(self, rhs):
        assert type(rhs) == int
        return MMQuantity( self.magnitude**rhs, self.unit**rhs)



    def is_compatible(self,u):
        return  self.unit.meter == u.meter and self.unit.kilogram == u.kilogram and self.unit.second == u.second and self.unit.ampere == u.ampere and self.unit.kelvin == u.kelvin and self.unit.mole == u.mole and self.unit.candela == u.candela

    def check_compatible(self, u):
        assert self.is_compatible(u)

    def rescale(self, u):
        self.check_compatible(u)
        mul_fac = u.powerTen - self.unit.powerTen
        return MMQuantity( self.magnitude / 10**mul_fac,  u )

    def dimensionless( self, ):
        assert self.is_dimensionless(allow_non_zero_power_of_ten=True)
        return self.magnitude * 10**self.unit.powerTen

    def is_dimensionless(self,allow_non_zero_power_of_ten):
        return self.unit.is_dimensionless(allow_non_zero_power_of_ten=allow_non_zero_power_of_ten)





    



