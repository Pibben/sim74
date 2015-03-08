import xml.etree.ElementTree as ET
from partfactory import PartFactory
from core import Net

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
               gate   = pinrefOrWire.attrib['gate']
               pinstr = pinrefOrWire.attrib['pin']
               pin = parts[pinrefOrWire.attrib['part']].getPinByGate(gate, pinstr)
               net.addPin(pin)
   
   return parts, nets
