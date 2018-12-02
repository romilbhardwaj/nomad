import unittest
from core.universe.universe import Universe
class TestUniverseMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = open("tests/core/types/nodes.json")
        self.link_info = open('tests/core/types/links.json')
        self.pipeline_info = open('tests/core/types/pipeline.json')
        self.graph_topo = open('tests/core/types/graph_topology.txt')
        self.universe = Universe.create_universe(self.node_info, self.link_info,  self.graph_topo)

    def tearDown(self):
        self.node_info.close()
        self.link_info.close()
        self.pipeline_info.close()
        self.graph_topo.close()

    def test_create_universe(self):
        self.assertTrue(self.universe.cluster != None)

    def test_add_pipeline(self):
        fns = ['fn1.txt', 'fn2.txt', 'fn3.txt']
        start = 1
        end = 4
        pid = self.universe.add_pipeline(fns, start, end)
        pipeline = self.universe.get_pipeline(pid)
        self.assertTrue(len(pipeline.operators) == 3)


if __name__ == '__main__':
    unittest.main()