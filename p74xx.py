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
         self.addGate(gate)
         self.addGateAndPin(gate, 'I', Pin.INPUT)
         self.addGateAndPin(gate, 'O', Pin.OUTPUT)
      
   def updateImpl(self, gateName):
      self.getPinByGate(gateName, 'O').setValue(1 - self.getPinByGate(gateName, 'I').getValue())
      
      return True
   
   def getDAG(self, gate, _):
      return {self.getPinByGate(gate, 'O')}
   
class P7408(Part7400):
   matchingNames = ["74*08"]

   def __init__(self, name):
      Part7400.__init__(self, name)
      
      for gate in ('/1', '/2', '/3', '/4',):
         self.addGate(gate)
         self.addGateAndPin(gate, 'A', Pin.INPUT)
         self.addGateAndPin(gate, 'B', Pin.INPUT)
         self.addGateAndPin(gate, 'Y', Pin.OUTPUT)
      
   def updateImpl(self, gateName):
      a = bool(self.getPinByGate(gateName, 'A').getValue())
      b = bool(self.getPinByGate(gateName, 'B').getValue())
      self.getPinByGate(gateName, 'Y').setValue(int(a & b))
      
      return True
   
   def getDAG(self, gate, _):
      return {self.getPinByGate(gate, 'Y')}
   
