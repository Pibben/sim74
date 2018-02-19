from util import int_to_bits, bits_to_int

from core import Part, Pin


class Part7400(Part):
    def __init__(self, name):
        Part.__init__(self, name)


class P7404(Part7400):
    def __init__(self, name):
        Part7400.__init__(self, name)

        for gate in ('A', 'B', 'C', 'D', 'E', 'F'):
            self.add_gate(gate)
            self.add_gate_and_pin(gate, 'I', Pin.INPUT)
            self.add_gate_and_pin(gate, 'O', Pin.OUTPUT)

    def update_impl(self, gate_name):
        self.get_pin_by_gate(gate_name, 'O').set_value(1 - self.get_pin_by_gate(gate_name, 'I').get_value())

        return True

    def get_dag(self, gate, _):
        return {self.get_pin_by_gate(gate, 'O')}


class P7408(Part7400):
    def __init__(self, name):
        Part7400.__init__(self, name)

        for gate in ('/1', '/2', '/3', '/4',):
            self.add_gate(gate)
            self.add_gate_and_pin(gate, 'A', Pin.INPUT)
            self.add_gate_and_pin(gate, 'B', Pin.INPUT)
            self.add_gate_and_pin(gate, 'Y', Pin.OUTPUT)

    def update_impl(self, gate_name):
        a = bool(self.get_pin_by_gate(gate_name, 'A').get_value())
        b = bool(self.get_pin_by_gate(gate_name, 'B').get_value())
        self.get_pin_by_gate(gate_name, 'Y').set_value(int(a & b))

        return True

    def get_dag(self, gate, _):
        return {self.get_pin_by_gate(gate, 'Y')}


class P74161(Part7400):
    matchingNames = ["74*161"]

    def __init__(self, name):
        Part7400.__init__(self, name)
        self.count = 0
        self.rco = 0

        self.add_default_gate('1')

        self.add_pin('QA', Pin.OUTPUT)
        self.add_pin('QB', Pin.OUTPUT)
        self.add_pin('QC', Pin.OUTPUT)
        self.add_pin('QD', Pin.OUTPUT)

        self.add_pin('A', Pin.INPUT)
        self.add_pin('B', Pin.INPUT)
        self.add_pin('C', Pin.INPUT)
        self.add_pin('D', Pin.INPUT)

        self.add_pin('RCO', Pin.OUTPUT)

        self.add_pin('CLK', Pin.INPUT)
        self.add_pin('ENP', Pin.INPUT)
        self.add_pin('ENT', Pin.INPUT)

    def update_impl(self, gate_name):
        enable = self.get_pin('ENP').get_value()
        positive_edge = self.get_pin('CLK').is_positive_edge()

        if enable == 1 and positive_edge:
            self.count = self.count + 1

        # print("%s: %d" % (self.name, self.count))

        if self.count == 16:
            self.count = 0

        bits = int_to_bits(self.count, 4)
        self.get_pin('QA').set_value(bits[3])
        self.get_pin('QB').set_value(bits[2])
        self.get_pin('QC').set_value(bits[1])
        self.get_pin('QD').set_value(bits[0])
        self.get_pin('RCO').set_value(self.rco)

        if self.count == 15:
            self.rco = 1
        else:
            self.rco = 0

        return False

    def get_dag(self, gate, name):
        return set([self.get_pin(name) for name in ['QA', 'QB', 'QC', 'QD', 'RCO']])


