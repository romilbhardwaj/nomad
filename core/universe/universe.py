from core.types.cluster import Cluster

class Universe(object):
    def __init__(self, cluster):
        """

        :param cluster: The cluster info
        :type cluster: ClusterObj
        """
        self.pipelines = []
        self.cluster = cluster

    def get_next_operator(self, client_guid):
        for pipeline in self.pipelines:
            for operator_instance in pipeline.operator_instances:
                if client_guid == operator_instance.client_guid:
                    operator_to_find = operator_instance.operator
                    next_operator_instance = pipeline.operator_instance[pipeline.operators.index(operator_to_find) + 1]  # Assuming ordering on operator_instance is the same as operators
                    return next_operator_instance
        raise Exception("No next operator.")

    @classmethod
    def create_universe(cls, node_file, links_file, graph_topo_file):
        """

        :param node_file: JSON file containing node info
        :param links_file: JSON file containing link info
        :param graph_topo_file: File containing adjacency list. One node pair per line.
        :return:
        """
        cluster = Cluster(node_file, links_file, graph_topo_file)
        return  cls(cluster)

    def add_pipeline(self):
        pass

    def save_scheduling_decision(self):

        pass

    def update_network_profiling(self, links):
        #update the cluster info
        pass

    def update_pipeline_profiling(self, pipeline):
        #update piepline profile.

        pass

