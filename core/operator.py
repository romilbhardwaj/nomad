
class Operator:
    def __init__(self, l, t, s):
        self._label = l #Name of operator
        self._cloud_execution_time = t #Time to execute the operator in a cloud environment on a typical workload. Measured in seconds
        self._output_msg_size = s # Size of operator output in Kilobytes assuming a typical input.
        self._next = None #Next operator in pipeline.
    
    def cloud_execution_time(self):
        return self._cloud_execution_time