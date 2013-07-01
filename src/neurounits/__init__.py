#!/usr/bin/python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------
# Copyright (c) 2012 Michael Hull.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# -------------------------------------------------------------------------------




"""
Intended for client
=====================


Parsing
-------

.. autosummary::
   :toctree: DIRNAME

   NeuroUnitParser
   MQ1

.. _autoclass:: NeuroUnitParser

Simulation & Code Generation
-----------------------------



Visitors
---------


NUTS files
-----------




Intended for internal
======================




"""

# Add 'straight.plugin' into the python path

try:
    import straight.plugin

except ImportError:
    import sys, os
    localdir = os.path.dirname( __file__ )
    ext_deps_dir = os.path.abspath( os.path.join( localdir, '../../ext_deps/') )
    print ext_deps_dir
    sys.path.append(os.path.join(ext_deps_dir, 'straight.plugin/') )

    import straight.plugin



# Standard imports:

from neurounits.neurounitparser import NeuroUnitParser, MQ1
from neurounits.neurounitparser import NeuroUnitParserOptions
from neurounits.unit_expr_parsing.units_expr_yacc import ParseTypes

from neurounits.nuts_io import NutsIO
from neurounits.locations import Locations

from neurounits.ast import NineMLComponent

Q1 = lambda o: NeuroUnitParser.QuantitySimple(o).as_quantities_quantity()
Q2 = lambda o: NeuroUnitParser.QuantityExpr(o).as_quantities_quantity()

