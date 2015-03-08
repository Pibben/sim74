
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
   
   def getValue(self):
      for p in self.terminals:
         if p.direction == Pin.OUTPUT:
            return p.getValue()
      print("Net %s has no output pins!" % self.name)
      return 0

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
      if self.direction == Pin.OUTPUT:
         self.part.update()
         
         return self.value
      elif self.direction == Pin.INPUT:
         if(self.net == None):
            return 0
         else:
            return self.net.getValue()
      else:
         print("Get value on tristate pin")
         return None
      
   def setValue(self, value):
      self.value = value
   
   def __repr__(self):
      return "%s: %s" % (self.part.name, self.name)

   def setNet(self, net):
      self.net = net

class Part(object):
   def __init__(self, name):
      self.name = name
      self.pins = {}
      
   def getPin(self, name):
      return self.pins[name]
   
   def addPin(self, name, direction):
      self.pins.update({name: Pin(self, name, direction)})
   
   def __repr__(self):
      pins = [str("%s: %s" % (k, repr(v))) for k,v in self.pins.items()]
      return "Part %s \n%s" % (self.name, '\n'.join(pins))
   


