from unittest import TestCase

from core import Pin
from util import BinaryBus


class TestBinaryBus(TestCase):
    def test_set_value(self):
        a = Pin()
        b = Pin()

        bus = BinaryBus(('a', 'b'))
        bus.connect_pins((a, b))

        bus.set_value(1)
        self.assertEqual(a.net.value, 0)
        self.assertEqual(b.net.value, 1)

        bus.set_value(2)
        self.assertEqual(a.net.value, 1)
        self.assertEqual(b.net.value, 0)

    def test_get_value(self):
        a = Pin()
        b = Pin()

        bus = BinaryBus(('a', 'b'))
        bus.connect_pins((a, b))

        a.net.value = 0
        b.net.value = 1

        self.assertEqual(bus.get_value(), 1)

        a.net.value = 1
        b.net.value = 0

        self.assertEqual(bus.get_value(), 2)
