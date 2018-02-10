from unittest import TestCase
from unittest.mock import patch
from unittest.mock import call
from util import BinaryBus
from core import Pin


class TestBinaryBus(TestCase):
    @patch('core.Pin')
    @patch('core.Pin')
    def testSetValue(self, Pin1, Pin2):
        a = Pin1()
        b = Pin2()

        bus = BinaryBus(a, b)

        bus.setValue(1)
        a.setValue.assert_called_with(0)
        b.setValue.assert_called_with(1)

        bus.setValue(2)
        a.setValue.assert_called_with(1)
        b.setValue.assert_called_with(0)

    @patch('core.Pin')
    @patch('core.Pin')
    def testGetValue(self, Pin1, Pin2):
        a = Pin1()
        b = Pin2()

        bus = BinaryBus(a, b)

        a.getValue.return_value = 0
        b.getValue.return_value = 1

        self.assertEqual(bus.getValue(), 1)

        a.getValue.return_value = 1
        b.getValue.return_value = 0

        self.assertEqual(bus.getValue(), 2)

    def testConnect(self):
        a = Pin()
        b = Pin()
        c = Pin()
        d = Pin()

        b1 = BinaryBus(a, b)
        b2 = BinaryBus(c, d)
        b1.connect(b2)

        self.assertIsNotNone(a.net)
        self.assertIsNotNone(b.net)
        self.assertIsNotNone(c.net)
        self.assertIsNotNone(d.net)
        self.assertTrue(a.net is c.net)
        self.assertTrue(b.net is d.net)
