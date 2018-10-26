
class Node:
    def __init__(self, label, C):
        self._label = label
        self._C = C
        self._num_operators = 0
    
    def processing_time(self, operator):
        return operator.cloud_execution_time() / self._C
