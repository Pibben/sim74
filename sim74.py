
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
      pins = [str("%s:" % k) for k in self.terminals]
      return "%s: %s" % (self.name, pins)
   
   def addPin(self, pin):
      self.terminals.append(pin)
      pin.addNet(self)

class Pin(object):
   INPUT = 0
   OUTPUT = 1
   TRISTATE = 2
   
   def __init__(self, part, direction):
      self.direction = direction
      self.part = part
      self.value = 0
      self.net = None
      
   def update(self):
      pass
   
   def getValue(self):
      return self.value
   
   def __repr__(self):
      return "%s: %s" % (self.part.name, "pin xx")
   
   def setNet(self, net):
      self.net = net

class Part(object):
   def __init__(self, name):
      self.name = name
      self.pins = {}
      
   def getPin(self, name):
      return self.pins[name]
   
   def __repr__(self):
      pins = [str("%s: %s" % (k, repr(v))) for k,v in self.pins.items()]
      return "Part %s \n%s" % (self.name, '\n'.join(pins))
   
class Header(Part):
   matchingNames = ["PINHD-1X4"]
   def __init__(self, name):
      Part.__init__(self, name)
      self.pins = {'1': Pin(self, Pin.INPUT),
                   '2': Pin(self, Pin.INPUT),
                   '3': Pin(self, Pin.INPUT),
                   '4': Pin(self, Pin.INPUT)}

class Part7400(Part):
   def __init__(self, name):
      Part.__init__(self, name)
      
class P74181(Part7400):
   matchingNames = ["74*181"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      self.pins = {'A0': Pin(self, Pin.INPUT),
                   'A1': Pin(self, Pin.INPUT),
                   'A2': Pin(self, Pin.INPUT),
                   'A3': Pin(self, Pin.INPUT),
                   'B0': Pin(self, Pin.INPUT),
                   'B1': Pin(self, Pin.INPUT),
                   'B2': Pin(self, Pin.INPUT),
                   'B3': Pin(self, Pin.INPUT),
                   'F0': Pin(self, Pin.OUTPUT),
                   'F1': Pin(self, Pin.OUTPUT),
                   'F2': Pin(self, Pin.OUTPUT),
                   'F3': Pin(self, Pin.OUTPUT),
                   'S0': Pin(self, Pin.INPUT),
                   'S1': Pin(self, Pin.INPUT),
                   'S2': Pin(self, Pin.INPUT),
                   'S3': Pin(self, Pin.INPUT),
                   'CN': Pin(self, Pin.INPUT),
                   'CN+4': Pin(self, Pin.OUTPUT),
                   'M': Pin(self, Pin.INPUT),
                   'A=B': Pin(self, Pin.OUTPUT),
                   'G': Pin(self, Pin.OUTPUT),
                   'P': Pin(self, Pin.OUTPUT)}

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
