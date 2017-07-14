from p74xx import P74181,P7404,P7408,P74161,P74244,P74374
from header import Header
from memory import CY62256LL

class PartFactory(object):
   def createPart(self, device, name):
      #print("%s %s" % (device, name))
      if device in P7404.matchingNames:
         return P7404(name)
      if device in P7408.matchingNames:
         return P7408(name)
      if device in P74161.matchingNames:
         return P74161(name)
      if device in P74181.matchingNames:
         return P74181(name)
      if device in P74244.matchingNames:
         return P74244(name)
      if device in P74374.matchingNames:
         return P74374(name)
      if device in CY62256LL.matchingNames:
         return CY62256LL(name)
      if device in Header.matchingNames:
         return Header(name, device)
      else:
         print("Unknown part %s %s" % (device, name))
         assert False
         return None
    
    