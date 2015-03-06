
import xml.etree.ElementTree as ET

def bitsToInt(*bits):
   val = 0
   for i in range(len(bits)):
      val = (val << 1) | bits[i]
      
   return val

class Pin(object):
   INPUT = 0
   OUTPUT = 1
   TRISTATE = 2
   
   def __init__(self, direction):
      self.direction = direction
      self.connected = []
      self.value = 0
      
   def addConnection(self, part):
      self.connected.append(part)
      
   def __repr__(self):
      connectedTo = [p.name for p in self.connected]
      return '\n'.join(connectedTo)
   
   def update(self):
      pass
   
   def getValue(self):
      return self.value

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
      self.pins = {'1': Pin(Pin.INPUT),
                   '2': Pin(Pin.INPUT),
                   '3': Pin(Pin.INPUT),
                   '4': Pin(Pin.INPUT)}

class Part7400(Part):
   def __init__(self, name):
      Part.__init__(self, name)
      
class P74181(Part7400):
   matchingNames = ["74*181"]
   
   def __init__(self, name):
      Part7400.__init__(self, name)
      self.pins = {'A0': Pin(Pin.INPUT),
                   'A1': Pin(Pin.INPUT),
                   'A2': Pin(Pin.INPUT),
                   'A3': Pin(Pin.INPUT),
                   'B0': Pin(Pin.INPUT),
                   'B1': Pin(Pin.INPUT),
                   'B2': Pin(Pin.INPUT),
                   'B3': Pin(Pin.INPUT),
                   'F0': Pin(Pin.OUTPUT),
                   'F1': Pin(Pin.OUTPUT),
                   'F2': Pin(Pin.OUTPUT),
                   'F3': Pin(Pin.OUTPUT),
                   'S0': Pin(Pin.INPUT),
                   'S1': Pin(Pin.INPUT),
                   'S2': Pin(Pin.INPUT),
                   'S3': Pin(Pin.INPUT),
                   'CN': Pin(Pin.INPUT),
                   'CN+4': Pin(Pin.OUTPUT),
                   'M': Pin(Pin.INPUT),
                   'A=B': Pin(Pin.OUTPUT),
                   'G': Pin(Pin.OUTPUT),
                   'P': Pin(Pin.OUTPUT)}

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
   nets  = root.findall("./drawing/schematic/sheets/sheet/nets/net/segment")
   
   pf = PartFactory()

   parts = {part.attrib['name']: pf.createPart(part.attrib['deviceset'], part.attrib['name']) for part in parts}
   
   for net in nets:
      pinrefs = net.findall('pinref')
      connectedParts = [parts[pinref.attrib['part']] for pinref in pinrefs]
      for pinref in pinrefs:
         for part in connectedParts:
            thisPart = parts[pinref.attrib['part']]
            if thisPart != part:
               thisPart.getPin(pinref.attrib['pin']).addConnection(part)
               
               
   for part in parts.values():
      print(part)
   
if __name__ == '__main__':
   parseXml('/home/per/eagle/test.sch')