class P74161(Part7400):
   matchingNames = ["74*161"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      self.count = 0
      self.rco = 0
      
      self.addDefaultGate('1')
      
      self.addPin('QA', Pin.OUTPUT)
      self.addPin('QB', Pin.OUTPUT)
      self.addPin('QC', Pin.OUTPUT)
      self.addPin('QD', Pin.OUTPUT)
      
      self.addPin('A', Pin.INPUT)
      self.addPin('B', Pin.INPUT)
      self.addPin('C', Pin.INPUT)
      self.addPin('D', Pin.INPUT)
      
      self.addPin('RCO', Pin.OUTPUT)
      
      self.addPin('CLK', Pin.INPUT)
      self.addPin('ENP', Pin.INPUT)
      self.addPin('ENT', Pin.INPUT)
      
   def updateImpl(self, gateName):
      enable = self.getPin('ENP').getValue()
      positiveEdge = self.getPin('CLK').isPositiveEdge()
      negativeEdge = self.getPin('CLK').isNegativeEdge()
      
      if enable == 1 and positiveEdge:
         self.count = self.count + 1
         
      #print("%s: %d" % (self.name, self.count))
         
      if self.count == 16:
         self.count = 0
         
      bits = intToBits(self.count, 4)
      self.getPin('QA').setValue(bits[3])
      self.getPin('QB').setValue(bits[2])
      self.getPin('QC').setValue(bits[1])
      self.getPin('QD').setValue(bits[0])
      self.getPin('RCO').setValue(self.rco)
      
      if self.count == 15:
         self.rco = 1
      else:
         self.rco = 0
      
      return False
      
   def getDAG(self, gate, name):
      return set([self.getPin(name) for name in ['QA', 'QB', 'QC', 'QD', 'RCO']])

#https://github.com/MisterTea/MAMEHub/blob/master/Sources/Emulator/src/emu/machine/74181.c
class P74181(Part7400):
   matchingNames = ["74*181"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      
      self.addGate('A')

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

   def updateImpl(self, gateName):
      a3, a2, a1, a0 = (self.getPin(name).getValue() for name in ('A3', 'A2', 'A1', 'A0'))
      b3, b2, b1, b0 = (self.getPin(name).getValue() for name in ('B3', 'B2', 'B1', 'B0'))
      s3, s2, s1, s0 = (self.getPin(name).getValue() for name in ('S3', 'S2', 'S1', 'S0'))

      m_c = self.getPin('CN').getValue()
      mp = not self.getPin('M').getValue()

      ap0 = not (a0 or (b0 and s0) or (s1 and not b0))
      bp0 = not (((not b0) and s2 and a0) or (a0 and b0 and s3))
      ap1 = not (a1 or (b1 and s0) or (s1 and not b1))
      bp1 = not (((not b1) and s2 and a1) or (a1 and b1 and s3))
      ap2 = not (a2 or (b2 and s0) or (s1 and not b2))
      bp2 = not (((not b2) and s2 and a2) or (a2 and b2 and s3))
      ap3 = not (a3 or (b3 and s0) or (s1 and not b3))
      bp3 = not (((not b3) and s2 and a3) or (a3 and b3 and s3))

      fp0 = not (m_c and mp) != ((not ap0) and bp0)
      fp1 = (not ((mp and ap0) or (mp and bp0 and m_c))) != ((not ap1) and bp1)
      fp2 = (not ((mp and ap1) or (mp and ap0 and bp1) or (mp and m_c and bp0 and bp1))) != ((not ap2) and bp2)

      fp3 = (not ((mp and ap2) or (mp and ap1 and bp2) or (mp and ap0 and bp1 and bp2) or (mp and m_c and bp0 and bp1 and bp2))) != ((not ap3) and bp3)
      
      m_equals = fp0 and fp1 and fp2 and fp3
      m_p = not (bp0 and bp1 and bp2 and bp3)
      m_g = not ((ap0 and bp1 and bp2 and bp3) or (ap1 and bp2 and bp3) or (ap2 and bp3) or ap3)
      m_cn = (not (m_c and bp0 and bp1 and bp2 and bp3)) or m_g

      self.getPin('F0').setValue(fp0)
      self.getPin('F1').setValue(fp1)
      self.getPin('F2').setValue(fp2)
      self.getPin('F3').setValue(fp3)
      self.getPin('CN+4').setValue(m_cn)
      
      return False
      
   def getDAG(self, g, n):
      return set([self.getPin(name) for name in ['F0', 'F1', 'F2', 'F3', 'CN+4', 'A=B', 'G', 'P']])
   
class P74244(Part7400):
   matchingNames = ["74*244"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      
      self.outputEnabled = {'A': True, 'B': True}
      
      for gate in ('A', 'B'):
         self.addGate(gate)
         self.addGateAndPin(gate, 'G', Pin.INPUT)
         
         for i in range(1,4):
            self.addGateAndPin(gate, "A%d" % i, Pin.INPUT)
            self.addGateAndPin(gate, "Y%d" % i, Pin.OUTPUT)
            
   def updateImpl(self, gateName):
      outputEnabled[gateName] = self.getPinByGate(gateName, 'G').getValue()
      
      if outputEnabled[gateName]:
         for i in range(1,4):
            self.getPinByGate(gateName, "Y%d" % i).setDirection(Pin.OUTPUT)
      else:
         for i in range(1,4):
            self.getPinByGate(gateName, "Y%d" % i).setDirection(Pin.TRISTATE)

      for i in range(1,4):
         value = self.getPinByGate(gateName, "A%d" % i).getValue()
         self.getPinByGate(gateName, "Y%d" % i).setValue(value)
         
   def getDAG(self, gate, name):
      allOutputs = set([self.getPinByGate(gate, "Y%d" % i) for i in range(1,4)])
      
      if name == 'G':
         return allOutputs
      
      return set()

class P74374(Part7400):
   matchingNames = ["74*374"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      
      self.outputEnabled = True
      
      self.addGate('A')
      
      self.addPin('CLK', Pin.INPUT)
      self.addPin('OC', Pin.INPUT)
      
      for i in range(1,8):
         self.addPin("D%d" % i, Pin.INPUT)
         self.addPin("Q%d" % i, Pin.OUTPUT)
         
   def updateImpl(self, gateName):
      positiveEdge = self.getPin('CLK').isPositiveEdge()
      outputEnable = self.getPin('OC').getValue()
      
      if positiveEdge:
         for i in range(1,8):
            self.getPin("Q%d" % i).setValue(self.getPin("D%d" % i).getValue)
            
      if outputEnable:
         self.outputEnabled = True
         for i in range(1,8):
            self.getPin("Q%d" % i).setDirection(Pin.OUTPUT)
            
      else:
         self.outputEnabled = False
         for i in range(1,8):
            self.getPin("Q%d" % i).setDirection(Pin.TRISTATE)
            
      return False
   
   def getDAG(self, gate, name):
      allOutputs = set([self.getPin("Q%d" % i) for i in range(1,8)])
      
      if gate == 'OC':
         return allOutputs
      
      if gate == 'CLK' and self.outputEnabled:
         return allOutputs
      
      return set()
   
