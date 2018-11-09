import unittest
from core.graph.diedge import DirectedEdge 

class TestDirectedEdgeMethods(unittest.TestCase):
    def setUp(self):
        v = 1
        w = 2
        weight = 2.5
        self.edge = DirectedEdge(v, w, weight)

    def test_to_sting(self):
        print(self.edge.to_string())

    def test_from(self):
        self.assertEqual(self.edge.tail(), 1)

    def test_to(self):
        self.assertEqual(self.edge.head(), 2)     

    

if __name__ == '__main__':
    unittest.main()        




