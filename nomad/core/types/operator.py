class Operator:
    def __init__(self, guid, l='', fn_file='', t=0, s=0):
        self.guid = guid
        self._label = l #Name of operator
        self._fn_file = fn_file
        self._cloud_execution_time = t #Time to execute the operator in a cloud environment on a typical workload. Measured in milliseconds
        self._output_msg_size = s # Size of operator output in Kilobytes assuming a typical input.
        self._next = None # GUID of next op in pipeline
        self._op_instances = []

    def get_op_inst_guid(self):
        return self.guid + "-instance" + str(len(self._op_instances))

    def append_op_instance(self, op_inst_guid):
        self._op_instances.append(op_inst_guid)

    def cloud_execution_time(self):
        return self._cloud_execution_time
    
    def msg_size_bits(self):
        return self._output_msg_size * pow(10, 3) * 8

    def set_cloud_execution_time(self, t):
        self._cloud_execution_time = t

    def set_output_msg_size(self, s):
        self._output_msg_size = s

class OperatorInstance(object):
    def __init__(self, guid, pipeline_guid, operator_guid, node_id=None, client_ip=None, image=None):
        '''
        Defines an operator instance running on the network. Associated with an operator and a pipeline.
        :param guid: GUID, typically of the form <pipeline_guid>-<operator_guid>-<instance_guid>
        :type guid: str
        :param pipeline_guid: GUID of the parent pipeline
        :type pipeline_guid: str
        :param operator_guid: GUID of the operator
        :type operator_guid: str
        :param node_id: id of the node in kubernetes where it is launched
        :type node_id: str
        :param client_ip: IP of the client
        :type client_ip: str
        :param image: docker image the operator instance is running
        :type image: str
        '''
        self.guid = guid
        self.node_id = node_id  # Node Id where it is has been placed by the scheduler
        self.client_guid = guid     #TODO: Redundant, can this be removed?
        self.client_ip = client_ip
        self.image = image
        self.operator_guid = operator_guid
        self.pipeline_guid = pipeline_guid

    def update_ip(self, client_ip):
        self.client_ip = client_ip