import networkx as nx
import  json
from core.graph.node import Node
from core.graph.link import Link

class Cluster(object):
    def __init__(self, nodes, links, graph):
        """

        :param nodes:
        :type nodes: core.graph.node
        :param links:
        :type links: core.graph.link
        :param graph:
        :type graph: NetworkXDiGraph
        """
        self.nodes = nodes
        self.links = links
        self.graph = graph

    @classmethod
    def read_cluster_spec(cls, nodes_path, links_path, edge_path):
        nodes_file = open(nodes_path)
        links_file = open(links_path)
        nodes_json = json.load(nodes_file)
        links_json = json.load(links_file)

        #create networkx graph
        graph = nx.read_weighted_edgelist(edge_path, create_using=nx.MultiDiGraph, nodetype=int)
        nodes = []
        links= []

        #add Nodes
        for n in nodes_json:
            node = Node(n['label'], n['C'])
            graph.nodes[n['id']]['node'] =  node
            nodes.append(node)

        #add Links
        for l in links_json:
            link = Link(l['from'], l['to'], l['bandwidth'], l['latency'])
            graph[l['from']][l['to']][0]['link'] = link
            links.append(link)

        #Close files
        nodes_file.close()
        links_file.close()

        #Create cluster
        return cls(nodes, links, graph)

