
import xml.etree.ElementTree as ET

def bitsToInt(*bits):
   val = 0
   for i in range(len(bits)):
      val = (val << 1) | bits[i]
      
   #print(str(bits) + " -> %d" % val)
      
   return val

def intToBits(integer, num):
   retval = []
   for i in range(num):
      retval.append((integer >> (num-i-1)) & 1)
      
   #print("%d -> " % integer + str(retval))
      
   return retval


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
   
   def getValue(self):
      for p in self.terminals:
         if p.direction == Pin.OUTPUT:
            p.update()
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
      
   def update(self):
      pass
   
   def getValue(self):
      if self.direction == Pin.OUTPUT:
         self.part.update()
         #print("%s:%s: %d" % (self.part.name, self.name, self.value))
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
      self.width = 4
      
   def update(self):
      pass
   
   def setWidth(self, width):
      self.width = width
      
   def setDirection(self, direction):
      self.direction = direction
      for p in self.pins.values():
         p.setDirection(direction)
         
   def setNumber(self, number):
      bits = intToBits(number, self.width)
      #print(bits)
      
      for i in range(self.width):
         self.pins[str(i+1)].setValue(bits[self.width-1-i])

   def getNumber(self):
      bits = [self.pins[str(i+1)].getValue() for i in range(self.width-1,-1,-1)]
      #print(bits)
      retval = bitsToInt(*bits)
      #print("%s: %d" % (self.name, retval))
      return retval

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
      a = bitsToInt(*[self.pins[name].getValue() for name in ['A3', 'A2', 'A1', 'A0']])
      b = bitsToInt(*[self.pins[name].getValue() for name in ['B3', 'B2', 'B1', 'B0']])
      s = bitsToInt(*[self.pins[name].getValue() for name in ['S3', 'S2', 'S1', 'S0']])
      c = self.pins['CN'].getValue()
      m = self.pins['M'].getValue()
      
      f = a + b
      
      bits = intToBits(f, 4)

      self.pins['F0'].setValue(bits[3])
      self.pins['F1'].setValue(bits[2])
      self.pins['F2'].setValue(bits[1])
      self.pins['F3'].setValue(bits[0])
      
      #print("%s: %d + %d = %d" % (self.name, a, b, f))
      
   def getDAG(self, _):
      return [pins[name] for name in ['F0', 'F1', 'F2', 'F3', 'CN+4', 'A=B', 'G', 'P']]
      
      
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
               pin = parts[pinrefOrWire.attrib['part']].getPin(pinrefOrWire.attrib['pin'])
               net.addPin(pin)
               pin.setNet(net)
         
   #for net in nets:
   #   print(net)
         
   #for part in parts.values():
   #   print(part)
   
   return parts, nets
   
if __name__ == '__main__':
   parts, nets = parseXml('/home/per/eagle/test.sch')

   parts['IN_A'].setDirection(Pin.OUTPUT)
   parts['IN_A'].setWidth(8)
   parts['IN_B'].setDirection(Pin.OUTPUT)
   parts['IN_B'].setWidth(8)
   
   parts['IN_S'].setDirection(Pin.OUTPUT)
   parts['IN_S'].setNumber(0)
   
   parts['OUT_F'].setWidth(8)

   parts['IN_A'].setNumber(3)
   parts['IN_B'].setNumber(2)
   
   print(parts['OUT_F'].getNumber())
   
   parts['IN_A'].setNumber(4)
   parts['IN_B'].setNumber(5)
   
   print(parts['OUT_F'].getNumber())
