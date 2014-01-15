import pyneurounits

try:
    pyneurounits.throw_exception()
except pyneurounits.MyCPPException:
    print 'Exception Caught!'
