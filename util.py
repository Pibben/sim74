def bitsToInt(*bits):
   val = 0
   for bit in bits:
      val = (val << 1) | bit
      
   #print(str(bits) + " -> %d" % val)
      
   return val

def intToBits(integer, num):
   retval = []
   for i in range(num):
      retval.append((integer >> (num-i-1)) & 1)
      
   #print("%d -> " % integer + str(retval))
      
   return retval

class BinaryBus:
   def __init__(self, *pins):
      self.pins = pins

   def setValue(self, value):
      for bit,pin in zip(intToBits(value, len(self.pins)), self.pins):
         pin.setValue(bit)

   def getValue(self):
      return bitsToInt(*(pin.getValue() for pin in self.pins))

   def connect(self, bus):
      assert len(self.pins) == len(bus.pins)
      for p1, p2 in zip(self.pins, bus.pins):
         p1.connect(p2)
