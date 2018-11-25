import unittest
import networkx as nx
from core.placement.swsolver import RecShortestWalkSolver 

class TestShorthestWalkSolverMethods(unittest.TestCase):
    def setUp(self):
        self.g1 = nx.read_weighted_edgelist('tests/test_graph_2.txt', create_using=nx.MultiDiGraph, nodetype=int)

    def test_shortest_walk(self):
        u = 0
        v = 3
        k = 1
        weight_shortest_walk = 2
        (weight, walk) = RecShortestWalkSolver.shortest_walk(self.g1, u, v, k)
        print(walk)
        self.assertEqual(weight, weight_shortest_walk)
        self.assertEqual(walk, [0, 3])

        u = 0
        v = 3
        k = 2
        weight_shortest_walk = 3
        (weight, walk) = RecShortestWalkSolver.shortest_walk(self.g1, u, v, k)
        print(walk)
        self.assertEqual(weight, weight_shortest_walk)
        self.assertEqual(walk, [0, 0, 3])

if __name__ == '__main__':
    unittest.main()        