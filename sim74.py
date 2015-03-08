
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
   
   s.run(1)
   s.run(1)
   
if __name__ == '__main__':
   #testALU()
   testMemory()
