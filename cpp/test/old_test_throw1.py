#!/usr/bin/python
# -*- coding: utf-8 -*-

import pyneurounits

try:
    pyneurounits.throw_exception()
except pyneurounits.MyCPPException:
    print 'Exception Caught!'
