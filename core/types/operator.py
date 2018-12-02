class Operator:
    def __init__(self, l='', fn_file='', t=0, s=0):
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
    def __init__(self, client_guid, client_ip, operator):
        """

        :param client_guid:
        :type client_guid: guid str
        :param operator:
        :type operator: type core.types.operator
        """
        self.client_guid = client_guid
        self.client_ip = client_ip
        self.operator = operator