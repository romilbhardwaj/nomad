import unittest
from core.types.cluster import Cluster
class TestClusterMethods(unittest.TestCase):
    def setUp(self):
        self.node_info = open("tests/core/types/nodes.json")
        self.link_info = open('tests/core/types/links.json')
        self.graph_topo = open('tests/core/types/graph_topology.txt')
        self.cluster = Cluster.read_cluster_spec('tests/core/types/nodes.json','tests/core/types/links.json', 'tests/core/types/graph_topology.txt')

    def tearDown(self):
        self.node_info.close()
        self.link_info.close()
        self.graph_topo.close()

    def test_create_universe(self):
        self.assertTrue(len(self.cluster.nodes) == 4)
        self.assertTrue(len(self.cluster.links) == 5)

    def test_update_links(self):
        #Update existing links
        links_json = [
            {
                "from": 0,
                "to": 1,
                "bandwidth": 10,
                "latency": 0.1

            },
            {
                "from": 0,
                "to": 3,
                "bandwidth": 20,
                "latency": 0.05

            }
        ]
        link_01 = self.cluster.graph[0][1][0]['link']
        link_03 = self.cluster.graph[0][3][0]['link']
        self.assertTrue(link_01._bandwidth == 5)
        self.assertTrue(link_01._latency == 0.05)
        self.assertTrue(link_03._bandwidth == 50)
        self.assertTrue(link_03._latency == 0.05)

        self.cluster.update_links(links_json)

        link_01 = self.cluster.graph[0][1][0]['link']
        link_03 = self.cluster.graph[0][3][0]['link']
        self.assertTrue(link_01._bandwidth == 10)
        self.assertTrue(link_01._latency == 0.1)
        self.assertTrue(link_03._bandwidth == 20)
        self.assertTrue(link_03._latency == 0.05)

        #Update link between one or more non-existing nodes ( should fail )
        links_json = [
            {
                "from": 0,
                "to": 100,
                "bandwidth": 10,
                "latency": 0.1

            }
        ]

        #Update link between existing nodes with no previous link info.


if __name__ == '__main__':
    unittest.main()