# https://github.com/MisterTea/MAMEHub/blob/master/Sources/Emulator/src/emu/machine/74181.c
# http://static.righto.com/chip/74181-viewer.js
class P74181(Part7400):
    def __init__(self, name):
        Part7400.__init__(self, name)

        self.add_gate('A')

        self.add_pin('A0', Pin.INPUT)
        self.add_pin('A1', Pin.INPUT)
        self.add_pin('A2', Pin.INPUT)
        self.add_pin('A3', Pin.INPUT)

        self.add_pin('B0', Pin.INPUT)
        self.add_pin('B1', Pin.INPUT)
        self.add_pin('B2', Pin.INPUT)
        self.add_pin('B3', Pin.INPUT)

        self.add_pin('F0', Pin.OUTPUT)
        self.add_pin('F1', Pin.OUTPUT)
        self.add_pin('F2', Pin.OUTPUT)
        self.add_pin('F3', Pin.OUTPUT)

        self.add_pin('S0', Pin.INPUT)
        self.add_pin('S1', Pin.INPUT)
        self.add_pin('S2', Pin.INPUT)
        self.add_pin('S3', Pin.INPUT)

        self.add_pin('CN', Pin.INPUT)
        self.add_pin('CN+4', Pin.OUTPUT)
        self.add_pin('M', Pin.INPUT)
        self.add_pin('A=B', Pin.OUTPUT)
        self.add_pin('G', Pin.OUTPUT)
        self.add_pin('P', Pin.OUTPUT)

    def update_impl(self, gate_name):
        a3, a2, a1, a0 = (self.get_pin(name).get_value() for name in ('A3', 'A2', 'A1', 'A0'))
        b3, b2, b1, b0 = (self.get_pin(name).get_value() for name in ('B3', 'B2', 'B1', 'B0'))
        s3, s2, s1, s0 = (self.get_pin(name).get_value() for name in ('S3', 'S2', 'S1', 'S0'))
        # print(self.name)
        # print(a3, a2, a1, a0)
        # print(b3, b2, b1, b0)

        m_c = self.get_pin('CN').get_value()
        mp = not self.get_pin('M').get_value()

        # print(m_c)

        def make_p(a, b, s0, s1):
            return not (a or (b and s0) or (s1 and not b))

        def make_g(a, b, s2, s3):
            return not (((not b) and s2 and a) or (a and b and s3))

        p0 = make_p(a0, b0, s0, s1)
        g0 = make_g(a0, b0, s2, s3)
        p1 = make_p(a1, b1, s0, s1)
        g1 = make_g(a1, b1, s2, s3)
        p2 = make_p(a2, b2, s0, s1)
        g2 = make_g(a2, b2, s2, s3)
        p3 = make_p(a3, b3, s0, s1)
        g3 = make_g(a3, b3, s2, s3)

        # print([int(x) for x in (p0,g0,p1,g1,p2,g2,p3,g3)])

        i0 = not (m_c and mp)
        i1 = not p0 and g0
        i2 = (not ((mp and p0) or (mp and g0 and m_c)))
        i3 = not p1 and g1
        i4 = (not ((mp and p1) or (mp and p0 and g1) or (mp and m_c and g0 and g1)))
        i5 = not p2 and g2
        i6 = (not ((mp and p2) or (mp and p1 and g2) or (mp and p0 and g1 and g2) or (mp and m_c and g0 and g1 and g2)))
        i7 = not p3 and g3

        fp0 = i0 != i1
        fp1 = i2 != i3
        fp2 = i4 != i5
        fp3 = i6 != i7

        # m_equals = fp0 and fp1 and fp2 and fp3
        # m_p = not (g0 and g1 and g2 and g3)

        i8 = not (m_c and g0 and g1 and g2 and g3)

        m_g = not ((p0 and g1 and g2 and g3) or (p1 and g2 and g3) or (p2 and g3) or p3)
        m_cn = not i8 or not m_g

        self.get_pin('F0').set_value(fp0)
        self.get_pin('F1').set_value(fp1)
        self.get_pin('F2').set_value(fp2)
        self.get_pin('F3').set_value(fp3)
        self.get_pin('CN+4').set_value(m_cn)

        # print(self.name, int(m_cn), int(fp3), int(fp2), int(fp1), int(fp0))

        return False

    def get_dag(self, g, n):
        return set([self.get_pin(name) for name in ['F0', 'F1', 'F2', 'F3', 'CN+4', 'A=B', 'G', 'P']])


class P74244(Part7400):
    def __init__(self, name):
        Part7400.__init__(self, name)

        self.output_enabled = {'A': True, 'B': True}

        for gate in ('A', 'B'):
            self.add_gate(gate)
            self.add_gate_and_pin(gate, 'G', Pin.INPUT)

            for i in range(1, 4):
                self.add_gate_and_pin(gate, "A%d" % i, Pin.INPUT)
                self.add_gate_and_pin(gate, "Y%d" % i, Pin.OUTPUT)

    def update_impl(self, gate_name):
        self.output_enabled[gate_name] = self.get_pin_by_gate(gate_name, 'G').get_value()

        if self.output_enabled[gate_name]:
            for i in range(1, 4):
                self.get_pin_by_gate(gate_name, "Y%d" % i).set_direction(Pin.OUTPUT)
        else:
            for i in range(1, 4):
                self.get_pin_by_gate(gate_name, "Y%d" % i).set_direction(Pin.TRISTATE)

        for i in range(1, 4):
            value = self.get_pin_by_gate(gate_name, "A%d" % i).get_value()
            self.get_pin_by_gate(gate_name, "Y%d" % i).set_value(value)

    def get_dag(self, gate, name):
        all_outputs = set([self.get_pin_by_gate(gate, "Y%d" % i) for i in range(1, 4)])

        if name == 'G':
            return all_outputs

        return set()


class P74374(Part7400):
    def __init__(self, name):
        Part7400.__init__(self, name)

        self.output_enabled = True

        self.saved = [0 for _ in range(8)]

        self.add_gate('A')

        self.add_pin('CLK', Pin.INPUT)
        self.add_pin('OC', Pin.INPUT)

        for i in range(1, 9):
            self.add_pin("D%d" % i, Pin.INPUT)
            self.add_pin("Q%d" % i, Pin.TRISTATE)

        for i in range(8):
            self.add_pin("DUMMY%d" % i, Pin.OUTPUT)

    def init(self):
        for pin in self.get_all_pins():
            if pin.direction == Pin.OUTPUT:
                pin.set_value(0)

    def update_impl(self, gate_name):
        positive_edge = self.get_pin('CLK').is_positive_edge()
        output_enable = self.get_pin('OC').get_value()

        if output_enable:
            self.output_enabled = True
            for i in range(1, 9):
                self.get_pin("Q%d" % i).set_direction(Pin.OUTPUT)

        else:
            self.output_enabled = False
            for i in range(1, 9):
                self.get_pin("Q%d" % i).set_direction(Pin.TRISTATE)

        if positive_edge:
            # print("saving " + str(list(int(self.get_pin("D%d" % i).get_value()) for i in range(1,9))))
            for i in range(1, 9):
                self.saved[i-1] = int(self.get_pin("D%d" % i).get_value())
        else:
            for i in range(1, 9):
                # print("Outputting" + str(self.saved))
                self.get_pin("Q%d" % i).set_value(self.saved[i - 1])

        return False

    def get_dag(self, gate, name):
        all_outputs = set([self.get_pin("Q%d" % i) for i in range(1, 9)])

        if name == 'OC':
            return all_outputs

        if name == 'CLK' and self.output_enabled:
            return all_outputs

        return set([self.get_pin("DUMMY%d" % i) for i in range(8)])

    def get_value(self):
        return bits_to_int(*reversed(self.saved))
