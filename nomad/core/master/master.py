import os
import logging
import threading
import xmlrpc
import time
import sys
from queue import Queue

import dill
from nomad.core.config import CONSTANTS
from nomad.core.placement.minlatsolver import RecMinLatencySolver
from nomad.core.types.operator import OperatorInstance
from nomad.core.universe.universe import Universe

from nomad.core.utils.LoggerWriter import LoggerWriter
from nomad.core.utils.RPCServerThreads import RPCServerThread
import nomad.core.config.MasterConfig as MasterConfig

# ====== BEGIN SETUP LOGGING =========

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-4s] %(message)s")

# Setup logging to file
os.makedirs(MasterConfig.DEFAULT_LOG_DIR, exist_ok=True)
fileHandler = logging.FileHandler("{0}/{1}".format(MasterConfig.DEFAULT_LOG_DIR, MasterConfig.MASTER_LOG_FILE_NAME))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# Setup logging to console for Docker
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

# sys.stderr = LoggerWriter(logger.warning)


# ======= LOGGER SETUP DONE =========

class Master(object):
    def __init__(self, master_rpc_port=None):
        self.universe = Universe()

        # Setting up the universe
        self.universe_setup()

        if master_rpc_port is None:
            self.master_rpc_port = MasterConfig.RPC_DEFAULT_PORT
        else:
            if isinstance(master_rpc_port, int) and (master_rpc_port < CONSTANTS.MAX_PORT_NUM) and (
                    master_rpc_port > CONSTANTS.MIN_PORT_NUM):
                self.master_rpc_port = MasterConfig.RPC_DEFAULT_PORT
            else:
                raise TypeError(
                    "RPC Port must be int between %d and %d" % (CONSTANTS.MIN_PORT_NUM, CONSTANTS.MAX_PORT_NUM))

        # Init RPC Server
        methods_to_register = [self.register_client_onalive, self.get_next_op_address]
        self.rpcserver = RPCServerThread(methods_to_register, self.master_rpc_port, multithreaded=False)
        self.rpcserver.start()  # Run RPC server in separate thread

        self.scheduler = RecMinLatencySolver(self.universe.get_graph())

    def universe_setup(self):
        '''
        Static profiles the cluster and updates the universe with the cluster and the profiling values.
        '''
        node_list_from_kubernetes = kubernetesAPI.get_nodes()  # List of str
        self.universe.create_cluster(node_list_from_kubernetes)
        node_profiling_info, link_profiling_info = self.profile_cluster(self.universe.cluster) # Dict of {'node_id': {'C': int}}
        self.universe.update_network_profiling(link_profiling_info)
        self.universe.update_node_profiling(node_profiling_info)

    def profile_cluster(self, cluster):
        node_profiling_info = {}    # Dict of {'node_id': {'C': int}}
        link_profiling_info = {}    # List of link objects [Link()..]
        # Replace with reading from file.
        return node_profiling_info, link_profiling_info

    def register_client_onalive(self, guid):
        logging.info("Client %s registered." % guid)

    def get_next_op_address(self, guid):
        next_op_addr = "http://127.0.0.1:10000"
        logging.info("Client %s requested next op address, returning %s" % (guid, next_op_addr))
        return next_op_addr

    def submit_network_profiling(self, network_profiling_info):
        self.universe.update_network_profiling(network_profiling_info)

    def submit_pipeline_profiling(self, pid, pipelinne_profiling_info):
        self.universe.update_pipeline_profiling(pid, pipeline_profiling_info)

    def submit_pipeline(self, fns, start, end):
        pipeline_id = self.universe.add_pipeline(fns, start, end)
        pipeline_profiling_info = self.profile_pipeline(self.universe.get_pipeline(pipeline_id))
        self.submit_pipeline_profiling(pipeline_id, pipeline_profiling_info)
        self.schedule(pipeline_id)
        status = self.instantiate_pipeline(pipeline_id)
        return pipeline_id if status != -1 else -1

    def schedule(self, pipeline_id):
        pipeline = self.universe.get_pipeline(pipeline_id)
        start, end = pipeline.start_node, pipeline.end_node
        oid_list = [oid for oid in pipeline.operators]
        operators = [self.universe.get_operator(oid) for oid in oid_list]
        #run scheduler
        latency, placement, distribution = self.scheduler.find_optimal_placement(start, end, operators)

        # Create OperatorInstances
        op_inst_guids = []
        for i in range(0, len(oid_list)):
            guid = self.generate_guid()
            op_inst_guids.append(guid)
            operator_instance = OperatorInstance(guid=self.universe.generate_guid(), node_id=placement[i], operator_id=oid_list[i])
            self.universe.add_operator_instance(operator_instance)

        #update the pipeline with the operator instance
        pipeline.set_operator_instances(op_inst_guids)
        logger.info("The placement decision is %s" % str(placement))

    def profile_pipeline(self, pipeline):
        #create_pipeline_profiling_containers()
        #wait_for_pipeline_profiling_completion()

        # fill in cloud_exec_time and msg_size
        pipeline_profiling_info = []
        for op_id in pipeline.operators:
            profiling_info = {}
            profiling_info['id'] = op_id
            profiling_info['ref_exec_time'] = 10
            profiling_info['output_msg_size'] = 20
            pipeline_profiling_info.append(profiling_info)

        return pipeline_profiling_info

    # def profile_cluster():
    #     create_profiling_containers()
    #     wait_for_profiling_completion()
    # def submit_network_profiling(self, network_profiling_info):
    #     self.universe.update_network_profiling(network_profiling_info)
    #
    # def submit_pipeline_profiling(self, pipeline_profiling_info):
    #     self.universe.update_pipeline_profiling(pipeline_profiling_info)
    #
    # def create_profiling_containers(self):
    #     pass
    #
    # def wait_for_profiling_completion(self):
    #     pass
    #

    #
    # def profile_pipeline(self, pipeline):
    #     create_pipeline_profiling_containers()
    #     wait_for_pipeline_profiling_completion()
    #     pass


if __name__ == '__main__':
    master = Master()
