class Link:
    def __init__(self, b, l):
        self._bandwidth = b # bytes/second(Mb/s)
        self._latency = l   # seconds(ms)
    
    def transfer_time(self, bytes):
        """Calculates the transfer time in milliseconds for a given number of bytes (ms)"""
    
        return bytes / self._bandwidth + self._latency
