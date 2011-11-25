from units_core import Unit

multipliers = (
       ( 'giga','G', 9) ),
       ( 'mega','M', 6) ),
       ( 'kilo','k', 3) ),
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

       )

special_unit_abbrs = ( 
        ( 'm', Unit(meter=1)  ),

            )
