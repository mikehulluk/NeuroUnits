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


#assert False
#
#from neurounits import ast
#from units_data_unitterms import UnitTermData
#
#
#class StdLibrary(object):
#
#    @classmethod
#    def getMath(cls, backend):
#
#        consts = {
#          'pi':           backend.Quantity(3.141592653,   backend.Unit() ),
#          'e_euler':      backend.Quantity(2.718281828,   backend.Unit() ),
#        }
#        constants = dict( [ (sym, ast.SymbolicConstant(symbol=sym, value=val) ) for (sym,val) in consts.iteritems()] )
#
#        functiondefs ={
#            'exp' : ast.BuiltInFunction(funcname='exp',
#                                        parameters={'x':ast.FunctionDefParameter(symbol='x', dimension=backend.Unit() ) },
#                                        dimension=backend.Unit() ),
#            }
#
#        return ast.Library('std.math', constants=constants, functiondefs=functiondefs)
#
#    @classmethod
#    def getPhysics(cls, backend):
#
#        uL = UnitTermData.getUnitLUT(backend)
#        consts = {
#                   'F':         backend.Quantity(96485.3365,    uL['coulomb']/uL["mole"] ),
#                   'R':         backend.Quantity(8.3144621,     uL['joule']/(uL["mole"]*uL['kelvin'] ) ),
#                   'Na':        backend.Quantity(6.02214129e23, backend.Unit(mole=-1) ),
#                   'k':         backend.Quantity(1.380648e-23,  uL['joule']/uL["kelvin"] ),
#                   'e_charge':  backend.Quantity(1.602176565,   uL['coulomb']   ),
#                   }
#        constants = dict( [ (sym, ast.SymbolicConstant(symbol=sym, value=val) ) for (sym,val) in consts.iteritems()] )
#
#        return ast.Library('std.physics', constants = constants, functiondefs={} )
#
#
#
#    @classmethod
#    def get_default(cls, backend):
#        return []
#
#
