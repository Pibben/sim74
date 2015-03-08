from p74xx import P74181,P7404
from header import Header

class PartFactory(object):
   def createPart(self, device, name):
      #print("%s %s" % (device, name))
      if device in P74181.matchingNames:
         return P74181(name)
      if device in P7404.matchingNames:
         return P7404(name)
      if device in Header.matchingNames:
         return Header(name, device)
      else:
         print("Unknown part %s %s" % (device, name))
         assert False
         return None
    
    