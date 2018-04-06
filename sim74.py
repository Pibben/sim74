from core import Pin, Part
from p74xx import P74181, P74374, P7408
from system import System
from util import BinaryBus, Injector, int_to_bits, SystemClock


class InstructionDecoder(Part):
    def __init__(self, name):
        super().__init__(name)

        self.add_gate('A')

        self.add_pin('S0', Pin.OUTPUT)
        self.add_pin('S1', Pin.OUTPUT)
        self.add_pin('S2', Pin.OUTPUT)
        self.add_pin('S3', Pin.OUTPUT)

        for i in range(8):
            self.add_pin('IMM' + str(i), Pin.OUTPUT)

        self.add_pin('M', Pin.OUTPUT)
        self.add_pin("REG_A", Pin.OUTPUT)
        self.add_pin("REG_B", Pin.OUTPUT)

        self.add_pin("REG_A_OE", Pin.OUTPUT)
        self.add_pin("REG_B_OE", Pin.OUTPUT)

    def decode(self, mnemonic):
        table = {'add': [1, 0, 0, 1, 0],
                 'sbc': [0, 1, 1, 0, 0],
                 'ld':  [0, 0, 0, 0, 0],
                 'xor': [0, 1, 1, 0, 1],
                 'and': [1, 0, 1, 1, 1],
                 'or':  [1, 1, 1, 0, 1]}

        operation, *operands = mnemonic.split()

        out = table[operation]
        for pin_name, value in zip(['S3', 'S2', 'S1', 'S0', 'M'], out):
            self.get_pin(pin_name).set_value(value)

        bits = int_to_bits(int(operands[1]), 8)
        for pin_name, value in zip(('IMM' + str(i) for i in range(7, -1, -1)), bits):
            self.get_pin(pin_name).set_value(value)

        if operands[0] == 'a':
            self.get_pin('REG_A').set_value(1)
            self.get_pin('REG_B').set_value(0)
        else:
            self.get_pin('REG_A').set_value(0)
            self.get_pin('REG_B').set_value(1)

        if operands[2] == 'a':
            self.get_pin('REG_A_OE').set_value(1)
            self.get_pin('REG_B_OE').set_value(0)
        else:
            self.get_pin('REG_A_OE').set_value(0)
            self.get_pin('REG_B_OE').set_value(1)

    def init(self):
        self.get_pin('REG_A_OE').set_value(1)
        self.get_pin('REG_B_OE').set_value(0)

    def update_impl(self, gate_name):
        pass
        #for pin in self.get_all_pins():
        #    pin.set_value(0)


