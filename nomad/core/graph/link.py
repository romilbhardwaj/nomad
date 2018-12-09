class Link:
    def __init__(self, f, t, b, l):
        self._bandwidth = b # bytes/second(B/s)
        self._latency = l   # seconds(s)
        self._from = f
        self._to = t
    
    def transfer_time(self, bytes):
        """Calculates the transfer time in seconds for a given number of bytes (s)"""
    
        return bytes / self._bandwidth + self._latency
