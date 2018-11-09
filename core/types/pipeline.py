class Pipeline(object):
    def __init__(self, operators, start_node, end_node):
        '''

        :param operators:
        :type operators: list of core.operator
        :param start_node:
        :type start_node: guid str
        :param end_node:
        :type end_node: guid str
        '''
        self.operators = operators
        self.operator_instances = []    #populated by master (type: OperatorInstance)
        self.start_node = start_node
        self.end_node = end_node