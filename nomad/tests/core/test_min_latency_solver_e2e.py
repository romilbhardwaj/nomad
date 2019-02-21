import unittest
import networkx as nx
from nomad.core.placement.minlatsolver import RecMinLatencySolver
from nomad.core.graph.link import Link
from nomad.core.graph.node import Node
from nomad.core.types.operator import Operator

class TestMinLatencySolverMethods(unittest.TestCase):
    def setUp(self):
        self.links = {
            (0,1): {
                'bw': 1000000, #B/s
                'lat': 0.3 #s
            }, 
            (1,0): {
                'bw': 1000000, #B/s
                'lat': 0.3 #s
            }
        }

        self.node_info = [
            { 
                'label': 'rpi',
                'C': 0.1
            },

            { 
                'label': 'x1',
                'C': 1
            }
        ]

        self.pipeline_info = [
            {
                'label': 'Pre processing',
                'cloud_execution_time': 10, #s
                'output_msg_size': 100, #bytes,
            },
            {
                'label': 'Resampling',
                'cloud_execution_time': 5, #s
                'output_msg_size': 5, #bytes,
            },

            {
                'label': 'Inference',
                'cloud_execution_time': 1, #s
                'output_msg_size': 1, #bytes
            }
        ]

        self.g1 = nx.read_weighted_edgelist('../test_graph_3.txt', create_using=nx.MultiDiGraph, nodetype=int)
        #Add links:
        #curr_link = self.links[(0,1)]
        #self.g1[0][1][0]['link'] = Link(curr_link['bw'], curr_link['lat'])
        #curr_link = self.links[(0,2)]
        #self.g1[0][2]['link'] = Link(curr_link['bw'], curr_link['lat'])
        #curr_link = self.links[(0,3)]
        #self.g1[0][3]['link'] = Link(curr_link['bw'], curr_link['lat'])
        #curr_link = self.links[(1,3)]
        #self.g1[1][3]['link'] = Link(curr_link['bw'], curr_link['lat']) 
        #curr_link = self.links[(2,3)]
        #self.g1[2][3]['link'] = Link(curr_link['bw'], curr_link['lat']) 

        for u in range(self.g1.number_of_nodes()):
            for v in range(self.g1.number_of_nodes()):
                if (u,v) in self.links.keys():
                    curr_link = self.links[(u,v)]
                    self.g1[u][v][0]['link'] = Link(curr_link['bw'], curr_link['lat'])

        #Add Node info:
        for i in range(self.g1.number_of_nodes()):
            self.g1.nodes[i]['node'] = Node(self.node_info[i]['label'], self.node_info[i]['C'])
            print(self.g1.nodes[i])
        
        #Create operators:
        self.operator_list = []
        for i in range(len(self.pipeline_info)):
            op = self.pipeline_info[i]
            self.operator_list.append(Operator(op['label'], op['cloud_execution_time'], op['output_msg_size']))
    

    def test_shortest_walk(self):
        u = 0
        v = 3
        k = len(self.pipeline_info) - 1 
        total_latency = 2
        solver = RecMinLatencySolver(self.g1)
        (total_latency, placement) = solver.find_optimal_placement(u, v, self.operator_list)
        print('seconds:',total_latency, placement)


if __name__ == '__main__':
    unittest.main()    