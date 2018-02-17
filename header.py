from core import Part, Pin
from util import bits_to_int, int_to_bits


class Header(Part):
    def __init__(self, name, device):
        Part.__init__(self, name)

        self.width = int(device[-1])

        if self.width == 1:
            self.add_default_gate("G$1")
            self.add_pin('1', Pin.INPUT)
        else:
            self.add_default_gate("A")
            for i in range(self.width):
                self.add_pin(str(i + 1), Pin.INPUT)

        self.direction = Pin.TRISTATE

    def update_impl(self, gate_name):
        return False

    def set_direction(self, direction):
        self.direction = direction
        for p in self.gates[self.default_gate].pins.values():  # TODO
            p.set_direction(direction)

    def set_number(self, number):
        bits = int_to_bits(number, self.width)
        bits.reverse()

        for i in range(self.width):
            self.get_pin(str(i + 1)).set_value(bits[i])

    def get_number(self):
        bits = [self.get_pin(str(i + 1)).get_value() for i in range(self.width)]
        bits.reverse()

        return bits_to_int(*bits)

    def get_dag(self, g, n):
        return set()
