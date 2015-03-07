
import xml.etree.ElementTree as ET

def bitsToInt(*bits):
   val = 0
   for i in range(len(bits)):
      val = (val << 1) | bits[i]
      
   return val

class Net(object):
   def __init__(self, name):
      self.terminals = []
      self.name = name
      
   def getValue(self):
      pass
   
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
      
   def update(self):
      pass
   
   def getValue(self):
      return self.value
   
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
   
class Header(Part):
   matchingNames = ["PINHD-1X4", "PINHD-1X8"]
   def __init__(self, name):
      Part.__init__(self, name)
      self.addPin('1', Pin.INPUT)
      self.addPin('2', Pin.INPUT)
      self.addPin('3', Pin.INPUT)
      self.addPin('4', Pin.INPUT)
      self.addPin('5', Pin.INPUT)
      self.addPin('6', Pin.INPUT)
      self.addPin('7', Pin.INPUT)
      self.addPin('8', Pin.INPUT)

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

   def update(self):
      a = bitsToInt(*[pins[name].getValue() for name in ['A0', 'A1', 'A2', 'A3']])
      b = bitsToInt(*[pins[name].getValue() for name in ['B0', 'B1', 'B2', 'B3']])
      s = bitsToInt(*[pins[name].getValue() for name in ['S0', 'S1', 'S2', 'S3']])
      c = pins['CN'].getValue()
      m = pins['CN'].getValue()
      
      

      
class PartFactory(object):
   def createPart(self, device, name):
      if device in P74181.matchingNames:
         return P74181(name)
      if device in Header.matchingNames:
         return Header(name)
      else:
         return None
      

def parseXml(filename):
   tree = ET.parse(filename)
   root = tree.getroot()
   parts = root.findall("./drawing/schematic/parts/part")
   netsNode  = root.findall("./drawing/schematic/sheets/sheet/nets")[0]
   
   pf = PartFactory()

   parts = {part.attrib['name']: pf.createPart(part.attrib['deviceset'], part.attrib['name']) for part in parts}
   
   nets = []
   
   for netNode in netsNode:
      
      net = Net(netNode.attrib['name'])
      nets.append(net)
      
      for segmentNode in netNode:
         for pinrefOrWire in segmentNode:
            if pinrefOrWire.tag == 'pinref':
               net.addPin(parts[pinrefOrWire.attrib['part']].getPin(pinrefOrWire.attrib['pin']))
         
   for net in nets:
      print(net)
         
   #for part in parts.values():
   #   print(part)
   
if __name__ == '__main__':
   parseXml('/home/per/eagle/test.sch')
