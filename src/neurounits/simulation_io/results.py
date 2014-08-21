
import pylab
from collections import defaultdict
import itertools


def _auto_plot(res):


    si_base_units = defaultdict(list)
    plot_objs = sorted(list(itertools.chain(res.state_variables.keys(), res.assignments.keys(),)))
    for plt_obj in plot_objs:
        print plt_obj
        terminal_obj = res.component.get_terminal_obj(plt_obj)
        dimension = terminal_obj.get_dimension()

        found = False
        for k,v in si_base_units.items():
            if k.is_compatible(dimension):
                si_base_units[k].append(plt_obj)
                found = True
                break
        if not found:
            si_base_units[ dimension.with_no_powerten()].append(plt_obj)



    print si_base_units
    print len(si_base_units)
    n_axes = len(si_base_units)

    f = pylab.figure()
    axes = [f.add_subplot(n_axes, 1, i+1) for i in range(n_axes)]


    for ((unit,objs), ax) in zip(sorted(si_base_units.items()), axes):
        ax.set_ylabel(str(unit))
        ax.margins(0.1)
        for o in sorted(objs):
            ax.plot(res.get_time(), res.get_data(o), label=o)
        ax.legend()








class SimulationResultsData(object):
    def __init__(self, times, state_variables, assignments, transitions, rt_regimes, events, component):
        self.times = times
        self.state_variables = state_variables
        self.assignments = assignments
        self.transitions = transitions
        self.rt_regimes = rt_regimes

        self.events = events
        self.component = component

    def get_time(self):
        return self.times


    def get_data(self, name):
        assert isinstance(name, basestring)
        if name in self.state_variables:
            return self.state_variables[name]
        elif name in self.assignments:
            return self.assignments[name]
        else:
            assert False, 'Could not find: %s' % name

    def auto_plot(self):
        _auto_plot(self)