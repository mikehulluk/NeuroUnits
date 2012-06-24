


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


