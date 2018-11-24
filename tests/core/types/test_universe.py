import unittest
from core.universe.universe import Universe
class TestUniverseMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = open("tests/types/nodes.csv")
        self.link_info = open('tests/types/links.csv')
        self.pipeline_info = open('tests/types/pipeline.csv')
        self.graph_topo = open('tests/types/graph_topology.txt')

    def tearDown(self):
        self.node_info.close()
        self.link_info.close()
        self.pipeline_info.close()
        self.graph_topo.close()

    def test_create_universe(self):
        universe = Universe.create_universe(self.node_info, self.link_info,  self.graph_topo)
        self.assertTrue(universe.cluster != None)


if __name__ == '__main__':
    unittest.main()