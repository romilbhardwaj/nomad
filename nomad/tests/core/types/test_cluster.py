import unittest
from core.types.cluster import Cluster
class TestClusterMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = open("tests/core/types/nodes.json")
        self.link_info = open('tests/core/types/links.json')
        self.graph_topo = open('tests/core/types/graph_topology.txt')

    def tearDown(self):
        self.node_info.close()
        self.link_info.close()
        self.graph_topo.close()

    def test_create_universe(self):
        cluster = Cluster.read_cluster_spec('tests/core/types/nodes.json','tests/core/types/links.json', 'tests/core/types/graph_topology.txt')
        self.assertTrue(cluster.nodes != None)


if __name__ == '__main__':
    unittest.main()