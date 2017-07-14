
from system import System

def testALU():
   s = System('/home/per/eagle/test.sch')
   
   s.setInput('IN_A')
   s.setInput('IN_B')
   s.setInput('IN_S')
   s.setOutput('OUT_F')
   
   s.run(3, 2, 0)
   s.run(86, 47, 0)
   
def testMemory():
   s = System('/home/per/eagle/memory.sch')
   
   s.setInput('CLK')
   s.setOutput('OUT')
   s.setHigh('V4', 'ENT')
   s.setHigh('V4', 'ENP')
   
   for i in range(5):
      s.run(1)
      s.run(0)
      
def testCPU():
   s = System('/home/per/eagle/cpu.sch')
   
   s.setInput('CLK')
   s.setInput('R/W')
   s.setOutput('OUT_F')
   
   for i in range(5):
      s.run(1, 0)
      s.run(0, 0)
   
if __name__ == '__main__':
   #testALU()
   #testMemory()
   testCPU()