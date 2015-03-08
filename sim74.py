
from parsexml import parseXml
from toposort import toposort, toposort_flatten

from core import Pin
   
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

   totalDAGs = {}
   
   for p in parts.values():
      totalDAGs.update(p.getDAGs())
      
   for n in nets:
      totalDAGs.update(n.getDAG())

   sorted = toposort_flatten(totalDAGs)
   sorted.reverse()
   
   for s in sorted:
      if s.direction == Pin.OUTPUT and s.net:
         s.part.update()

      
   print(parts['OUT_F'].getNumber())
   
   parts['IN_A'].setNumber(86)
   parts['IN_B'].setNumber(47)
   
   for s in sorted:
      if s.direction == Pin.OUTPUT and s.net:
         s.part.update()
         
         
   print(parts['OUT_F'].getNumber())
