class Link:
    def __init__(self, b, l):
        self._bandwidth = b #Mega bits/second(Mb/s)
        self._latency = l   #milli seconds(ms)
    
    def transfer_time(self, bits):
        """
        Calculates the transfer time in seconds for a given number of bits
        """
        return bits / (self._bandwidth * pow(10,6)) + self._latency * pow(10, -3) 
    
