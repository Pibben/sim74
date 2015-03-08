
from system import System

def testALU():
   s = System('/home/per/eagle/test.sch')
   
   s.setInput('IN_A', 8)
   s.setInput('IN_B', 8)
   s.setInput('IN_S', 8)
   s.setOutput('OUT_F', 8)
   
   s.run(3, 2, 0)
   s.run(86, 47, 0)
   
if __name__ == '__main__':
   testALU()
