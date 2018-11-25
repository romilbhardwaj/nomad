class DirectedGraph:
    def __init__(self, v):
        self._v = v
        self._e = 0
        self._adj = [set()] * v
    
    @classmethod
    def from_file(self, path_to_file):
        pass