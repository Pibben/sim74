class Net(object):
    def __init__(self, name):
        self.terminals = []
        self.name = name
        self.positiveEdge = False
        self.negativeEdge = False
        self.value = None

    def __repr__(self):
        pins = [str("%s" % k) for k in self.terminals]
        return "%s (%d/%d)[%s]: %s" % (self.name, self.numInputs(), self.numOutputs(), self.value, pins)

    def isPositiveEdge(self):
        return self.positiveEdge

    def isNegativeEdge(self):
        return self.negativeEdge

    def addPin(self, pin):
        self.terminals.append(pin)
        pin.setNet(self)

    def numInputs(self):
        count = 0
        for pin in self.terminals:
            if pin.direction == Pin.INPUT:
                count += 1

        return count

    def numOutputs(self):
        count = 0
        for pin in self.terminals:
            if pin.direction == Pin.OUTPUT:
                count += 1

        return count

    def getValue(self):
        return self.value

    def setValue(self, value):
        assert self.numOutputs() <= 1
        self.positiveEdge = False
        self.negativeEdge = False
        if self.value == 0 and value == 1:
            self.positiveEdge = True
        elif self.value == 1 and value == 0:
            self.negativeEdge = True

        self.value = value

        for p in self.terminals:
            if p.direction == Pin.INPUT:
                p.setDirty()
        # print("Net %s has no input pins!" % self.name)

    def getDAG(self):
        dag = set()
        key = None
        if not self.numOutputs() == 1:
            print("Net " + str(self) + " have no outputs")
        assert self.numOutputs() == 1
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

    def setDirection(self, direction):
        self.direction = direction

    def getValue(self):
        assert self.direction == Pin.INPUT
        return self.net.getValue()

    def isPositiveEdge(self):
        return self.net.positiveEdge

    def isNegativeEdge(self):
        return self.net.negativeEdge

    def setDirty(self):
        self.gate.setDirty()

    def setValue(self, value):
        if self.direction == Pin.OUTPUT:
            if self.net:
                self.net.setValue(value)
        else:
            print("Set value on input or tristate pin")

    def __repr__(self):
        return "%s: %s-%s" % (self.part.name, self.gate.name, self.name)

    def setNet(self, net):
        self.net = net

    def connect(self, pin):
        assert not (self.net and pin.net), "Merging of nets not implemented"
        if self.net:
            pin.connect(self)
            return
        assert not self.net
        if pin.net:
            pin.net.addPin(self)
        else:
            new_net = Net("%s auto net" % self.name)
            new_net.addPin(self)
            new_net.addPin(pin)


class Gate(object):
    def __init__(self, part, name):
        self.name = name
        self.pins = {}
        self.dirty = True
        self.part = part

    def getPin(self, name):
        return self.pins[name]

    def getAllPins(self):
        return self.pins.values()

    def addPin(self, name, direction):
        self.pins.update({name: Pin(self.part, self, name, direction)})

    def update(self):
        if self.dirty:
            isDirty = self.part.updateImpl(self.name)
            self.dirty = isDirty

    def setDirty(self):
        self.dirty = True

    def sanity_check(self):
        for pin in self.pins.values():
            if pin.direction == Pin.INPUT:
                if not pin.net:
                    print("Pin " + str(pin) + " is not connected.")
                elif not pin.net.getValue():
                    print("Net " + str(pin.net) + " have no value.")


class Part(object):
    def __init__(self, name):
        self.defaultGate = 'A'
        self.gates = {}
        self.name = name

    def addGate(self, name):
        self.gates.update({name: Gate(self, name)})

    def setDefaultGate(self, gate):
        self.defaultGate = gate

    def addDefaultGate(self, name):
        self.addGate(name)
        self.setDefaultGate(name)

    def getPinByGate(self, gate, name):
        return self.gates[gate].getPin(name)

    def getPin(self, name):
        return self.getPinByGate(self.defaultGate, name)

    def getPins(self, names):
        return [self.getPin(name) for name in names]

    def getAllPins(self):
        return sum([list(g.getAllPins()) for g in self.gates.values()], [])

    def addGateAndPin(self, gate, name, direction):
        self.gates[gate].addPin(name, direction)

    def addPin(self, name, direction):
        self.addGateAndPin(self.defaultGate, name, direction)

    def getDAGs(self):
        dags = {}
        for g in self.gates.values():
            for p in g.pins.values():
                if p.direction == Pin.INPUT:
                    dags.update({p: self.getDAG(p.gate.name, p.name)})
        return dags

    def sanity_check(self):
        for gate in self.gates.values():
            gate.sanity_check()

    def __repr__(self):
        pins = [str("%s: %s" % (k, repr(v))) for k, v in self.pins.items()]
        return "Part %s \n%s" % (self.name, '\n'.join(pins))
