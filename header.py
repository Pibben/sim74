from core import Part,Pin
from util import *

class Header(Part):
   matchingNames = ["PINHD-1X4", "PINHD-1X8"]
   def __init__(self, name):
      Part.__init__(self, name)
      self.addPin('1', Pin.INPUT)
      self.addPin('2', Pin.INPUT)
      self.addPin('3', Pin.INPUT)
      self.addPin('4', Pin.INPUT)
      self.addPin('5', Pin.INPUT)
      self.addPin('6', Pin.INPUT)
      self.addPin('7', Pin.INPUT)
      self.addPin('8', Pin.INPUT)
      self.width = 1
      
   def updateImpl(self):
      return False
   
   def setWidth(self, width):
      self.width = width
      
   def setDirection(self, direction):
      self.direction = direction
      for p in self.pins.values():
         p.setDirection(direction)
         
   def setNumber(self, number):
      bits = intToBits(number, self.width)
      bits.reverse()
      
      for i in range(self.width):
         self.getPin(str(i+1)).setValue(bits[i])

   def getNumber(self):
      bits = [self.getPin(str(i+1)).getValue() for i in range(self.width)]
      bits.reverse()

      return bitsToInt(*bits)
   