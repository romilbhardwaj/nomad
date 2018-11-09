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
