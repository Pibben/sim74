class Net(object):
    def __init__(self, name):
        self.terminals = []
        self.name = name
        self.positive_edge = False
        self.negative_edge = False
        self.value = None

    def __repr__(self):
        pins = [str("%s" % k) for k in self.terminals]
        return "%s (%d/%d)[%s]: %s" % (self.name, self.num_inputs(), self.num_outputs(), self.value, pins)

    def is_positive_edge(self):
        return self.positive_edge

    def is_negative_edge(self):
        return self.negative_edge

    def add_pin(self, pin):
        self.terminals.append(pin)
        pin.set_net(self)

    def num_inputs(self):
        count = 0
        for pin in self.terminals:
            if pin.direction == Pin.INPUT:
                count += 1

        return count

    def num_outputs(self):
        count = 0
        for pin in self.terminals:
            if pin.direction == Pin.OUTPUT:
                count += 1

        return count

    def get_value(self):
        return self.value

    def set_value(self, value):
        assert self.num_outputs() <= 1
        self.positive_edge = False
        self.negative_edge = False
        if self.value == 0 and value == 1:
            self.positive_edge = True
        elif self.value == 1 and value == 0:
            self.negative_edge = True

        self.value = value

        for p in self.terminals:
            if p.direction == Pin.INPUT:
                p.set_dirty()
        # print("Net %s has no input pins!" % self.name)

    def get_dag(self):
        dag = set()
        key = None
        if not self.num_outputs() == 1:
            print("Net " + str(self) + " have no outputs")
        assert self.num_outputs() == 1
        for p in self.terminals:
            if p.direction == Pin.OUTPUT:
                key = p
            if p.direction == Pin.INPUT:
                dag.add(p)

        return {key: dag}


class Pin(object):
    INPUT = 0
    OUTPUT = 1
    TRISTATE = 2

    def __init__(self, part=None, gate=None, name='unnamed', direction=TRISTATE):
        self.direction = direction
        self.part = part
        self.net = None
        self.gate = gate
        self.name = name

    def set_direction(self, direction):
        self.direction = direction

    def get_value(self):
        assert self.direction == Pin.INPUT
        return self.net.get_value()

    def is_positive_edge(self):
        return self.net.positive_edge

    def is_negative_edge(self):
        return self.net.negative_edge

    def set_dirty(self):
        self.gate.set_dirty()

    def set_value(self, value):
        if self.direction == Pin.OUTPUT:
            if self.net:
                self.net.set_value(value)
        else:
            print("Set value on input or tristate pin")

    def __repr__(self):
        return "%s: %s-%s" % (self.part.name, self.gate.name, self.name)

    def set_net(self, net):
        self.net = net

    def connect(self, pin):
        assert not (self.net and pin.net), "Merging of nets not implemented"
        if self.net:
            pin.connect(self)
            return
        assert not self.net
        if pin.net:
            pin.net.add_pin(self)
        else:
            new_net = Net("%s auto net" % self.name)
            new_net.add_pin(self)
            new_net.add_pin(pin)


class Gate(object):
    def __init__(self, part, name):
        self.name = name
        self.pins = {}
        self.dirty = True
        self.part = part

    def get_pin(self, name):
        return self.pins[name]

    def get_all_pins(self):
        return self.pins.values()

    def add_pin(self, name, direction):
        self.pins.update({name: Pin(self.part, self, name, direction)})

    def update(self):
        if self.dirty:
            is_dirty = self.part.update_impl(self.name)
            self.dirty = is_dirty

    def set_dirty(self):
        self.dirty = True

    def sanity_check(self):
        for pin in self.pins.values():
            if pin.direction == Pin.INPUT:
                if not pin.net:
                    print("Pin " + str(pin) + " is not connected.")
                elif pin.net.get_value() == None:
                    print("Net " + str(pin.net) + " have no value.")


class Part(object):
    def __init__(self, name):
        self.default_gate = 'A'
        self.gates = {}
        self.name = name

    def add_gate(self, name):
        self.gates.update({name: Gate(self, name)})

    def set_default_gate(self, gate):
        self.default_gate = gate

    def add_default_gate(self, name):
        self.add_gate(name)
        self.set_default_gate(name)

    def get_pin_by_gate(self, gate, name):
        return self.gates[gate].get_pin(name)

    def get_pin(self, name):
        return self.get_pin_by_gate(self.default_gate, name)

    def get_pins(self, names):
        return [self.get_pin(name) for name in names]

    def get_all_pins(self):
        return sum([list(g.get_all_pins()) for g in self.gates.values()], [])

    def add_gate_and_pin(self, gate, name, direction):
        self.gates[gate].add_pin(name, direction)

    def add_pin(self, name, direction):
        self.add_gate_and_pin(self.default_gate, name, direction)

    def get_dags(self):
        dags = {}
        for g in self.gates.values():
            for p in g.pins.values():
                if p.direction == Pin.INPUT:
                    dags.update({p: self.get_dag(p.gate.name, p.name)})
        return dags

    def sanity_check(self):
        for gate in self.gates.values():
            gate.sanity_check()

    def __repr__(self):
        pins = [str("%s: %s" % (k, repr(v))) for k, v in self.pins.items()]
        return "Part %s \n%s" % (self.name, '\n'.join(pins))
