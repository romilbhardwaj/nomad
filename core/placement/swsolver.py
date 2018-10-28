from abc import ABC, abstractmethod
import networkx as nx
from sys import maxsize
from pprint import pprint

class ShortestWalkSolver(ABC):
    @classmethod
    @abstractmethod
    def shortest_walk(cls, graph, source, dest, k):
        pass
    

class RecShortestWalkSolver(ShortestWalkSolver):
    @classmethod
    def shortest_walk(cls, graph, source, dest, k):
        """
        Return the shortest walk or length k from source to dest.
        If no such walk exist, return maxsize, [].
        """
        #Base cases
        if k == 0:
            return 0, []

        if k == 1:
            if graph.has_edge(source, dest):
                return graph[source][dest][0]['weight'], [source, dest]
            else:
                return maxsize, []

        if k > 1:
            shortest_walk_weight, shortest_walk = maxsize, [] 
            
            #Loop over all neighbors 
            for nbr in graph.neighbors(source):
                curr_walk_weight, curr_walk = cls.shortest_walk(graph, nbr, dest, k - 1)
                if curr_walk_weight < shortest_walk_weight:
                    shortest_walk_weight = graph[source][nbr][0]['weight'] + curr_walk_weight 
                    shortest_walk = [source] + curr_walk
            
            return shortest_walk_weight, shortest_walk

