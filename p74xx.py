from util import *

from core import Part,Pin

class Part7400(Part):
   def __init__(self, name):
      Part.__init__(self, name)
      
class P74181(Part7400):
   matchingNames = ["74*181"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)

      self.addPin('A0', Pin.INPUT)
      self.addPin('A1', Pin.INPUT)
      self.addPin('A2', Pin.INPUT)
      self.addPin('A3', Pin.INPUT)

      self.addPin('B0', Pin.INPUT)
      self.addPin('B1', Pin.INPUT)
      self.addPin('B2', Pin.INPUT)
      self.addPin('B3', Pin.INPUT)
      
      self.addPin('F0', Pin.OUTPUT)
      self.addPin('F1', Pin.OUTPUT)
      self.addPin('F2', Pin.OUTPUT)
      self.addPin('F3', Pin.OUTPUT)

      self.addPin('S0', Pin.INPUT)
      self.addPin('S1', Pin.INPUT)
      self.addPin('S2', Pin.INPUT)
      self.addPin('S3', Pin.INPUT)
      
      self.addPin('CN', Pin.INPUT)
      self.addPin('CN+4', Pin.OUTPUT)
      self.addPin('M', Pin.INPUT)
      self.addPin('A=B', Pin.OUTPUT)
      self.addPin('G', Pin.OUTPUT)
      self.addPin('P', Pin.OUTPUT)

   def updateImpl(self):
      a = bitsToInt(*[self.getPin(name).getValue() for name in ['A3', 'A2', 'A1', 'A0']])
      b = bitsToInt(*[self.getPin(name).getValue() for name in ['B3', 'B2', 'B1', 'B0']])
      s = bitsToInt(*[self.getPin(name).getValue() for name in ['S3', 'S2', 'S1', 'S0']])
      c = self.getPin('CN').getValue()
      m = self.getPin('M').getValue()
      
      f = a + b + c
      
      bits = intToBits(f, 5)

      self.getPin('F0').setValue(bits[4])
      self.getPin('F1').setValue(bits[3])
      self.getPin('F2').setValue(bits[2])
      self.getPin('F3').setValue(bits[1])
      self.getPin('CN+4').setValue(bits[0])
      
      return False
      
   def getDAG(self, _):
      return [pins[name] for name in ['F0', 'F1', 'F2', 'F3', 'CN+4', 'A=B', 'G', 'P']]
