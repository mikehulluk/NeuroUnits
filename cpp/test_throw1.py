import fplib

try:
    fplib.throw_exception()
except fplib.MyCPPException:
    print 'Exception Caught!'
