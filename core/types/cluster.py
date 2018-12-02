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
        #TODO: links should be a dictionary mapping a tuple (from,to) -> core.graph.link
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
                #update links dict.
                self.links[(l['from'],l['to'])] = link

            except Exception as e:
                print(e)
                print('Could not update link between node %s and %s' % (l['from'], l['to']) )
