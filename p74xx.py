from util import *

from core import Part,Pin

class Part7400(Part):
   def __init__(self, name):
      Part.__init__(self, name)
      
class P7404(Part7400):
   matchingNames = ["74*04"]

   def __init__(self, name):
      Part7400.__init__(self, name)
      
      for gate in ('A', 'B', 'C', 'D', 'E', 'F'):
         self.addGateAndPin(gate, 'I', Pin.INPUT)
         self.addGateAndPin(gate, 'O', Pin.OUTPUT)
      
   def updateImpl(self):
      for gate in ('A', 'B', 'C', 'D', 'E', 'F'):
         self.getPinByGate(gate, 'O').setValue(1 - self.getPinByGate(gate, 'I').getValue())
      
      return True
   
   def getDAG(self, gate, _):
      return {self.getPinByGate(gate, 'O')}
   
class P7408(Part7400):
   matchingNames = ["74*08"]

   def __init__(self, name):
      Part7400.__init__(self, name)
      
      for gate in ('/1', '/2', '/3', '/4',):
         self.addGateAndPin(gate, 'A', Pin.INPUT)
         self.addGateAndPin(gate, 'B', Pin.INPUT)
         self.addGateAndPin(gate, 'Y', Pin.OUTPUT)
      
   def updateImpl(self):
      for gate in ('/1', '/2', '/3', '/4'):
         a = bool(self.getPinByGate(gate, 'A').getValue())
         b = bool(self.getPinByGate(gate, 'B').getValue())
         self.getPinByGate(gate, 'Y').setValue(int(a & b))
      
      return True
   
   def getDAG(self, gate, _):
      return {self.getPinByGate(gate, 'Y')}
   
class P74161(Part7400):
   matchingNames = ["74*161"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      self.gate = '1'
      self.setDefaultGate('1')
      self.count = 0
      self.rco = 0
      
      self.addGateAndPin(self.gate, 'QA', Pin.OUTPUT)
      self.addGateAndPin(self.gate, 'QB', Pin.OUTPUT)
      self.addGateAndPin(self.gate, 'QC', Pin.OUTPUT)
      self.addGateAndPin(self.gate, 'QD', Pin.OUTPUT)
      
      self.addGateAndPin(self.gate, 'A', Pin.INPUT)
      self.addGateAndPin(self.gate, 'B', Pin.INPUT)
      self.addGateAndPin(self.gate, 'C', Pin.INPUT)
      self.addGateAndPin(self.gate, 'D', Pin.INPUT)
      
      self.addGateAndPin(self.gate, 'RCO', Pin.OUTPUT)
      
      self.addGateAndPin(self.gate, 'CLK', Pin.INPUT)
      self.addGateAndPin(self.gate, 'ENP', Pin.INPUT)
      self.addGateAndPin(self.gate, 'ENT', Pin.INPUT)
      
   def updateImpl(self):
      enable = self.getPinByGate(self.gate, 'ENP').getValue()
      positiveEdge = self.getPinByGate(self.gate, 'CLK').isPositiveEdge()
      negativeEdge = self.getPinByGate(self.gate, 'CLK').isNegativeEdge()
      
      if enable == 1 and positiveEdge:
         self.count = self.count + 1
         
      #print("%s: %d" % (self.name, self.count))
         
      if self.count == 16:
         self.count = 0
         
      bits = intToBits(self.count, 4)
      self.getPinByGate(self.gate, 'QA').setValue(bits[3])
      self.getPinByGate(self.gate, 'QB').setValue(bits[2])
      self.getPinByGate(self.gate, 'QC').setValue(bits[1])
      self.getPinByGate(self.gate, 'QD').setValue(bits[0])
      self.getPinByGate(self.gate, 'RCO').setValue(self.rco)
      
      if self.count == 15:
         self.rco = 1
      else:
         self.rco = 0
      
      self.getPinByGate(self.gate, 'CLK').resetEdge() #TODO
      
      return False
      
   def getDAG(self, gate, name):
      return set([self.getPinByGate(self.gate, name) for name in ['QA', 'QB', 'QC', 'QD', 'RCO']])
      
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
      
   def getDAG(self, g, n):
      return set([self.getPin(name) for name in ['F0', 'F1', 'F2', 'F3', 'CN+4', 'A=B', 'G', 'P']])
