from core import Part,Pin
from util import *

class Header(Part):
   matchingNames = ["PINHD-1X4", "PINHD-1X8"]
   def __init__(self, name, device):
      Part.__init__(self, name)
      
      self.width = int(device[-1])
      
      for i in range(self.width):
         self.addPin(str(i+1), Pin.INPUT)
      
   def updateImpl(self):
      return False
      
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
   
   def getDAG(self, g, n):
      return set()
   