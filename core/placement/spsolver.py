from abc import ABC, abstractmethod
import networkx as nx
from sys import maxsize
from pprint import pprint

class ShortestPathSolver(ABC):
    """
    Class used to find the shortest path of length k from sorce u to destination v in a directed edge weighted graph.
    """
    def __init__(self):
        pass 
    
    @classmethod
    @abstractmethod
    def shortest_path(cls, graph, source, dest, k):
        pass


class DPShortestPathSolver(ShortestPathSolver):
    @classmethod
    def shortest_path(cls, graph, source, dest, k):
        """
         Returns shortest path from source to dest of length k. If no such path exist,
         the function returns sys.maxsize, [].
         Based on this implementation: https://www.geeksforgeeks.org/shortest-path-exactly-k-edges-directed-weighted-graph/ 
        """
        #TODO: test implementation more extensively
        V = graph.number_of_nodes()
        #Table to memoize results from DP. memo_table[i][j][e] corresponds to the shortest path 
        # between node i and node j of length e
        memo_table = [[[maxsize for k in range(k+1)] for j in range(V)] for i in range(V)]
        #Tabled used to reconstruct the path 
        path = [[[[] for k in range(k+1)] for j in range(V)] for i in range(V)] 
        
        #Loop for num edges from 0 to k 
        for e in range(k+1):
            #for source
            for s in range(V):
                # for destination
                for d in range(V):
                    if(e == 0 and s == d):
                        memo_table[s][d][e] = 0
                        path[s][d][e].append(s)

                    if(e == 1 and graph.has_edge(s,d)):
                        memo_table[s][d][e] = graph[s][d][0]['weight']
                        path[s][d][e] = [s,d] 

                    if e > 1:
                        #Loop over ever neighbor of s
                        for nbr in graph.neighbors(s):
                            if nbr != d and memo_table[nbr][d][e-1] != maxsize:
                                if memo_table[s][d][e] > graph[s][nbr][0]['weight'] + memo_table[nbr][d][e-1]:
                                    memo_table[s][d][e] = graph[s][nbr][0]['weight'] + memo_table[nbr][d][e-1] 
                                    path[s][d][e] = [s] + path[nbr][d][e-1]
        
        if (memo_table[source][dest][k] != maxsize):
            return memo_table[source][dest][k], path[source][dest][k]
        else:
            return maxsize, []




    
  
        

    