from abc import ABC, abstractmethod
import networkx as nx
from sys import maxsize
from pprint import pprint

class MinLatencySolver(ABC):
    @abstractmethod
    def find_optimal_placement(source, dest, operators):
        pass


class RecMinLatencySolver(MinLatencySolver):
    def __init__(self, graph):
        self._graph = graph

    def find_optimal_placement(self, source, dest, operators):
        k = len(operators) - 1

        #No operators to place
        if operators == [] or operators == None:
            return maxsize, []

        #Base case 1: Placeing 1 operator. 
        if k == 0:
            #check if placement is feasible
            if source == dest:
                #cost of executing operators[0] at source
                op0 = operators[0]
                latency, placement = self._processing_time(source, op0), [source] 
                #Increment number of ops at source
                self._get_node(source).add_operator()
                return latency, placement
            else:
                #no feasible placement
                maxsize, []

        #Base case 2: Placeing 2 operators.
        if k == 1:
            if self._graph.has_edge(source, dest):
                op0 = operators[0]
                op1 = operators[1]

                #cost executing op0 at source + cost of sending output of op0 to dest + cost executing op1 at dest
                latency = self._processing_time(source, op0) + self._transfer_time(source, dest, op1.msg_size_bits()) + self._processing_time(dest, op1)
                placement = [source, dest]

                #Increment the number of ops at source and dest
                self._get_node(source).add_operator() 
                self._get_node(dest).add_operator()
                return latency, placement

            else:
                #no feasible placement
                return maxsize, []

        if k > 1:
            #Cost of executing operator[0] at source
            op0 = operators[0]
            processing_time_src = self._processing_time(source, op0)
            #increment number of operators at source
            self._get_node(source).add_operator()

            #Loop over all neighbors 
            min_placement_latency, opt_placement = maxsize, []
            for nbr in self._graph.neighbors(source):
                curr_placement_latency, curr_placement = self.find_optimal_placement(nbr, dest, operators[1:])
                #Check if we have found a less expensive placement
                if (curr_placement_latency < min_placement_latency):
                    # If nbr == source we ignore the cost of sending the ouput of prev op across a link.(self-loop)
                    if nbr == source:
                        #cost of executing operators[0] at source + curr_placement_latency
                        min_placement_latency = processing_time_src + curr_placement_latency
                        opt_placement = [source] + curr_placement
                    else:
                        #cost of executing op0 at source + cost of sending output of op0 to nbr + curr_placement_latency
                        min_placement_latency = processing_time_src + self._transfer_time(source, nbr, op0.msg_size_bits()) + curr_placement_latency
                        opt_placement = [source] + curr_placement
            
            return min_placement_latency, opt_placement

    def _get_node(self, vertex):
        return self._graph.nodes[vertex]['node']

    def _get_link(self, u, v):
        return self._graph[u][v][0]['link']

    def _processing_time(self, vertex, operator):
        return self._get_node(vertex).processing_time(operator)
    
    def _transfer_time(self, start, end, bits):
        return self._get_link(start, end).transfer_time(bits)