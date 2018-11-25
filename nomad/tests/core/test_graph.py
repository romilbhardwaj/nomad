import unittest
from core.graph.digraph import DirectedGraph 

class TestGraphMethods(unittest.TestCase):
    def setUp(self):
        graph_file = open("tests/core/test-graph_1.txt", 'r')
        self._graph1 = DirectedGraph.from_file(graph_file)

    def test_to_sting(self):
        pass
        
if __name__ == '__main__':
    unittest.main()        