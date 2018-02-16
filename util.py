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


class BinaryBus:
    def __init__(self, *pins):
        self.pins = pins

    def setValue(self, value):
        for bit, pin in zip(intToBits(value, len(self.pins)), self.pins):
            pin.setValue(bit)
            if pin.net:
                pin.net.setValue(bit)

    def getValue(self):
        return bitsToInt(*(pin.getValue() for pin in self.pins))

    def connect(self, bus):
        self.connectPins(bus.pins)

    def connectPins(self, pins):
        assert len(self.pins) == len(pins)
        for p1, p2 in zip(self.pins, pins):
            p1.connect(p2)


class SystemClock:
    def __init__(self, pin, system):
        self.pin = pin
        self.system = system

    def step(self):
        assert self.pin.getValue() == 0

        self.pin.setValue(1)
        self.system.run()
        self.pin.setValue(0)
        self.system.run()

    def run(self, number):
        for i in range(number):
            self.step()
