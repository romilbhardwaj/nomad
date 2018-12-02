from core.types.cluster import Cluster
from core.types.operator import Operator
from core.types.pipeline import Pipeline

class Universe(object):
    def __init__(self, cluster):
        """

        :param cluster: The cluster info
        :type cluster: ClusterObj
        """
        self._next_pipeline_id = 0
        self.pipelines = {}
        self.operators  = {}
        self.operator_instances = {}
        self.cluster = cluster

    def get_next_operator(self, client_guid):
        for id, pipeline in self.pipelines.items():
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
        cluster = Cluster.read_cluster_spec(node_file, links_file, graph_topo_file)
        return  cls(cluster)


    def add_pipeline(self, fns, start, end):
        #create operators
        operators = []
        for fn in fns:
            op = Operator(fn_file=fn)
            op_id = id(op)
            operators.append(op_id)
            self.operators[op_id] = op

        #create pipeline object
        pipeline = Pipeline(operators, start, end)
        pid = id(pipeline)

        self.pipelines[pid] = pipeline

        return pid

    def get_pipeline(self, id):
        return self.pipelines[id]

    def get_operator(self, oid):
        return self.operators[oid]

    def get_graph(self):
        """Returns the network graph"""
        return  self.cluster.graph

    def save_scheduling_decision(self, pipeline_id, scheduling_result):
        #find pipeline
        #create operator instances,
        #update the ip adress field.
        pass

    def update_network_profiling(self, links_json):
        #update the cluster info
        self.cluster.update_links(links_json)

    def update_pipeline_profiling(self, pid, pipeline_profiling_info):
        #Lookup pipeline
        pipeline = self.pipelines[pid]

        for operator_profile in pipeline_profiling_info:
            oid = operator_profile['id']
            operator = self.operators[oid]
            operator.set_cloud_execution_time(operator_profile['ref_exec_time'])
            operator.set_output_msg_size(operator_profile['output_msg_size'])



