import unittest
from core.universe.universe import Universe
class TestUniverseMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = open("tests/core/types/nodes.json")
        self.link_info = open('tests/core/types/links.json')
        self.pipeline_info = open('tests/core/types/pipeline.json')
        self.graph_topo = open('tests/core/types/graph_topology.txt')

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