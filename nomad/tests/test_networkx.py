import unittest
import networkx as nx
import matplotlib.pyplot as plt

class TestNXMethods(unittest.TestCase):
    def setUp(self):
        pass
    def test_has_edge(self):
       G = nx.Graph()
       G.add_nodes_from([1,2])
       G.add_edge(1,2)
       print(G.edges)
       print(list(G.neighbors(1)))
       print(list(G.neighbors(2)))

       self.assertAlmostEqual(G.number_of_edges(), 1)

    def test_read_from_file(self):
        G = nx.read_weighted_edgelist('tests/test-graph_1.txt', create_using=nx.MultiDiGraph, nodetype=int, )
        print(nx.info(G))
        print(G[0][1][0]['weight'])
        for n1,n2,attr in G.edges(data=True):
            print(n1,n2,attr)
        

if __name__ == '__main__':
    unittest.main()        