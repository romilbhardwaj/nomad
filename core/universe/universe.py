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

