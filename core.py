
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
      assert self.numOutputs() == 1
      for p in self.terminals:
         if p.direction == Pin.INPUT:
            return p.setValue(value)
      print("Net %s has no input pins!" % self.name)
      
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
   
   def __init__(self, part, gate, name, direction):
      self.direction = direction
      self.part = part
      self.value = 0
      self.net = None
      self.gate = gate
      self.name = name
      
   def setDirection(self, direction):
      self.direction = direction
   
   def getValue(self):
      return self.value
      
   def setValue(self, value):
      self.value = value
      if self.direction == Pin.INPUT:
         self.part.setDirty()
      elif self.direction == Pin.OUTPUT:
         if(self.net):
            self.net.setValue(value)
      else:
         print("Set value on tristate pin")
   
   def __repr__(self):
      return "%s: %s-%s" % (self.part.name, self.gate, self.name)

   def setNet(self, net):
      self.net = net

class Part(object):
   def __init__(self, name):
      self.name = name
      self.pins = {}
      self.dirty = True
      
   def getPinByGate(self, gate, name):
      return self.pins[(gate, name)]
      
   def getPin(self, name):
      return self.getPinByGate('A', name)
   
   def addGateAndPin(self, gate, name, direction):
      self.pins.update({(gate, name): Pin(self, gate, name, direction)})
      
   def addPin(self, name, direction):
      self.addGateAndPin('A', name, direction)
      
   def update(self):
      if self.dirty:
         isDirty = self.updateImpl()
         self.dirty = isDirty
         
   def setDirty(self):
      self.dirty = True
      
   def getDAGs(self):
      dags = {}
      for p in self.pins.values():
         if p.direction == Pin.INPUT:
            dags.update({p: self.getDAG(p.gate, p.name)})
      return dags
   
   def __repr__(self):
      pins = [str("%s: %s" % (k, repr(v))) for k,v in self.pins.items()]
      return "Part %s \n%s" % (self.name, '\n'.join(pins))
   


