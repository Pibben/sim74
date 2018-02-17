from unittest import TestCase

from core import Net
from p74xx import P74161, P74181
from system import System
from util import BinaryBus, SystemClock, Injector, BusInjector


class TestP74161(TestCase):
    def test_single(self):
        part = P74161("test")

        outbus = BinaryBus(("QD", "QC", "QB", "QA"))
        outbus.connectPart(part)

        clk_inj = Injector([part.getPin("CLK")])
        clk_inj.setValue(0)

        rconet = Net("rco")
        rconet.addPin(part.getPin("RCO"))

        enp_inj = Injector([part.getPin("ENP")])
        enp_inj.setValue(1)

        sys = System({"msb": part})
        sc = SystemClock(clk_inj, sys)
        sys.run()

        self.assertEqual(outbus.getValue(), 0)
        sc.step()
        self.assertEqual(outbus.getValue(), 1)
        sc.run(14)
        self.assertEqual(outbus.getValue(), 15)
        self.assertEqual(rconet.getValue(), 1)
        sc.step()
        self.assertEqual(outbus.getValue(), 0)
        self.assertEqual(rconet.getValue(), 0)

    def test_cascade(self):
        lsb = P74161("lsb")
        msb = P74161("msb")

        outbus = BinaryBus(("QH", "QG", "QF", "QE", "QD", "QC", "QB", "QA"))
        outbus.connectPins(msb.getPins(["QD", "QC", "QB", "QA"]) + lsb.getPins(["QD", "QC", "QB", "QA"]))

        clk_inj = Injector([msb.getPin("CLK"), lsb.getPin("CLK")])
        clk_inj.setValue(0)

        rcopin = lsb.getPin("RCO")
        rcopin.connect(msb.getPin("ENP"))

        enp_inj = Injector([lsb.getPin("ENP")])
        enp_inj.setValue(1)

        sys = System({"lsb": lsb, "msb": msb})
        sc = SystemClock(clk_inj, sys)
        sys.run()

        self.assertEqual(outbus.getValue(), 0)
        sc.step()
        self.assertEqual(outbus.getValue(), 1)
        sc.run(14)
        self.assertEqual(outbus.getValue(), 15)
        sc.step()
        self.assertEqual(outbus.getValue(), 16)


# https://github.com/fdecaire/LogicLibrary/blob/master/TTLLibrary.Tests/TTL74181Tests.cs
class TestP74181(TestCase):
    def test_74181(self):
        part = P74181("test")

        abus = BinaryBus(("A3", "A2", "A1", "A0"))
        abus.connectPart(part)
        bbus = BinaryBus(("B3", "B2", "B1", "B0"))
        bbus.connectPart(part)
        fbus = BinaryBus(("F3", "F2", "F1", "F0"))
        fbus.connectPart(part)
        sbus = BinaryBus(("S3", "S2", "S1", "S0"))
        sbus.connectPart(part)

        m_inj = Injector([part.getPin("M")])
        cn_inj = Injector([part.getPin("CN")])

        a_inj = BusInjector(abus)
        b_inj = BusInjector(bbus)
        s_inj = BusInjector(sbus)

        # F equals B
        s_inj.setValue(0b1010)
        m_inj.setValue(1)
        a_inj.setValue(0)
        b_inj.setValue(5)
        cn_inj.setValue(1)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        b_inj.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F equals A
        s_inj.setValue(0b1111)
        m_inj.setValue(1)
        a_inj.setValue(5)
        b_inj.setValue(0)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        a_inj.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F = A + B
        s_inj.setValue(0b1001)
        m_inj.setValue(0)
        a_inj.setValue(5)
        b_inj.setValue(2)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 7)

        a_inj.setValue(4)
        b_inj.setValue(1)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

    def test_cascaded_74181(self):
        msb_alu = P74181("msb")
        lsb_alu = P74181("lsb")

        abus = BinaryBus('A' + str(i) for i in range(8))
        abus.connectPins(msb_alu.getPins(["A3", "A2", "A1", "A0"]) + lsb_alu.getPins(["A3", "A2", "A1", "A0"]))
        bbus = BinaryBus('B' + str(i) for i in range(8))
        bbus.connectPins(msb_alu.getPins(["B3", "B2", "B1", "B0"]) + lsb_alu.getPins(["B3", "B2", "B1", "B0"]))
        fbus = BinaryBus('F' + str(i) for i in range(8))
        fbus.connectPins(msb_alu.getPins(["F3", "F2", "F1", "F0"]) + lsb_alu.getPins(["F3", "F2", "F1", "F0"]))
        sbus = BinaryBus('S' + str(i) for i in range(4))
        sbus.connectPins(msb_alu.getPins(["S3", "S2", "S1", "S0"]))
        sbus.connectPins(lsb_alu.getPins(["S3", "S2", "S1", "S0"]))

        lsb_alu.getPin("CN+4").connect(msb_alu.getPin("CN"))

        a_inj = BusInjector(abus)
        b_inj = BusInjector(bbus)
        s_inj = BusInjector(sbus)

        m_inj = Injector([msb_alu.getPin("M"), lsb_alu.getPin("M")])
        cn_inj = Injector([lsb_alu.getPin("CN")])

        s_inj.setValue(0b1001)
        m_inj.setValue(0)
        a_inj.setValue(113)
        b_inj.setValue(11)
        cn_inj.setValue(1)
        m_inj.setValue(0)

        sys = System({"lsb": lsb_alu, "msb": msb_alu})

        sys.run()

        self.assertEqual(fbus.getValue(), 124)
