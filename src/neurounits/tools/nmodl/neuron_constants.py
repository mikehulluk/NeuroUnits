#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------


class MechanismType:
    Point = "Point"
    Distributed = "Distributed"

class NeuronSuppliedValues:
    Time = "Time"
    MembraneVoltage = "MembraneVoltage"
    Temperature = "Temperature"
    All = [ Time, MembraneVoltage, Temperature ]


class NEURONMappings():
    from neurounits import NeuroUnitParser
    current_units = {
            MechanismType.Distributed: NeuroUnitParser.Unit("mA/cm2"),
            MechanismType.Point: NeuroUnitParser.Unit("nA"),
            }

    supplied_value_names = {
                NeuronSuppliedValues.MembraneVoltage : 'v',
                NeuronSuppliedValues.Time: 't',
                NeuronSuppliedValues.Temperature: 'celsius'
    }

    supplied_value_units= {
                NeuronSuppliedValues.MembraneVoltage : NeuroUnitParser.Unit("mV"),
                NeuronSuppliedValues.Time: NeuroUnitParser.Unit("ms"),
                NeuronSuppliedValues.Temperature: NeuroUnitParser.Unit("K")
                }


