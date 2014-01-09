/*
Copyright (c) 2014, Michael Hull
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/




#include <boost/python.hpp>
#include "neurounits/neurounits.h"



class MyCPPException //: public std::exception
{
public:
    const char* what() const {
        return "AHHHHGHH!";
    }

};


namespace bp = boost::python;

PyObject* exceptionType = NULL; // will be initialised inside BOOST_PYTHON_MODULE(...) using createExceptionClass(...)

void translator(const MyCPPException& x)
{

    bp::object exc(x);

    bp::object exc_t(bp::handle<> (bp::borrowed(exceptionType)));
    exc_t.attr("cause") = exc;

    PyErr_SetString(exceptionType, x.what());
}



PyObject* createExceptionClass(const char* name, PyObject* baseTypeObj = PyExc_Exception)
{
    //char*
    PyObject* typeObj = PyErr_NewException((char*) name, baseTypeObj, 0);
    if(!typeObj) {
        bp::throw_error_already_set();
    }

    return typeObj;
}



void throw_exception()
{
    throw MyCPPException();
}












BOOST_PYTHON_MODULE(fplib)
{
    using namespace boost::python;

    typedef mh::FixedFloatConversion<24> FixedFloatConversion24;
    def("n32_to_float24", FixedFloatConversion24::n32_to_float);
    def("n32_from_float24", FixedFloatConversion24::n32_from_float);
    def("s32_to_float24", FixedFloatConversion24::s32_to_float);
    def("s32_from_float24", FixedFloatConversion24::s32_from_float);



    typedef LookUpTableExpPower2<24, NativeInt32> LUTExp24;
    class_<LUTExp24>("LUTExp24", init<int, int>())
        .def("get", &LUTExp24::get)
    ;

    bp::register_exception_translator<MyCPPException>(translator);
    bp::class_<MyCPPException>("MyCPPException")
        .def("what", &MyCPPException::what);
    exceptionType = createExceptionClass("fplib.MyCPPExceptionType");



    def("throw_exception", throw_exception);

}
