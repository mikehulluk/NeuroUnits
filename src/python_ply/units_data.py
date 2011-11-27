from units_core import Unit, Quantity

multipliers = (
       ( 'giga','G', 9) ,
       ( 'mega','M', 6) ,
       ( 'kilo','k', 3) ,
       ( 'centi','c', -2) ,
       ( 'milli','m', -3) ,
       ( 'micro','u', -6) ,
       ( 'nano','n', -9) ,
       ( 'pico','p', -12) ,
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
    'e_charge': Quantity(),
    
    'Na_e': 'Avagadro', 
    'Boltzmann',
    'Faraday', 
    'R':'Gas Constant',


        }
