
#include <boost/python.hpp>
#include "float_utils.h"


#include <lut.h>

char const* greet()
{
   return "hello, world";
}




BOOST_PYTHON_MODULE(fplib)
{
    using namespace boost::python;
    def("greet", greet);
    
    
    //typedef LookUpTableExpPower2<24> LUTExp24;
    typedef mh::FixedFloatConversion<24> FixedFloatConversion24;
    def("to_float24", FixedFloatConversion24::to_float);
    def("from_float24", FixedFloatConversion24::from_float);
    
    
    
    
    typedef LookUpTableExpPower2<24> LUTExp24;
    class_<LUTExp24>( "LUTExp24", init<int, int>() )
		.def("get", &LUTExp24::get)
		;
		
		//.int get(int x, int up_x, int up_out)
    
}
