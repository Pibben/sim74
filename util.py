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
