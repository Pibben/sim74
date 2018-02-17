from unittest import TestCase

from core import Net
from p74xx import P74161, P74181
from system import System
from util import BinaryBus, SystemClock, Injector, BusInjector


class TestP74161(TestCase):
    def test_single(self):
        part = P74161("test")

        outbus = BinaryBus(("QD", "QC", "QB", "QA"))
        outbus.connect_part(part)

        clk_inj = Injector([part.get_pin("CLK")])
        clk_inj.set_value(0)

        rconet = Net("rco")
        rconet.add_pin(part.get_pin("RCO"))

        enp_inj = Injector([part.get_pin("ENP")])
        enp_inj.set_value(1)

        sys = System({"msb": part})
        sc = SystemClock(clk_inj, sys)
        sys.run()

        self.assertEqual(outbus.get_value(), 0)
        sc.step()
        self.assertEqual(outbus.get_value(), 1)
        sc.run(14)
        self.assertEqual(outbus.get_value(), 15)
        self.assertEqual(rconet.get_value(), 1)
        sc.step()
        self.assertEqual(outbus.get_value(), 0)
        self.assertEqual(rconet.get_value(), 0)

    def test_cascade(self):
        lsb = P74161("lsb")
        msb = P74161("msb")

        outbus = BinaryBus(("QH", "QG", "QF", "QE", "QD", "QC", "QB", "QA"))
        outbus.connect_pins(msb.get_pins(["QD", "QC", "QB", "QA"]) + lsb.get_pins(["QD", "QC", "QB", "QA"]))

        clk_inj = Injector([msb.get_pin("CLK"), lsb.get_pin("CLK")])
        clk_inj.set_value(0)

        rcopin = lsb.get_pin("RCO")
        rcopin.connect(msb.get_pin("ENP"))

        enp_inj = Injector([lsb.get_pin("ENP")])
        enp_inj.set_value(1)

        sys = System({"lsb": lsb, "msb": msb})
        sc = SystemClock(clk_inj, sys)
        sys.run()

        self.assertEqual(outbus.get_value(), 0)
        sc.step()
        self.assertEqual(outbus.get_value(), 1)
        sc.run(14)
        self.assertEqual(outbus.get_value(), 15)
        sc.step()
        self.assertEqual(outbus.get_value(), 16)


# https://github.com/fdecaire/LogicLibrary/blob/master/TTLLibrary.Tests/TTL74181Tests.cs
class TestP74181(TestCase):
    def test_74181(self):
        part = P74181("test")

        abus = BinaryBus(("A3", "A2", "A1", "A0"))
        abus.connect_part(part)
        bbus = BinaryBus(("B3", "B2", "B1", "B0"))
        bbus.connect_part(part)
        fbus = BinaryBus(("F3", "F2", "F1", "F0"))
        fbus.connect_part(part)
        sbus = BinaryBus(("S3", "S2", "S1", "S0"))
        sbus.connect_part(part)

        m_inj = Injector([part.get_pin("M")])
        cn_inj = Injector([part.get_pin("CN")])

        a_inj = BusInjector(abus)
        b_inj = BusInjector(bbus)
        s_inj = BusInjector(sbus)

        # F equals B
        s_inj.set_value(0b1010)
        m_inj.set_value(1)
        a_inj.set_value(0)
        b_inj.set_value(5)
        cn_inj.set_value(1)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 5)

        b_inj.set_value(4)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 4)

        # F equals A
        s_inj.set_value(0b1111)
        m_inj.set_value(1)
        a_inj.set_value(5)
        b_inj.set_value(0)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 5)

        a_inj.set_value(4)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 4)

        # F = A + B
        s_inj.set_value(0b1001)
        m_inj.set_value(0)
        a_inj.set_value(5)
        b_inj.set_value(2)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 7)

        a_inj.set_value(4)
        b_inj.set_value(1)

        part.update_impl("foo")

        self.assertEqual(fbus.get_value(), 5)

    def test_cascaded_74181(self):
        msb_alu = P74181("msb")
        lsb_alu = P74181("lsb")

        abus = BinaryBus('A' + str(i) for i in range(8))
        abus.connect_pins(msb_alu.get_pins(["A3", "A2", "A1", "A0"]) + lsb_alu.get_pins(["A3", "A2", "A1", "A0"]))
        bbus = BinaryBus('B' + str(i) for i in range(8))
        bbus.connect_pins(msb_alu.get_pins(["B3", "B2", "B1", "B0"]) + lsb_alu.get_pins(["B3", "B2", "B1", "B0"]))
        fbus = BinaryBus('F' + str(i) for i in range(8))
        fbus.connect_pins(msb_alu.get_pins(["F3", "F2", "F1", "F0"]) + lsb_alu.get_pins(["F3", "F2", "F1", "F0"]))
        sbus = BinaryBus('S' + str(i) for i in range(4))
        sbus.connect_pins(msb_alu.get_pins(["S3", "S2", "S1", "S0"]))
        sbus.connect_pins(lsb_alu.get_pins(["S3", "S2", "S1", "S0"]))

        lsb_alu.get_pin("CN+4").connect(msb_alu.get_pin("CN"))

        a_inj = BusInjector(abus)
        b_inj = BusInjector(bbus)
        s_inj = BusInjector(sbus)

        m_inj = Injector([msb_alu.get_pin("M"), lsb_alu.get_pin("M")])
        cn_inj = Injector([lsb_alu.get_pin("CN")])

        s_inj.set_value(0b1001)
        m_inj.set_value(0)
        a_inj.set_value(113)
        b_inj.set_value(11)
        cn_inj.set_value(1)
        m_inj.set_value(0)

        sys = System({"lsb": lsb_alu, "msb": msb_alu})

        sys.run()

        self.assertEqual(fbus.get_value(), 124)
