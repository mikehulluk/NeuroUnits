from units_core import Unit, Quantity

multipliers = (
       ( 'giga','G',  Unit(powerTen=9)  ),
       ( 'mega','M',  Unit(powerTen=6)  ),
       ( 'kilo','k',  Unit(powerTen=3)  ),
       ( 'centi','c', Unit(powerTen=-2) ) ,
       ( 'milli','m', Unit(powerTen=-3) ) ,
       ( 'micro','u', Unit(powerTen=-6) ) ,
       ( 'nano','n',  Unit(powerTen=-9) ) ,
       ( 'pico','p',  Unit(powerTen=-12)) ,
        )

units = (
       ( 'meter','m', Unit(meter=1) ),
       ( 'gram','g', Unit(kilogram=1,powerTen=-3) ),
       ( 'second','s', Unit(second=1) ),
       ( 'amp','A', Unit(ampere=1) ),
       ( 'kelvin','K', Unit(kelvin=1) ),
       ( 'mole','mol', Unit(mole=1) ),
       ( 'candela','cd', Unit(candela=1) ),

       ( 'volt','V', Unit(meter=2, kilogram=1,second=-3,ampere=-1) ),
       ( 'siemen','S', Unit(meter=-2, kilogram=-1,second=3,ampere=2) ),
       ( 'farad','F', Unit(meter=-2, kilogram=-1,second=4,ampere=2) ),
       ( 'ohm','Ohm', Unit(meter=2, kilogram=1,second=-3,ampere=-2) ),
       ( 'coulomb','C', Unit(second=1,ampere=1) ),
       
       ( 'watt','W', Unit() ),
       ( 'joule','J', Unit() ),
       ( 'newton','N', Unit() ),
       ( 'liter','l', Unit() ),
       
)


unit_long_LUT = dict([(u[0],u[2]) for u in units] ) 
unit_short_LUT = dict([(u[1],u[2]) for u in units] ) 
unit_LUT = safe_merge(unit_long_LUT, unit_short_LUT)



special_unit_abbrs = ( 
        ( 'm', Unit(meter=1)  ),
        ( 'cm', Unit(meter=1, powerTen=-2)  ),
        ( 'mm', Unit(meter=1, powerTen=-3)  ),
        ( 'um', Unit(meter=1, powerTen=-6)  ),
        ( 'nm', Unit(meter=1, powerTen=-9)  ),
        ( 'pm', Unit(meter=1, powerTen=-12)  ),
            )



constants = {
    'pi': Quantity(3.141, Unit() ),
    'e_base':  Quantity(2.7,   Unit() ),
    #'e_charge': Quantity(),
    #
    #'Na_e': 'Avagadro', 
    #'Boltzmann',
    #'Faraday', 
    #'R':'Gas Constant',


        }
