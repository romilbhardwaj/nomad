class Link:
    def __init__(self, b, l):
        self._bandwidth = b #Mega bits/second(Mb/s)
        self._latency = l   #milliseconds(ms)
    
    def transfer_time(self, bits):
        """Calculates the transfer time in milliseconds for a given number of bits (ms)"""
    
        return bits / (self._bandwidth * pow(10,3)) + self._latency  
    
