from toposort import toposort_flatten

from core import Pin


class System(object):
    def __init__(self, parts, nets=None):
        self.parts = parts

        if nets:
            self.nets = nets
        else:
            set_of_all_pins = sum((part.get_all_pins() for part in parts.values()), [])
            self.nets = list({p.net for p in set_of_all_pins if p.net})

        assert self.nets

    def run(self):
        total_dags = {}

        for p in self.parts.values():
            total_dags.update(p.get_dags())

        for n in self.nets:
            total_dags.update(n.get_dag())

        order = toposort_flatten(total_dags, sort=False)
        order.reverse()

        for s in order:
            if s.direction == Pin.OUTPUT and s.gate:
                s.gate.update()


    def sanity_check(self):
        for part in self.parts.values():
            part.sanity_check()
