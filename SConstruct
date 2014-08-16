import sys
import os

def python_tool(env):
    pybase = 'python%s' % sys.version[0:3]
    env.Append(CPPPATH=[os.path.join(sys.prefix, 'include', pybase)],
               LIBPATH=[os.path.join(sys.prefix, 'lib', pybase, 'config')],
               LIBS=['lib%s' % pybase])
    if env['PLATFORM'] not in ['cygwin', 'win32']:
        env.Append(LIBS=['util'])

def boost_python_tool(env):
    env.Append(CPPDEFINES=['BOOST_PYTHON_STATIC_LIB',
                           'BOOST_PYTHON_STATIC_MODULE'],
               CPPPATH=['$boostIncludes'],  # boostIncludes is a PathOption
               LIBS=['boost_python'])

               





env = Environment(
	CCFLAGS = " -std=c++0x -Werror -Wall -Wno-unused-variable -Wno-unused-local-typedefs -I/usr/include/python2.7  -lpython2.7 -lboost_python -p -g -Wfatal-errors -Werror -Wno-unused-but-set-variable -Wno-write-strings " ,
	CPPPATH = ['include/'],
	tools=['default', python_tool, boost_python_tool]
	)

#conf = Configure(env)
#if not conf.CheckCHeader('boost/python.hpp'):
#        print 'boost/python.hpp must be installed!'
#        Exit(1)





# CPP libraries:
foo = SConscript('cpp/SConscript', exports='env')
