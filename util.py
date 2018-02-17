from core import Net, Pin


def bitsToInt(*bits):
    val = 0
    for bit in bits:
        val = (val << 1) | bit

    # print(str(bits) + " -> %d" % val)

    return val


def intToBits(integer, num):
    retval = []
    for i in range(num):
        retval.append((integer >> (num - i - 1)) & 1)

    # print("%d -> " % integer + str(retval))

    return retval

class Injector(Pin):
    def __init__(self, pins, name=None):

        if not name:
            name = pins[0].name

        super(Injector, self).__init__(name=name, direction=Pin.OUTPUT)

        for pin in pins:
            assert pin.direction == Pin.INPUT
            pin.connect(self)

class BinaryProbe:
    pass

class Bus(object):
    def __init__(self, names):
        self.nets = [Net(name) for name in names]

    def connectPins(self, pins):
        assert len(self.nets) == len(pins)
        for n, p in zip(self.nets, pins):
            n.addPin(p)

    def connectPart(self, part):
        d = {n.name: n for n in self.nets}
        for name, net in d.items():
            net.addPin(part.getPin(name))

class BinaryBus(Bus):
    def __init__(self, names):
        super(BinaryBus, self).__init__(names)

    def setValue(self, value):
        for bit, net in zip(intToBits(value, len(self.nets)), self.nets):
            net.setValue(bit)

    def getValue(self):
        return bitsToInt(*(net.getValue() for net in self.nets))

class BusInjector():
    def __init__(self, bus):
        self.nets = []
        for net in bus.nets:
            pin = Pin(direction=Pin.OUTPUT)
            net.addPin(pin)
            self.nets.append(net)

    def setValue(self, value):
        for bit, net in zip(intToBits(value, len(self.nets)), self.nets):
            net.setValue(bit)

class SystemClock:
    def __init__(self, net, system):
        self.net = net
        self.system = system

    def step(self):
        #assert self.net.getValue() == 0

        self.net.setValue(1)
        self.system.run()
        self.net.setValue(0)
        self.system.run()

    def run(self, number):
        for i in range(number):
            self.step()
