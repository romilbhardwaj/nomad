#Responsible for allocating nodes for a given operator. This is where Dijkstra's will be called.
from abc import ABC, abstractmethod

class BaseAllocator(ABC):
    @abstractmethod
    @staticmethod
    def get_allocation(op_guid):
        node_id = 0
        return node_id