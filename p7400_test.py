from unittest import TestCase
from p74xx import P74181
from util import BinaryBus

#https://github.com/fdecaire/LogicLibrary/blob/master/TTLLibrary.Tests/TTL74181Tests.cs
class TestP74181(TestCase):
    def test_updateImpl(self):
        part = P74181("test")

        abus = BinaryBus(part.getPins(["A3", "A2", "A1", "A0"]))
        bbus = BinaryBus(part.getPins(["B3", "B2", "B1", "B0"]))
        fbus = BinaryBus(part.getPins(["F3", "F2", "F1", "F0"]))
        sbus = BinaryBus(part.getPins(["S3", "S2", "S1", "S0"]))

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
