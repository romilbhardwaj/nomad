from abc import ABC, abstractmethod
import networkx as nx
from sys import maxsize
from copy import deepcopy
from pprint import pprint

class MinLatencySolver(ABC):
    @abstractmethod
    def find_optimal_placement(source, dest, operators):
        pass


class RecMinLatencySolver(MinLatencySolver):
    def __init__(self, graph):
        self._graph = graph

    def find_optimal_placement(self, source, dest, operators):
        ops_distribution = {}
        for node in self._graph.nodes():
            ops_distribution[node] = 0

        latency, placement, ops_dist = self.rec_placement_helper(source, dest, operators, ops_distribution)
        return  latency, placement, ops_dist

    def rec_placement_helper(self, source, dest, operators, ops_distribution):
        k = len(operators) - 1

        #No operators to place
        if operators == [] or operators == None:
            return maxsize, []

        #Base case 1: Placing 1 operator.
        if k == 0:
            ops_dist_copy = deepcopy(ops_distribution)
            #check if placement is feasible
            if source == dest:
                #cost of executing operators[0] at source
                op0 = operators[0]
                # Increment number of ops at source
                ops_dist_copy[source] += 1
                latency, placement = self._processing_time(source, op0, ops_dist_copy[source]), [source]

                return latency, placement, ops_dist_copy
            else:
                #no feasible placement
                return maxsize, [], ops_dist_copy

        #Base case 2: Placing 2 operators.
        if k == 1:
            ops_dist_copy = deepcopy(ops_distribution)

            if self._graph.has_edge(source, dest):
                op0 = operators[0]
                op1 = operators[1]
                # Increment the number of ops at source and dest
                ops_dist_copy[source] += 1
                ops_dist_copy[dest] += 1

                if source == dest:
                    #self loop
                    latency = self._processing_time(source, op0, ops_dist_copy[source]) + self._processing_time(dest, op1, ops_dist_copy[dest])
                else:
                    #cost executing op0 at source + cost of sending output of op0 to dest + cost executing op1 at dest
                    latency = self._processing_time(source, op0, ops_dist_copy[source]) + self._transfer_time(source, dest, op0.msg_size_bits()) + self._processing_time(dest, op1, ops_dist_copy[dest])

                placement = [source, dest]
                return latency, placement, ops_dist_copy

            else:
                #no feasible placement
                return maxsize, [], ops_dist_copy

        if k > 1:
            #Cost of executing operator[0] at source
            op0 = operators[0]
            #incremten the number of nodes at source
            ops_dist_copy = deepcopy(ops_distribution)
            ops_dist_copy[source] += 1
            #processing_time_src = self._processing_time(source, op0, ops_distribution[source])
            #increment number of operators at source
            #TODO: Wouldn't this update operators permanently, even though we might pick another path? Commenting out for now.
            # self._get_node(source).add_operator()

            #Loop over all neighbors
            min_latency, opt_placement, opt_ops_dist = maxsize, [], ops_dist_copy
            for nbr in self._graph.neighbors(source):

                nbr_latency, nbr_placement, nbr_ops_dist = self.rec_placement_helper(nbr, dest, operators[1:], ops_dist_copy)
                # If nbr == source we ignore the cost of sending the output of prev op across a link (self-loop)
                if nbr == source:
                    total_latency = self._processing_time(source, op0, nbr_ops_dist[source]) + nbr_latency
                else:
                    total_latency = self._processing_time(source, op0, nbr_ops_dist[source]) + self._transfer_time(source, nbr, op0.msg_size_bits()) + nbr_latency

                # Check if we have found a less expensive placement
                if (total_latency < min_latency):
                        min_latency = total_latency
                        opt_placement = [source] + nbr_placement
                        opt_ops_dist  = nbr_ops_dist

            return min_latency, opt_placement, opt_ops_dist

    def _get_node(self, vertex):
        return self._graph.nodes[vertex]['node']

    def _get_link(self, u, v):
        return self._graph[u][v][0]['link']

    def _processing_time(self, vertex, operator, ops_count):
        return self._get_node(vertex).processing_time(operator, ops_count)
    
    def _transfer_time(self, start, end, bits):
        # Self loop condition
        if start == end:
            return 0
        return self._get_link(start, end).transfer_time(bits)