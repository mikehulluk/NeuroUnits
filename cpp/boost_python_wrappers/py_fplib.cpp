
#include <boost/python.hpp>
#include "float_utils.h"

char const* greet()
{
   return "hello, world";
}




BOOST_PYTHON_MODULE(fplib)
{
    using namespace boost::python;
    def("greet", greet);
}
