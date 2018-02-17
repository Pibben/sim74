from unittest import TestCase
from p74xx import P74161, P74181
from util import BinaryBus, SystemClock, Injector
from system import System
from core import Pin, Net


class TestP74161(TestCase):
    def test_single(self):
        part = P74161("test")

        outbus = BinaryBus(("QD", "QC", "QB", "QA"))
        outbus.connectPart(part)

        clk_inj = Injector(part.getPin("CLK"))
        clk_inj.setValue(0)

        rconet = Net("rco")
        rconet.addPin(part.getPin("RCO"))

        enp_inj = Injector(part.getPin("ENP"))
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

        #TODO: Improve this
        clknet = Net("clk")
        clknet.addPin(msb.getPin("CLK"))
        clknet.addPin(lsb.getPin("CLK"))
        clknet.addPin(Pin(direction=Pin.OUTPUT))
        clknet.setValue(0)

        rcopin = lsb.getPin("RCO")
        rcopin.connect(msb.getPin("ENP"))

        enp_inj = Injector(lsb.getPin("ENP"))
        enp_inj.setValue(1)

        sys = System({"lsb": lsb, "msb": msb})
        sc = SystemClock(clknet, sys)
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

        m_inj = Injector(part.getPin("M"))
        cn_inj = Injector(part.getPin("CN"))

        # F equals B
        sbus.setValue(0b1010)
        m_inj.setValue(1)
        abus.setValue(0)
        bbus.setValue(5)
        cn_inj.setValue(1)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        bbus.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F equals A
        sbus.setValue(0b1111)
        m_inj.setValue(1)
        abus.setValue(5)
        bbus.setValue(0)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        abus.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F = A + B
        sbus.setValue(0b1001)
        m_inj.setValue(0)
        abus.setValue(5)
        bbus.setValue(2)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 7)

        abus.setValue(4)
        bbus.setValue(1)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

    def test_cascaded_74181(self):
        msb_alu = P74181("msb")
        lsb_alu = P74181("lsb")

        abus = BinaryBus('A'+str(i) for i in range(8))
        abus.connectPins(msb_alu.getPins(["A3", "A2", "A1", "A0"]) + lsb_alu.getPins(["A3", "A2", "A1", "A0"]))
        bbus = BinaryBus('B' + str(i) for i in range(8))
        bbus.connectPins(msb_alu.getPins(["B3", "B2", "B1", "B0"]) + lsb_alu.getPins(["B3", "B2", "B1", "B0"]))
        fbus = BinaryBus('F' + str(i) for i in range(8))
        fbus.connectPins(msb_alu.getPins(["F3", "F2", "F1", "F0"]) + lsb_alu.getPins(["F3", "F2", "F1", "F0"]))
        sbus = BinaryBus('S' + str(i) for i in range(4))
        sbus.connectPins(msb_alu.getPins(["S3", "S2", "S1", "S0"]))
        sbus.connectPins(lsb_alu.getPins(["S3", "S2", "S1", "S0"]))

        lsb_alu.getPin("CN").connect(msb_alu.getPin("CN+4"))

        m_net = Net("M")
        m_net.addPin(msb_alu.getPin("M"))
        m_net.addPin(lsb_alu.getPin("M"))
        cn_net = Net("CN")
        cn_net.addPin(lsb_alu.getPin("CN"))
        msb_cn_net = Net("CN")
        msb_cn_net.addPin(msb_alu.getPin("CN"))
        cn4_net = Net("CN+4")
        cn4_net.addPin(lsb_alu.getPin("CN+4"))

        sbus.setValue(0b1001)
        m_net.setValue(0)
        abus.setValue(113)
        bbus.setValue(11)
        cn_net.setValue(1)
        m_net.setValue(0)

        lsb_alu.updateImpl("foo")
        msb_cn_net.setValue(cn4_net.getValue())  # TODO: Run DAG
        msb_alu.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 124)
