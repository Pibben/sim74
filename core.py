
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
     

class Pin(object):
   INPUT = 0
   OUTPUT = 1
   TRISTATE = 2
   
   def __init__(self, part, name, direction):
      self.direction = direction
      self.part = part
      self.value = 0
      self.net = None
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
      return "%s: %s" % (self.part.name, self.name)

   def setNet(self, net):
      self.net = net

class Part(object):
   def __init__(self, name):
      self.name = name
      self.pins = {}
      self.dirty = True
      
   def getPin(self, name):
      return self.pins[name]
   
   def addPin(self, name, direction):
      self.pins.update({name: Pin(self, name, direction)})
      
   def update(self):
      if self.dirty:
         isDirty = self.updateImpl()
         self.dirty = isDirty
         
   def setDirty(self):
      self.dirty = True
   
   def __repr__(self):
      pins = [str("%s: %s" % (k, repr(v))) for k,v in self.pins.items()]
      return "Part %s \n%s" % (self.name, '\n'.join(pins))
   


