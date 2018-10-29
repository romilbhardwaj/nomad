# Gets the node allocation for given operator
import logging
from .BaseAllocator import BaseAllocator

logger = logging.getLogger(__name__)

class ShortestPathAllocator(BaseAllocator):
    @staticmethod
    def get_allocation(op_guid):
        raise NotImplementedError