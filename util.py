from core import Net, Pin


def bits_to_int(*bits):
    val = 0
    for bit in bits:
        val = (val << 1) | bit

    # print(str(bits) + " -> %d" % val)

    return val


def int_to_bits(integer, num):
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

    def connect_pins(self, pins):
        assert len(self.nets) == len(pins)
        for n, p in zip(self.nets, pins):
            n.add_pin(p)

    def connect_part(self, part):
        d = {n.name: n for n in self.nets}
        for name, net in d.items():
            net.add_pin(part.get_pin(name))


class BinaryBus(Bus):
    def __init__(self, names):
        super(BinaryBus, self).__init__(names)

    def set_value(self, value):
        for bit, net in zip(int_to_bits(value, len(self.nets)), self.nets):
            net.set_value(bit)

    def get_value(self):
        return bits_to_int(*(net.get_value() for net in self.nets))


class BusInjector:
    def __init__(self, bus):
        self.nets = []
        for net in bus.nets:
            pin = Pin(direction=Pin.OUTPUT)
            net.add_pin(pin)
            self.nets.append(net)

    def set_value(self, value):
        for bit, net in zip(int_to_bits(value, len(self.nets)), self.nets):
            net.set_value(bit)


class SystemClock:
    def __init__(self, net, system):
        self.net = net
        self.system = system

    def step(self):
        # assert self.net.getValue() == 0

        self.net.set_value(1)
        self.system.run()
        self.net.set_value(0)
        self.system.run()

    def run(self, number):
        for i in range(number):
            self.step()
