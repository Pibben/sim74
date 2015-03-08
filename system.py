
from parsexml import parseXml
from toposort import toposort_flatten

from core import Pin

class System(object):
   def __init__(self, filename):
      self.parts, self.nets = parseXml(filename)
      
      self.inputs = []
      self.outputs = []
      
   def setOutput(self, pinName):
      self.parts[pinName].setDirection(Pin.INPUT)
      self.outputs.append(self.parts[pinName])
      
      
   def setInput(self, pinName):
      self.parts[pinName].setDirection(Pin.OUTPUT)
      self.inputs.append(self.parts[pinName])
   
   def run(self, *args):
      assert len(args) == len(self.inputs)
      
      for i in range(len(args)):
         self.inputs[i].setNumber(args[i])
         
      totalDAGs = {}
      
      for p in self.parts.values():
         totalDAGs.update(p.getDAGs())
         
      for n in self.nets:
         totalDAGs.update(n.getDAG())

         
      order = toposort_flatten(totalDAGs)
      order.reverse()
         
      for s in order:
         if s.direction == Pin.OUTPUT and s.net:
            s.part.update()
            
      for o in self.outputs:
         print("%s: %d" % (o.name, o.getNumber()))
