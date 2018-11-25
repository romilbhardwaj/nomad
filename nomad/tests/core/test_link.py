import unittest
from core.graph.link import Link

class TestLinkMethods(unittest.TestCase):
    def setUp(self):
        bandwidth = 200 #Mb/s
        latency = 100 # ms
        self.link = Link(bandwidth, latency) 

    def test_transfer_time(self):
        msg_size_bits = 1000 
        transfer_time = 0.100005
        self.assertAlmostEqual(self.link.transfer_time(msg_size_bits), transfer_time)
    def test_to_sting(self):
        pass 
        
    

if __name__ == '__main__':
    unittest.main()        