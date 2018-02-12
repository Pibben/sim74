from unittest import TestCase
from p74xx import P74161, P74181
from util import BinaryBus, SystemClock
from system import System
from core import Pin

class TestP74161(TestCase):
    def test_single(self):
        part = P74161("test")
        sys = System({"msb": part})

        outbus = BinaryBus(*part.getPins(["QD", "QC", "QB", "QA"]))
        enpin = part.getPin("ENP")
        enpin.setInjectionEnabled()
        clkpin = part.getPin("CLK")
        clkpin.setInjectionEnabled()
        rcopin = part.getPin("RCO")

        enpin.setValue(1)

        sc = SystemClock(clkpin, sys)

        self.assertEqual(outbus.getValue(), 0)
        sc.step()
        self.assertEqual(outbus.getValue(), 1)
        sc.run(14)
        self.assertEqual(outbus.getValue(), 15)
        self.assertEqual(rcopin.getValue(), 1)
        sc.step()
        self.assertEqual(outbus.getValue(), 0)
        self.assertEqual(rcopin.getValue(), 0)

    def tes_cascade(self):
        lsb = P74161("lsb")
        msb = P74161("msb")

        outbus = BinaryBus(*(msb.getPins(["QD", "QC", "QB", "QA"]) + lsb.getPins(["QD", "QC", "QB", "QA"])))
        enpin = lsb.getPin("ENP")
        clkpin = msb.getPin("CLK")
        clkpin.connect(lsb.getPin("CLK"))
        rcopin = lsb.getPin("RCO")
        rcopin.connect(msb.getPin("ENP"))

        enpin.setValue(1)

        c = Clock(clkpin)

        self.assertEqual(outbus.getValue(), 0)
        c.step()
        self.assertEqual(outbus.getValue(), 1)
        c.run(14)
        self.assertEqual(outbus.getValue(), 15)
        c.step()
        self.assertEqual(outbus.getValue(), 16)



#https://github.com/fdecaire/LogicLibrary/blob/master/TTLLibrary.Tests/TTL74181Tests.cs
class TestP74181(TestCase):
    def test_74181(self):
        part = P74181("test")

        abus = BinaryBus(*part.getPins(["A3", "A2", "A1", "A0"]))
        bbus = BinaryBus(*part.getPins(["B3", "B2", "B1", "B0"]))
        fbus = BinaryBus(*part.getPins(["F3", "F2", "F1", "F0"]))
        sbus = BinaryBus(*part.getPins(["S3", "S2", "S1", "S0"]))

        mpin = part.getPin("M")
        cnpin = part.getPin("CN")

        # F equals B
        sbus.setValue(0b1010)
        mpin.setValue(1)
        abus.setValue(0)
        bbus.setValue(5)
        cnpin.setValue(1)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        bbus.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F equals A
        sbus.setValue(0b1111)
        mpin.setValue(1)
        abus.setValue(5)
        bbus.setValue(0)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 5)

        abus.setValue(4)

        part.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 4)

        # F = A + B
        sbus.setValue(0b1001)
        mpin.setValue(0)
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

        abus = BinaryBus(*(msb_alu.getPins(["A3", "A2", "A1", "A0"]) + lsb_alu.getPins(["A3", "A2", "A1", "A0"])))
        bbus = BinaryBus(*(msb_alu.getPins(["B3", "B2", "B1", "B0"]) + lsb_alu.getPins(["B3", "B2", "B1", "B0"])))
        fbus = BinaryBus(*(msb_alu.getPins(["F3", "F2", "F1", "F0"]) + lsb_alu.getPins(["F3", "F2", "F1", "F0"])))
        sbus = BinaryBus(*(msb_alu.getPins(["S3", "S2", "S1", "S0"])))
        sbus.connectPins(lsb_alu.getPins(["S3", "S2", "S1", "S0"]))

        lsb_alu.getPin("CN").connect(msb_alu.getPin("CN+4"))

        mpin = msb_alu.getPin("M")
        mpin.connect(lsb_alu.getPin("M"))
        cnpin = lsb_alu.getPin("CN")

        sbus.setValue(0b1001)
        mpin.setValue(0)
        abus.setValue(113)
        bbus.setValue(11)
        cnpin.setValue(1)
        mpin.setValue(0)

        lsb_alu.updateImpl("foo")
        msb_alu.getPin("CN").setValue(lsb_alu.getPin("CN+4").getValue()) #TODO: Run DAG
        msb_alu.updateImpl("foo")

        self.assertEqual(fbus.getValue(), 124)
