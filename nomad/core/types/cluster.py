import networkx as nx
import  json
from nomad.core.graph.node import Node
from nomad.core.graph.link import Link
import logging

logger = logging.getLogger(__name__)

class Cluster(object):
    def __init__(self, graph=None):
        """
        :param nodes:
        :type nodes: core.graph.node
        :param links:
        :type links: core.graph.link
        :param graph:
        :type graph: NetworkXDiGraph
        """
        self.graph = graph

    @classmethod
    def read_cluster_spec(cls, nodes_path, links_path, edge_path):
        nodes_file = open(nodes_path)
        links_file = open(links_path)
        nodes_json = json.load(nodes_file)
        links_json = json.load(links_file)

        #create networkx graph
        graph = nx.read_weighted_edgelist(edge_path, create_using=nx.MultiDiGraph, nodetype=int)
        nodes = []#make dict
        links= {}

        #add Nodes
        for n in nodes_json:
            node = Node(n['label'], n['C'])
            graph.nodes[n['id']]['node'] =  node
            nodes.append(node)

        #add Links
        for l in links_json:
            link = Link(l['from'], l['to'], l['bandwidth'], l['latency'])
            graph[l['from']][l['to']][0]['link'] = link
            links[(l['from'],l['to'])] = link
            #links.append(link)

        #Close files
        nodes_file.close()
        links_file.close()

        #Create cluster
        return cls(nodes, links, graph)

    @classmethod
    def create_cluster(cls, node_list):
        #create node_objects
        nodes = [Node(label=label) for label in node_list]

        #create graph
        graph = nx.MultiDiGraph()

        #Add Nodes
        graph.add_nodes_from(node_list)

        #Add edges
        edges = []
        for i in range(len(node_list)):
            for j in range(len(node_list)):
                edges.append((node_list[i], node_list[j]))

        graph.add_edges_from(edges)

        #Assign node objects
        for i in range(len(node_list)):
            graph.node[node_list[i]]['node'] = nodes[i]

        return cls(graph)

    def update_links(self, links_json):
        """
        :param links_json:
        :type list of link dicts
        :return:
        """
        for l in links_json:
            link = Link(l['from'], l['to'], l['bandwidth'], l['latency'])
            try:
                self.graph[l['from']][l['to']][0]['link'] = link

            except Exception as e:
                logger.exception(e)
                logger.warning('Could not update link between node %s and %s' % (l['from'], l['to']) )


    def update_nodes(self, nodes_dict):
        for k,v in nodes_dict.items():
           try:
               node_label = k
               compute_capacity = v['C']
               if 'architecture' not in v:
                   arch = 'x86'
                   logger.warning("Architecture not found in specficiation, using default.")
               else:
                   arch = v['architecture']

               node = Node(label=node_label, C=compute_capacity, architecture=arch)
               self.graph.node[k]['node'] = node

           except Exception as e:
               logger.exception(e)
               logger.warning('Could not update node %s' % k)


    def get_node(self, label):
        return self.graph.node[label]['node']
