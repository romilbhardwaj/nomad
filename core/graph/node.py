
class Node:
    def __init__(self, label, C):
        self._label = label
        self._C = C
        self._C_scaled = C
        self._num_operators = 0
    
    def processing_time(self, operator, ops_count):
        return (operator.cloud_execution_time() * ops_count) / self._C

    def add_operator(self):
        #TODO remove this function
        self._num_operators += 1
        self._update_C_scaled()
    
    def _update_C_scaled(self):
        self._C_scaled  = self._C / self._num_operators

