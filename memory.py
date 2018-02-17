from core import Part, Pin
from util import bits_to_int, int_to_bits


class Memory(Part):
    def __init__(self, name):
        Part.__init__(self, name)


class CY62256LL(Memory):
    def __init__(self, name):
        Memory.__init__(self, name)

        self.add_default_gate("G$1")

        for i in range(15):
            self.add_pin("A%d" % i, Pin.INPUT)

        for i in range(8):
            self.add_pin("DQ%d" % i, Pin.OUTPUT)

    def get_dag(self, gate, name):
        return set([self.get_pin("DQ%d" % i) for i in range(8)])

    def update_impl(self, gate_name):
        bits = [self.get_pin("A%d" % (14 - i)).get_value() for i in range(15)]
        a = bits_to_int(*bits)

        bits = int_to_bits(a, 8)
        bits.reverse()

        for i in range(8):
            self.get_pin("DQ%d" % i).set_value(bits[i])

        return False
