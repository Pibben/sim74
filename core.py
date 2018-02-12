
from util import *

class Net(object):
   def __init__(self, name):
      self.terminals = []
      self.name = name
      
   def __repr__(self):
      pins = [str("%s" % k) for k in self.terminals]
      return "%s (%d/%d): %s" % (self.name, self.numInputs(), self.numOutputs(), pins)
   
   def addPin(self, pin):
      self.terminals.append(pin)
      pin.setNet(self)
      
   def numInputs(self):
      count = 0
      for pin in self.terminals:
         if pin.direction == Pin.INPUT:
            count += 1
            
      return count
   
   def numOutputs(self):
      count = 0
      for pin in self.terminals:
         if pin.direction == Pin.OUTPUT:
            count += 1
            
      return count
   
   def setValue(self, value):
      assert self.numOutputs() <= 1
      for p in self.terminals:
         if p.direction == Pin.INPUT:
            p.setValue(value)
      #print("Net %s has no input pins!" % self.name)
      
   def getDAG(self):
      dag = set()
      key = None
      assert self.numOutputs() == 1
      for p in self.terminals:
         if p.direction == Pin.OUTPUT:
            key = p
         if p.direction == Pin.INPUT:
            dag.add(p)
      
      return {key: dag}
     
class Pin(object):
   INPUT = 0
   OUTPUT = 1
   TRISTATE = 2

   def __init__(self, part=None, gate=None, name='unnamed', direction=TRISTATE):
      self.direction = direction
      self.part = part
      self.value = 0
      self.net = None
      self.gate = gate
      self.name = name
      self.positiveEdge = False
      self.negativeEdge = False
      self.injectionEnabled = False

   def setInjectionEnabled(self):
       self.injectionEnabled = True
      
   def setDefaultValue(self, value):
      self.value = value
      
   def setDirection(self, direction):
      self.direction = direction
   
   def getValue(self):
      return self.value
   
   def isPositiveEdge(self):
      return self.positiveEdge

   def isNegativeEdge(self):
      return self.negativeEdge
      
   def setValue(self, value):
      if self.direction == Pin.INPUT:
         self.gate.setDirty()
         self.positiveEdge = False
         self.negativeEdge = False
         if self.value == 0 and value == 1:
            self.positiveEdge = True
         elif self.value == 1 and value == 0:
            self.negativeEdge = True

      elif self.direction == Pin.OUTPUT:
         if(self.net):
            self.net.setValue(value)
      else:
         print("Set value on tristate pin")
         
      self.value = value
   
   def __repr__(self):
      return "%s: %s-%s" % (self.part.name, self.gate.name, self.name)

   def setNet(self, net):
      self.net = net

   def connect(self, pin):
      assert not self.net
      if pin.net:
         pin.net.addPin(self)
      else:
         new_net = Net("%s auto net" % self.name)
         new_net.addPin(self)
         new_net.addPin(pin)
      
class Gate(object):
   def __init__(self, part, name):
      self.name = name
      self.pins = {}
      self.dirty = True
      self.part = part
      
   def getPin(self, name):
      return self.pins[name]

   def getAllPins(self):
       return self.pins.values()
   
   def addPin(self, name, direction):
      self.pins.update({name: Pin(self.part, self, name, direction)})
      
   def update(self):
      if self.dirty:
         isDirty = self.part.updateImpl(self.name)
         self.dirty = isDirty
         
   def setDirty(self):
      self.dirty = True

class Part(object):
   def __init__(self, name):
      self.defaultGate = 'A'
      self.gates = {}
      self.name = name
      
   def addGate(self, name):
      self.gates.update({name: Gate(self, name)})
      
   def setDefaultGate(self, gate):
      self.defaultGate = gate
      
   def addDefaultGate(self, name):
      self.addGate(name)
      self.setDefaultGate(name)
      
   def getPinByGate(self, gate, name):
      return self.gates[gate].getPin(name)
      
   def getPin(self, name):
      return self.getPinByGate(self.defaultGate, name)

   def getPins(self, names):
      return [self.getPin(name) for name in names]

   def getAllPins(self):
       return sum([list(g.getAllPins()) for g in self.gates.values()], [])
   
   def addGateAndPin(self, gate, name, direction):
      self.gates[gate].addPin(name, direction)
      
   def addPin(self, name, direction):
      self.addGateAndPin(self.defaultGate, name, direction)
      
   def getDAGs(self):
      dags = {}
      for g in self.gates.values():
         for p in g.pins.values():
            if p.direction == Pin.INPUT:
               dags.update({p: self.getDAG(p.gate.name, p.name)})
      return dags
   
   def __repr__(self):
      pins = [str("%s: %s" % (k, repr(v))) for k,v in self.pins.items()]
      return "Part %s \n%s" % (self.name, '\n'.join(pins))
   


