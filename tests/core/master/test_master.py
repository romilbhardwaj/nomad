import unittest
from core.master.master import Master
from core.universe.universe import Universe

class TestMasterMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = "tests/core/types/nodes.json"
        self.link_info = 'tests/core/types/links.json'
        self.pipeline_info = 'tests/core/types/pipeline.json'
        self.graph_topo = 'tests/core/types/graph_topology.txt'
        self.universe = Universe.create_universe(self.node_info, self.link_info,  self.graph_topo)
        self.master = Master(self.universe)

    def test_submit_pipeline(self):
        fns = ['fn1.txt', 'fn2.txt', 'fn3.txt']
        start = 1
        end = 4
        pipeline_id = self.master.submit_pipeline(fns, start, end)

        pipeline = self.master.universe.pipelines[pipeline_id]

        self.assertTrue(pipeline.operator_instances != [])

if __name__ == '__main__':
    unittest.main()
