class Operator:
    def __init__(self, guid, l='', fn_file='', t=0, s=0):
        self.guid = guid
        self._label = l #Name of operator
        self._fn_file = fn_file
        self._cloud_execution_time = t #Time to execute the operator in a cloud environment on a typical workload. Measured in milliseconds
        self._output_msg_size = s # Size of operator output in Kilobytes assuming a typical input.
        self._next = None #Next operator in pipeline.

    def cloud_execution_time(self):
        return self._cloud_execution_time
    
    def msg_size_bits(self):
        return self._output_msg_size * pow(10, 3) * 8

    def set_cloud_execution_time(self, t):
        self._cloud_execution_time = t

    def set_output_msg_size(self, s):
        self._output_msg_size = s

class OperatorInstance(object):
    def __init__(self, guid, node_id="", operator_id=None, client_guid=None, client_ip=None):
        """

        :param operator:
        :type operator: type core.types.operator
        :param client_guid:
        :type client_guid: guid str
        """
        self.guid = guid
        self.node_id = node_id  # Node Id where it is has been placed by the scheduler
        self.client_guid = client_guid
        self.client_ip = client_ip
        self.operator_id = operator_id

    def update_on_instantiation(self, client_guid, client_ip):
        self.client_guid = client_guid
        self.client_ip = client_ip