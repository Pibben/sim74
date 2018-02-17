from unittest import TestCase

from core import Pin
from util import BinaryBus


class TestBinaryBus(TestCase):
    def testSetValue(self):
        a = Pin()
        b = Pin()

        bus = BinaryBus(('a', 'b'))
        bus.connectPins((a, b))

        bus.setValue(1)
        self.assertEqual(a.net.value, 0)
        self.assertEqual(b.net.value, 1)

        bus.setValue(2)
        self.assertEqual(a.net.value, 1)
        self.assertEqual(b.net.value, 0)

    def testGetValue(self):
        a = Pin()
        b = Pin()

        bus = BinaryBus(('a', 'b'))
        bus.connectPins((a, b))

        a.net.value = 0
        b.net.value = 1

        self.assertEqual(bus.getValue(), 1)

        a.net.value = 1
        b.net.value = 0

        self.assertEqual(bus.getValue(), 2)
