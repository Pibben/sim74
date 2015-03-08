
from parsexml import parseXml
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
   
   partOrder = ['IN_A', 'IN_B', 'IN_S', 'ALU1', 'ALU2', 'OUT_F']

   for p in partOrder:
      parts[p].update()
      
   print(parts['OUT_F'].getNumber())
   
   parts['IN_A'].setNumber(86)
   parts['IN_B'].setNumber(47)
   
   for p in partOrder:
      parts[p].update()
      
   print(parts['OUT_F'].getNumber())
   
      