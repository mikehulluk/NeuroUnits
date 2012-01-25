
import quantities as pq

#def check_unit_dimensionless(u1):
#    assert u1.rescale("")

def unit_as_dimensionless(u1):
    assert u1.rescale("")
    return float(u1.rescale("").magnitude)

def make_unit(meter=0,kilogram=0,second=0,ampere=0,kelvin=0,mole=0,candela=0, powerTen=0):
    pTenDict = {    -12:    pq.pico,
                    -9:     pq.nano,
                    -6:     pq.micro,
                    -3:     pq.milli,
                    -2:     pq.centi,
                     0:     pq.dimensionless,
                     3:     pq.kilo,
                     6:     pq.mega,
                     9:     pq.giga,
                     12:     pq.tera, }
    pTen = pTenDict[powerTen]

    types = [ 
              (meter,pq.m) ,
              (kilogram,pq.kg) ,
              (second,pq.s) ,
              (ampere,pq.A) ,
              (kelvin,pq.K) ,
              (mole,pq.mole) ,
              (candela,pq.candela) ,
            ]
    o = pTen
    for i,j in types:
        if i != 0:
            o = o * j**i
    return o
    
    #return pq.m ** meter * \
    #       pq.kg ** kilogram * \
    #       pq.s ** second * \
    #       pq.A ** ampere * \
    #       pq.K ** kelvin * \
    #       pq.mole ** mole * \
    #       pq.candela ** candela * \
    #       pTen

    #pass

def make_quantity(magnitude, unit):
    return magnitude * unit
