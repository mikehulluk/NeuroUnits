
#include <boost/python.hpp>
#include "neurounits/neurounits.h"



class MyCPPException //: public std::exception
{
public:
    const char* what() const
    {
        return "AHHHHGHH!";
    }

};


namespace bp = boost::python;

PyObject *exceptionType=NULL; // will be initialised inside BOOST_PYTHON_MODULE(...) using createExceptionClass(...)

void translator(const MyCPPException &x) {

	bp::object exc(x);

	bp::object exc_t(bp::handle<>(bp::borrowed(exceptionType)));
	exc_t.attr("cause") = exc;

	PyErr_SetString(exceptionType, x.what());
}



PyObject* createExceptionClass(const char* name, PyObject* baseTypeObj =
PyExc_Exception)
{
    //char*
     PyObject* typeObj = PyErr_NewException( (char*) name, baseTypeObj, 0);
     if(!typeObj)
     {
        bp::throw_error_already_set();
     }

     //bp::scope().attr(name) = bp::handle<>(bp::borrowed(typeObj));
     return typeObj;
}



void throw_exception()
{
    throw MyCPPException();
}












BOOST_PYTHON_MODULE(fplib)
{
    using namespace boost::python;
    //def("greet", greet);


    typedef mh::FixedFloatConversion<24> FixedFloatConversion24;
    def("to_float24", FixedFloatConversion24::to_float);
    def("from_float24", FixedFloatConversion24::from_float);


    typedef LookUpTableExpPower2<24, SafeInt32> LUTExp24;
    class_<LUTExp24>( "LUTExp24", init<int, int>() )
                .def("get", &LUTExp24::get)
                ;

     bp::register_exception_translator<MyCPPException>(translator);
     bp::class_<MyCPPException>("MyCPPException")
         .def("what", &MyCPPException::what);
     exceptionType = createExceptionClass("fplib.MyCPPExceptionType");



    def("throw_exception", throw_exception);

}
