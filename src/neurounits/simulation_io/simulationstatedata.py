
class SimulationStateData(object):
    def __init__(self,
            parameters,
            suppliedvalues,
            assignedvalues,
            states_in,
            states_out,
            rt_regimes,
            event_manager,
            ):
        self.parameters = parameters
        self.assignedvalues = assignedvalues
        self.suppliedvalues = suppliedvalues
        self.states_in = states_in
        self.states_out = states_out
        self.rt_regimes = rt_regimes
        self.event_manager = event_manager

    def clear_states_out(self):
        self.states_out = {}

    def copy(self):
        return SimulationStateData(parameters=self.parameters.copy(),
                                   suppliedvalues=self.suppliedvalues.copy(),
                                   assignedvalues=self.assignedvalues.copy(),
                                   states_in=self.states_in.copy(),
                                   states_out=self.states_out.copy(),
                                   rt_regimes=self.rt_regimes.copy(),
                                   event_manager = None
                                   )
