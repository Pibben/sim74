from toposort import toposort_flatten

from core import Pin


class System(object):
    def __init__(self, parts, nets=None):
        self.parts = parts

        if nets:
            self.nets = nets
        else:
            setOfAllPins = sum((part.getAllPins() for part in parts.values()), [])
            self.nets = list({p.net for p in setOfAllPins if p.net})

        self.inputs = []
        self.outputs = []

    def setOutput(self, pinName):
        self.parts[pinName].setDirection(Pin.INPUT)
        self.outputs.append(self.parts[pinName])

    def setInput(self, pinName):
        self.parts[pinName].setDirection(Pin.OUTPUT)
        self.inputs.append(self.parts[pinName])

    def setHigh(self, partName, pinName):
        self.parts[partName].getPin(pinName).setDefaultValue(1)

    def run(self):
        totalDAGs = {}

        for p in self.parts.values():
            totalDAGs.update(p.getDAGs())

        for n in self.nets:
            totalDAGs.update(n.getDAG())

        order = toposort_flatten(totalDAGs, sort=False)
        order.reverse()

        for s in order:
            if (s.direction == Pin.OUTPUT) or s.injectionEnabled:
                s.gate.update()

        for o in self.outputs:
            print("%s: %d" % (o.name, o.getNumber()))
