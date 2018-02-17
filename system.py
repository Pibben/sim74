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

        self.inputs = []
        self.outputs = []

    def set_output(self, pin_name):
        self.parts[pin_name].set_direction(Pin.INPUT)
        self.outputs.append(self.parts[pin_name])

    def set_input(self, pin_name):
        self.parts[pin_name].set_direction(Pin.OUTPUT)
        self.inputs.append(self.parts[pin_name])

    def set_high(self, part_name, pin_name):
        self.parts[part_name].get_pin(pin_name).setDefaultValue(1)

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

        for o in self.outputs:
            print("%s: %d" % (o.name, o.get_number()))

    def sanity_check(self):
        for part in self.parts.values():
            part.sanity_check()
