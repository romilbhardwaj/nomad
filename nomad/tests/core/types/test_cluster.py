import unittest
from core.types.cluster import Cluster
class TestClusterMethods(unittest.TestCase):
    def setUp(self):
        self.node_list = ['phone', 'base_station', 'cloud', 'pc']
        self.cluster = Cluster.create_cluster(self.node_list)

    def test_create_cluster(self):
        self.assertTrue(len(self.cluster.graph.edges) == 16)

    def test_update_links(self):
        #Update existing links
        links_json = [
            {
                "from": 'phone',
                "to": 'base_station',
                "bandwidth": 10,
                "latency": 0.1

            },
            {
                "from": 'phone',
                "to": 'cloud',
                "bandwidth": 20,
                "latency": 0.05

            }
        ]
        link_phone_base = self.cluster.graph['phone']['base_station'][0]
        link_phone_cloud = self.cluster.graph['phone']['cloud'][0]

        self.cluster.update_links(links_json)

        self.assertTrue(link_phone_base['link']._latency == 0.1)
        self.assertTrue(link_phone_base['link']._bandwidth == 10)
        self.assertTrue(link_phone_cloud['link']._latency == 0.05)
        #Update link between one or more non-existing nodes ( should fail )
        links_json = [
            {
                "from": 'phone',
                "to": 'cloud_3',
                "bandwidth": 10,
                "latency": 0.1

            }
        ]

        #Update link between existing nodes with no previous link info.
        self.cluster.update_links(links_json)

    def test_update_nodes(self):
        nodes =['phone', 'cloud', 'base_station', 'pc']

        node_info = {
            "phone": {
              "C": 0.2,
              "architecture": "arm"
            },

            "cloud": {
              "C": 1.0,
              "architecture": "x86"
            },

            "base_station": {
              "C": 0.7,
              "architecture": "x86"
            },

            "pc": {
              "C": 0.4,
              "architecture": "x86"
            }
        }

        self.cluster.update_nodes(node_info)

        for k, v in node_info.items():
            self.assertEqual(self.cluster.graph.node[k]['node']._C, v['C'])


    def test_get_node(self):
        node_info = {
            "phone": {
                "C": 0.2,
                "architecture": "arm"
            },

            "cloud": {
                "C": 1.0,
                "architecture": "x86"
            },

            "base_station": {
                "C": 0.7,
                "architecture": "x86"
            },

            "pc": {
                "C": 0.4,
                "architecture": "x86"
            }
        }

        self.cluster.update_nodes(node_info)

        node = self.cluster.get_node('cloud')
        self.assertEqual(node._C, 1.0)

if __name__ == '__main__':
    unittest.main()