import uuid

from nomad.core.types.cluster import Cluster
from nomad.core.types.operator import Operator
from nomad.core.types.pipeline import Pipeline


class Universe(object):
    def __init__(self):
        """

        :param cluster: The cluster info
        :type cluster: ClusterObj
        """
        self._next_pipeline_id = 0
        self.pipelines = {}
        self.operators  = {}
        self.operator_instances = {}
        self.cluster = None

    def get_next_operator(self, client_guid):
        for id, pipeline in self.pipelines.items():
            for operator_instance in pipeline.operator_instances:
                if client_guid == operator_instance.client_guid:
                    operator_to_find = operator_instance.operator
                    next_operator_instance = pipeline.operator_instance[pipeline.operators.index(operator_to_find) + 1]  # Assuming ordering on operator_instance is the same as operators
                    return next_operator_instance
        raise Exception("No next operator.")

    @staticmethod
    def generate_guid():
        return str(uuid.uuid4())

    def add_pipeline(self, fns, start, end, id=''):
        #new pid
        pid = self.generate_guid() if id == '' else id

        #create operators
        operators = []
        for i, fn in enumerate(fns):
            if i == len(fns) - 1:
                next_op_id = None
            else:
                next_op_id = pid + "-" + str(i+1)

            op_id = pid + "-" + str(i)
            op = Operator(fn_file=fn, guid= op_id)
            op._next = next_op_id
            operators.append(op_id)
            self.operators[op_id] = op

        #create pipeline object
        pipeline = Pipeline(pid, operators, start, end)
        self.pipelines[pid] = pipeline

        return pid

    def add_operator_instance(self, op_instance):
        '''
        Adds an operator instance to the universe
        :param op_instance:
        :type op_instance: OperatorInstance object
        :return:
        :rtype:
        '''

        raise NotImplementedError()

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
        #TODO: remove pid input
        pipeline = self.pipelines[pid]
        for op_id, operator_profile in pipeline_profiling_info.items():
            operator = self.operators[op_id]
            for key, val in operator_profile.items():
                setattr(operator, '_'+key, val)

    def create_cluster(self, node_list_from_kuberenetes):
        self.cluster = Cluster.create_cluster(node_list_from_kuberenetes)

    def update_network_profiling(self, link_profiling_info):
        '''
        :param link_profiling_info:
        :type link_profiling_info: List of link objects [Link()..]
        '''
        self.cluster.update_links(link_profiling_info)

    def update_node_profiling(self, node_profiling_info):
        '''

        :param node_profiling_info:
        :type node_profiling_info: Dict of {'node_id': {'C': int}}
        '''
        self.cluster.update_nodes(node_profiling_info)