class Cpu:
    def __init__(self):
        self.instruction_decoder = InstructionDecoder("id")
        lsb_alu = P74181("lsb")
        msb_alu = P74181("msb")

        self.reg_a = P74374("a")
        self.reg_b = P74374("b")
        reg_clk_sel = P7408("rcs")

        alu_ctrl_bus = BinaryBus(['S3', 'S2', 'S1', 'S0', 'M'])
        alu_ctrl_bus.connect_part(self.instruction_decoder)
        alu_ctrl_bus.connect_part(lsb_alu)
        alu_ctrl_bus.connect_part(msb_alu)

        self.alu_a_bus = BinaryBus('A' + str(i) for i in range(7, -1, -1))
        self.alu_b_bus = BinaryBus('B' + str(i) for i in range(7, -1, -1))
        self.alu_f_bus = BinaryBus('F' + str(i) for i in range(7, -1, -1))

        self.alu_a_bus.connect_pins(msb_alu.get_pins(["A3", "A2", "A1", "A0"]) +
                                    lsb_alu.get_pins(["A3", "A2", "A1", "A0"]))
        self.alu_f_bus.connect_pins(msb_alu.get_pins(["F3", "F2", "F1", "F0"]) +
                                    lsb_alu.get_pins(["F3", "F2", "F1", "F0"]))

        self.alu_a_bus.connect_pins(self.instruction_decoder.get_pins('IMM' + str(i) for i in range(7, -1, -1)))
        self.alu_f_bus.connect_pins(self.reg_a.get_pins('D' + str(i) for i in range(8, 0, -1)))
        self.alu_f_bus.connect_pins(self.reg_b.get_pins('D' + str(i) for i in range(8, 0, -1)))

        lsb_alu.get_pin("CN+4").connect(msb_alu.get_pin("CN"))

        clk_inj = Injector([reg_clk_sel.get_pin_by_gate('/1', 'A'), reg_clk_sel.get_pin_by_gate('/2', 'A')])
        clk_inj.set_value(0)

        self.instruction_decoder.get_pin("REG_A").connect(reg_clk_sel.get_pin_by_gate('/1', 'B'))
        self.instruction_decoder.get_pin("REG_B").connect(reg_clk_sel.get_pin_by_gate('/2', 'B'))

        self.instruction_decoder.get_pin("REG_A_OE").connect(self.reg_a.get_pin("OC"))
        self.instruction_decoder.get_pin("REG_B_OE").connect(self.reg_b.get_pin("OC"))

        self.alu_input_b_bus = BinaryBus('Q' + str(i) for i in range(8, 0, -1))
        self.alu_input_b_bus.connect_part(self.reg_a)
        self.alu_input_b_bus.connect_pins(msb_alu.get_pins(["B3", "B2", "B1", "B0"]) +
                                          lsb_alu.get_pins(["B3", "B2", "B1", "B0"]))
        self.alu_input_b_bus.connect_part(self.reg_b)
        self.alu_input_b_bus.connect_pins(msb_alu.get_pins(["B3", "B2", "B1", "B0"]) +
                                          lsb_alu.get_pins(["B3", "B2", "B1", "B0"]))

        self.reg_a.get_pin("CLK").connect(reg_clk_sel.get_pin_by_gate('/1', 'Y'))
        self.reg_b.get_pin("CLK").connect(reg_clk_sel.get_pin_by_gate('/2', 'Y'))

        dummy_inj = Injector([reg_clk_sel.get_pin_by_gate('/3', 'A'),
                              reg_clk_sel.get_pin_by_gate('/3', 'B'),
                              reg_clk_sel.get_pin_by_gate('/4', 'A'),
                              reg_clk_sel.get_pin_by_gate('/4', 'B')])

        dummy_inj.set_value(0)

        self.sys = System({"is": self.instruction_decoder,
                           "lsb": lsb_alu,
                           "msb": msb_alu,
                           "rcs": reg_clk_sel,
                           "reg_a": self.reg_a,
                           "reg_b": self.reg_b})

        cn_inj = Injector([lsb_alu.get_pin("CN")])
        cn_inj.set_value(1)

        # TODO: Do somethings smarter
        self.reg_a.init()
        self.reg_b.init()
        self.instruction_decoder.init()

        self.sys.run()

        self.sys.sanity_check()

        self.sc = SystemClock(clk_inj, self.sys)

    def run(self, line):
        self.instruction_decoder.decode(line)

        self.sc.step()

        retval = {'a': self.reg_a.get_value(),
                  'b': self.reg_b.get_value()}

        print(retval)

        return retval


if __name__ == '__main__':
    cpu = Cpu()
    assert cpu.run("ld b 123 b") ==  {'a': 0, 'b': 123}
    assert cpu.run("add a 31 b") ==  {'b': 123, 'a': 154}  # a = 31 + b
    assert cpu.run("add a 1 b") ==   {'b': 123, 'a': 124}   # a =  1 + b
    assert cpu.run("add b 1 b") ==   {'b': 124, 'a': 124}   # b =  1 + b
    assert cpu.run("sbc b 132 b") == {'b': 7, 'a': 124}   # b = 132 - b - 1
    assert cpu.run("add a 1 a") ==   {'b': 7, 'a': 125}
    assert cpu.run("sbc b 129 a") == {'b': 3, 'a': 125}
    assert cpu.run("ld b 15 b") ==   {'a': 125, 'b': 15}
    assert cpu.run("xor a 85 b") ==  {'a': 90, 'b': 15}
    assert cpu.run("or a 16 b") ==   {'a': 31, 'b': 15}
    assert cpu.run("and a 8 b") ==   {'a': 8, 'b': 15}
