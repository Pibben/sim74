
from core import Part,Pin
from util import *

class Memory(Part):
   def __init__(self, name):
      Part.__init__(self, name)
   
   
class CY62256LL(Memory):
   matchingNames = ["CY62256LL-?*"]
   def __init__(self, name):
      Memory.__init__(self, name)
      
      self.gate = "G$1"
      
      for i in range(15):
         self.addGateAndPin(self.gate, "A%d" % i, Pin.INPUT)

      for i in range(8):
         self.addGateAndPin(self.gate, "DQ%d" % i, Pin.OUTPUT)

   def getDAG(self, gate, name):
      return set([self.getPinByGate(self.gate, "DQ%d" % i) for i in range(8)])
   
   def updateImpl(self):
      bits = [self.getPinByGate(self.gate, "A%d" % (14-i)).getValue() for i in range(15)]
      a = bitsToInt(*bits)
      
      bits = intToBits(a,8)
      bits.reverse()
      
      for i in range(8):
         self.getPinByGate(self.gate, "DQ%d" % i).setValue(bits[i])
         
      return False