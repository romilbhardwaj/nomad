class Message(object):
    def __init__(self, args, kwargs=None):
        '''
        The Nomad Message type which is passed around clients.
        :param args: list of args for the next operator
        :type args: list
        :param kwargs: dict of kwargs for the next operator
        :type kwargs: dict
        '''
        if not isinstance(args, list):
            args = [args]
        self.args = args
        if kwargs is None:
            self.kwargs = {}
        else:
            self.kwargs = kwargs

    def get_args(self):
        return self.args

    def __str__(self):
        return str(self.args)