import cloudpickle
import xmlrpc.client

def submit_pipeline(ops, start, end, pipeline_id, master_conn_str, profile=None):
    '''
    Submits a pipeline to the Nomad master and instantiates the pipeline in the nomad cluster.
    :param ops: List of functions which compose the pipeline. The ordering of this list defines the ordering of the operators.
    :type ops: list of functions
    :param start: specifies the start node in the cluster where the first operator is placed.
    :type start: str - Name of the node as in Kubernetes
    :param end: Specifies the end node in the cluster where the last operator will be placed
    :type end: str - Name of the node as in Kubernetes
    :param pipeline_id: Name of the pipeline - used for internal bookkeeping
    :type pipeline_id: str
    :param master_conn_str: Connection string for the nomad master. For eg. "http://127.0.0.1:30000"
    :type master_conn_str: str
    :param profile: Profiling information for the pipeline being submitted.
    It is a list of length == ops, where each element of the list is a dictionary containing the following fields:
    {"cloud_execution_time": <double, time in seconds taken to execute the operator on a benchmark machine>, "output_msg_size": <double, the size of the result of the operator in bytes>}
    The ordering of this list should be the same as that of ops
    :type profile: list of dicts
    :return: List of operator GUIDs spawned by the pipeline.
    :rtype:
    '''
    server = xmlrpc.client.ServerProxy(master_conn_str, allow_none=True)
    data_to_send = []

    print("Launching pipeline. This might take some time..")

    if not profile:
        profiling_dict = {}
        for count, op_info in enumerate(profile):
            op_id = pipeline_id + "-%d" % count # For instance, demo-0
            profiling_dict[op_id] = {
                "label": op_id,
                "order": count,
                "cloud_execution_time": op_info["cloud_execution_time"],
                "output_msg_size": op_info["output_msg_size"],
            }
    else:
        profiling_dict = None

    #pickle operators
    for op in ops:
        p = cloudpickle.dumps(op)
        data_to_send.append(p)

    if profiling_dict:
        op_guids = server.receive_pipeline(data_to_send, start, end, pipeline_id)
    else:
        op_guids = server.receive_pipeline(data_to_send, start, end, pipeline_id, profiling_dict)
    op_guids.reverse()
    return op_guids


def get_last_output(op_id, master_conn_str):
    '''
    Gets the last output computed for the given operator.
    :param op_id: Id of the operator to get the result for
    :type op_id:
    :param master_conn_str: Connection string to nomad master
    :type master_conn_str:
    :return:
    :rtype:
    '''
    server = xmlrpc.client.ServerProxy(master_conn_str, allow_none=True)
    return server.get_last_output(op_id)


def get_nodes(master_conn_str):
    '''
    Gets the list of nodes in the nomad cluster.
    :param master_conn_str: Connection string to nomad master
    :type master_conn_str:
    :return:
    :rtype:
    '''
    server = xmlrpc.client.ServerProxy(master_conn_str, allow_none=True)
    return server.get_nodes()