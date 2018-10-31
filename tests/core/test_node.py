import unittest
from core.graph.node import Node
from core.operator import Operator

class TestNodeMethods(unittest.TestCase):
    def setUp(self):
        C = 0.8 #CPU speed relative to cloud env.
        label = 'c.5.large'
        cpu = 2 #GHz
        self.node = Node(label, C) 

    def test_processing_time(self):
        label = 'resampling'
        cloud_execution_time = 5000 #milliseconds
        output_msg_size = 1000 #Kb - kilobytes
        operator = Operator(label, cloud_execution_time, output_msg_size)
        processing_time = 6.25
        self.assertAlmostEqual(self.node.processing_time(operator), processing_time)

    def test_to_sting(self):
        pass 
        
if __name__ == '__main__':
    unittest.main()        