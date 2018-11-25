import unittest
import networkx as nx
from core.placement.spsolver import DPShortestPathSolver

class TestShorthestPathSolverMethods(unittest.TestCase):
    def setUp(self):
        self.g1 = nx.read_weighted_edgelist('tests/test-graph_1.txt', create_using=nx.MultiDiGraph, nodetype=int)

    def test_shortest_path(self):
        u = 0
        v = 3
        k = 2
        weight_shortest_path = 9
        (weight, path) = DPShortestPathSolver.shortest_path(self.g1, u, v, k)
        self.assertEqual(weight, weight_shortest_path)
        self.assertEqual(path, [0, 2, 3])



if __name__ == '__main__':
    unittest.main()        