import os
import logging
import time
import sys
from queue import Queue
import json
import dill
from nomad.core.config import CONSTANTS, ClientConfig
from nomad.core.master.kubernetes_api import KubernetesAPI
from nomad.core.placement.minlatsolver import RecMinLatencySolver
from nomad.core.universe.universe import Universe

from nomad.core.utils.LoggerWriter import LoggerWriter
from nomad.core.utils.RPCServerThreads import RPCServerThread
import nomad.core.config.MasterConfig as MasterConfig

# ====== BEGIN SETUP LOGGING =========
from nomad.core.utils.helpers import construct_xmlrpc_addr

#logging.basicConfig(level=logging.DEBUG)
#logger = logging.getLogger()

#logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-4s] %(message)s")

# Setup logging to file
#os.makedirs(MasterConfig.DEFAULT_LOG_DIR, mode=0o755, exist_ok=True)
#fileHandler = logging.FileHandler("{0}/{1}".format(MasterConfig.DEFAULT_LOG_DIR, MasterConfig.MASTER_LOG_FILE_NAME))
#fileHandler.setFormatter(logFormatter)
#logger.addHandler(fileHandler)

# Setup logging to console for Docker
#consoleHandler = logging.StreamHandler()
#consoleHandler.setFormatter(logFormatter)
#logger.addHandler(consoleHandler)

# sys.stderr = LoggerWriter(logger.warning)


# ======= LOGGER SETUP DONE =========

class Master(object):
    def __init__(self, master_rpc_port=None):
        self.universe = Universe()
        self.KubernetesAPI = KubernetesAPI()

        # Setting up the universe
        self.universe_setup()

        #if master_rpc_port is None:
        #    self.master_rpc_port = MasterConfig.RPC_DEFAULT_PORT
        #else:
        #    if isinstance(master_rpc_port, int) and (master_rpc_port < CONSTANTS.MAX_PORT_NUM) and (
        #            master_rpc_port > CONSTANTS.MIN_PORT_NUM):
        #        self.master_rpc_port = MasterConfig.RPC_DEFAULT_PORT
        #    else:
        #        raise TypeError(
        #            "RPC Port must be int between %d and %d" % (CONSTANTS.MIN_PORT_NUM, CONSTANTS.MAX_PORT_NUM))

        # Init RPC Server
        #methods_to_register = [self.register_client_onalive, self.get_next_op_address]
        #self.rpcserver = RPCServerThread(methods_to_register, self.master_rpc_port, multithreaded=False)
        #self.rpcserver.start()  # Run RPC server in separate thread


        self.scheduler = RecMinLatencySolver(self.universe.get_graph())

    def universe_setup(self):
        '''
        Static profiles the cluster and updates the universe with the cluster and the profiling values.
        '''
        #node_list = self.KubernetesAPI.get_nodes()  # List of str
        node_list_from_kubernetes =  ['phone', 'cloud', 'pc', 'base_station'] # List of str
        self.universe.create_cluster(node_list_from_kubernetes)
        node_profiling_info, link_profiling_info = self.profile_cluster(self.universe.cluster) # Dict of {'node_id': {'C': int}}
        self.universe.update_network_profiling(link_profiling_info)
        self.universe.update_node_profiling(node_profiling_info)

    def profile_cluster(self, cluster):
        #TODO: read from file
        node_profiling_file  = open('nomad/core/master/nodes.json')
        link_profiling_file  = open('nomad/core/master/links.json')
        node_profiling_info = json.load(node_profiling_file)    # Dict of {'node_id': {'C': int}}
        link_profiling_info = json.load(link_profiling_file)     # List of link objects [Link()..]
        # Replace with reading from file.
        node_profiling_file.close()
        link_profiling_file.close()
        return node_profiling_info, link_profiling_info

    def register_client_onalive(self, guid):
        logging.info("Client %s registered." % guid)

    def get_next_op_address(self, op_inst_guid):
        logging.info("Operator instance %s requested next op address." % op_inst_guid)
        op_inst = self.universe.get_operator_instance(op_inst_guid)
        next_op_guid = self.universe.get_operator(op_inst.operator_guid)._next
        if next_op_guid is None:
            next_op_addr = None
        else:
            next_op = self.universe.get_operator(next_op_guid)
            next_op_inst_ip = next_op._op_instances[0].client_ip    # _op_instances has already been instantiated while scheduling, but the IP may not exist depending if it has been instantiated yet.

            retry_count = 0
            while not next_op_inst_ip:
                if retry_count > MasterConfig.GET_NEXT_OP_RETRIES:
                    message = "Unable to get the next operator ip for %s. Is the next container ready?" % op_inst_guid
                    logging.error(message)
                    raise Exception(message)
                time.sleep(0.5)   # Wait before retrying - the container might be spinning up
                next_op_inst_ip = next_op._op_instances[0].client_ip
                retry_count += 1

            next_op_addr = construct_xmlrpc_addr(next_op_inst_ip, ClientConfig.RPC_DEFAULT_PORT)
        logging.info("Returning next operator %s" % next_op_addr)
        return next_op_addr

    def submit_network_profiling(self, network_profiling_info):
        self.universe.update_network_profiling(network_profiling_info)

    def submit_pipeline_profiling(self, pid, pipeline_profiling_info):
        self.universe.update_pipeline_profiling(pid, pipeline_profiling_info)

    def submit_pipeline(self, fns, start, end, id=''):
        pipeline_id = self.universe.add_pipeline(fns, start, end, id)
        pipeline_profiling_info = self.profile_pipeline(self.universe.get_pipeline(pipeline_id))
        self.submit_pipeline_profiling(pipeline_id, pipeline_profiling_info)
        self.schedule(pipeline_id)
        status = self.instantiate_pipeline(pipeline_id)
        return pipeline_id if status != -1 else -1

    def schedule(self, pipeline_guid):
        pipeline = self.universe.get_pipeline(pipeline_guid)
        start, end = pipeline.start_node, pipeline.end_node
        oid_list = [oid for oid in pipeline.operators]
        operators = [self.universe.get_operator(oid) for oid in oid_list]
        #run scheduler
        latency, placement, distribution = self.scheduler.find_optimal_placement(start, end, operators)

        # Create OperatorInstances
        for i in range(0, len(oid_list)):
            op_inst = self.universe.create_and_append_operator_instance(pipeline_guid, oid_list[i], node_id=placement[i])

#        logger.info("The placement decision is %s" % str(placement))

    def profile_pipeline(self, pipeline):
        #create_pipeline_profiling_containers()
        #wait_for_pipeline_profiling_completion()
        #TODO: read from file
        # fill in cloud_exec_time and msg_size
        profiling_info_file = open('nomad/core/master/pipeline.json')
        profiling_info = json.load(profiling_info_file)
        profiling_info_file.close()
        return  profiling_info

    def instantiate_pipeline(self, pipeline_id):
        pipeline = self.universe.get_pipeline(pipeline_id)
        operator_instance_guids = [self.universe.get_operator(op_guid)._op_instances[0] for op_guid in pipeline.operators]
        operator_instances = [self.universe.get_operator_instance(guid) for guid in operator_instance_guids]

        #Instantiate in reverse order
        for operator_instance in operator_instances.reverse():
            k8s_service, k8s_job = self.KubernetesAPI.create_kube_service_and_job(operator_instance)
            operator_instance.update_ip(k8s_service.spec.cluster_ip)    # update the ip from kubernetes

if __name__ == '__main__':
    master = Master()
