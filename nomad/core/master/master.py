import os
from os.path import expanduser
import platform
import logging
import threading
from multiprocessing import Process
import time
import sys
import json
import docker
from collections import defaultdict
import shutil
from nomad.core.config import CONSTANTS, ClientConfig, DockerConfig
from nomad.core.master.kubernetes_api import KubernetesAPI
from nomad.core.placement.minlatsolver import RecMinLatencySolver
from nomad.core.scheduler.KubernetesScheduler import KubernetesScheduler
from nomad.core.universe.universe import Universe
from nomad.core.graph.node import Architectures
from nomad.core.utils.LoggerWriter import LoggerWriter
from nomad.core.utils.RPCServerThreads import RPCServerThread
import nomad.core.config.MasterConfig as MasterConfig
from nomad.core.utils.helpers import construct_xmlrpc_addr

# ====== BEGIN SETUP LOGGING =========

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-4s] %(message)s")

# Setup logging to file
if platform.system() == 'Darwin':
    #OS X
    os.makedirs(expanduser("~") + '/nomad/logs', mode=0o755, exist_ok=True)
    fileHandler = logging.FileHandler("{0}/{1}".format(expanduser("~") + '/nomad/logs', MasterConfig.MASTER_LOG_FILE_NAME))
else:
    os.makedirs(MasterConfig.DEFAULT_LOG_DIR, mode=0o755, exist_ok=True)
    fileHandler = logging.FileHandler("{0}/{1}".format(MasterConfig.DEFAULT_LOG_DIR, MasterConfig.MASTER_LOG_FILE_NAME))

fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# Setup logging to console for Docker
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

sys.stderr = LoggerWriter(logger.warning)


# ======= LOGGER SETUP DONE =========

class SchedulerThread(threading.Thread):
    def __init__(self, scheduler):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stoprequest = threading.Event()
        self.scheduler = scheduler

    def run(self):
        self.scheduler.run()

class Master(object):
    def __init__(self, master_rpc_port=None):
        self.universe = Universe()
        self.KubernetesAPI = KubernetesAPI()

        # Setting up the universe
        self.node_list = []
        self.universe_setup()

        if master_rpc_port is None:
            logger.warning("No master_rpc_port specified, using default %d" % MasterConfig.RPC_DEFAULT_PORT)
            self.master_rpc_port = MasterConfig.RPC_DEFAULT_PORT
        else:
            if isinstance(master_rpc_port, int) and (master_rpc_port < CONSTANTS.MAX_PORT_NUM) and (
                    master_rpc_port > CONSTANTS.MIN_PORT_NUM):
                self.master_rpc_port = master_rpc_port
            else:
                raise TypeError(
                    "RPC Port must be int between %d and %d" % (CONSTANTS.MIN_PORT_NUM, CONSTANTS.MAX_PORT_NUM))

        if MasterConfig.MASTER_K8S_SERVICE_ENVVAR in os.environ:
            self.ip_address = str(os.environ[MasterConfig.MASTER_K8S_SERVICE_ENVVAR])
            logger.info("Envvar introspection: Read env var %s, using ip %s" % (
                MasterConfig.MASTER_K8S_SERVICE_ENVVAR, self.ip_address))
        else:
            logger.warning(
                "Envvar %s not detected. IP Address is none. clients spawned from this master won't be able to make RPC calls." % MasterConfig.MASTER_K8S_SERVICE_ENVVAR)
            self.ip_address = None

        # Init RPC Server
        logger.info("Instantiating RPC server on port %d" % self.master_rpc_port)
        methods_to_register = [self.receive_pipeline, self.register_client_onalive, self.get_next_op_address, self.update_pipeline_profiling,
                               self.update_node_profiling, self.update_network_profiling, self.get_node_profiling, self.get_network_profiling,
                               self.get_pipeline_profiling, self.get_nodes, self.get_last_output]
        #TODO: Use multithreded
        self.rpcserver = RPCServerThread(methods_to_register, self.master_rpc_port, multithreaded=True)
        self.rpcserver.start()  # Run RPC server in separate thread

        logger.info("Creating the scheduler object.")
        self.scheduler = RecMinLatencySolver(self.universe.get_graph())

        self._init_k8s_scheduler()

        logger.info("Master instantiation complete.")

    def _init_k8s_scheduler(self):
        sched = KubernetesScheduler(universe=self.universe)
        self.k8s_schedthread = SchedulerThread(sched)
        self.k8s_schedthread.start()

    def universe_setup(self):
        '''
        Static profiles the cluster and updates the universe with the cluster and the profiling values.
        '''
        logger.info("Setting up universe.")
        self.node_list = self.KubernetesAPI.get_nodes()  # List of str
       # node_list_test =  ['phone', 'cloud', 'pc', 'base_station'] # List of str
        logger.info("Creating cluster object in universe.")
        self.universe.create_cluster(self.node_list)
        logger.info("Cluster created, adding profiling info now.")
        node_profiling_info, link_profiling_info = self.profile_cluster(self.universe.cluster) # Dict of {'node_id': {'C': int}}
        self.universe.update_network_profiling(link_profiling_info)
        self.universe.update_node_profiling(node_profiling_info)
        logger.info("Profiling complete.")
        logger.info("Universe setup complete.")

    def profile_cluster(self, cluster):
        #TODO: read from file
        is_aws = False
        is_e2e = False
        if is_aws:
            node_profiling_file = open('/nomad/nomad/tests/core/master/nodes_aws.json')
            link_profiling_file = open('/nomad/nomad/tests/core/master/links_aws.json')
        if is_e2e:
            node_profiling_file = open('/nomad/nomad/tests/core/master/nodes_e2e_test.json')
            link_profiling_file = open('/nomad/nomad/tests/core/master/links_e2e_test.json')
        else:
            node_profiling_file = open('/nomad/nomad/tests/core/master/nodes_test.json')
            link_profiling_file = open('/nomad/nomad/tests/core/master/links_test.json')
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
            next_op_inst_ip = self.universe.get_operator_instance(next_op._op_instances[0]).client_ip    # _op_instances has already been instantiated while scheduling, but the IP may not exist depending if it has been instantiated yet.

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
        #TODO: check format of pipeline_profiling_info. If we have multiple operator instances we need to syncronize threads
        self.universe.update_pipeline_profiling(pid, pipeline_profiling_info)

    def submit_node_profiling(self, node_profile):
        self.universe.update_node_profiling(node_profile)

    def submit_pipeline(self, images, start, end, pipeline_id, profile=None):
        #fns: list of image ids
        #TODO: add optional arg profiling
        logger.info("Submit_pipeline is called with params fns=%s, start=%s, end=%s, pipeline_id=%s." % (str(images), str(start), str(end), str(pipeline_id)))
        pipeline_id = self.universe.add_pipeline(images, start, end, pipeline_id)
        logger.info("Pipeline %s added to universe, now profiling." % str(pipeline_id))
        if profile:
            self.submit_pipeline_profiling(pipeline_id, profile)
        else:
            self.profile_pipeline(pipeline_id)
        logger.info("Pipeline %s profiling complete - scheduling now." % str(pipeline_id))
        logger.info("Pipeline %s profiling complete - scheduling now." % str(pipeline_id))
        self.schedule(pipeline_id)
        logger.info("Pipeline %s schedule computed! Now instantiating.." % str(pipeline_id))
        operator_instances = self.instantiate_pipeline(pipeline_id)
        logger.info("Pipeline %s instantiated!" % str(pipeline_id))
        return operator_instances

    def schedule(self, pipeline_guid):
        logger.info("Trying to schedule pipeline %s" % str(pipeline_guid))
        pipeline = self.universe.get_pipeline(pipeline_guid)
        start, end = pipeline.start_node, pipeline.end_node
        oid_list = [oid for oid in pipeline.operators]
        operators = [self.universe.get_operator(oid) for oid in oid_list]
        #run scheduler
        logger.info("Finding optimal placement for pipeline %s" % str(pipeline_guid))
        latency, placement, distribution = self.scheduler.find_optimal_placement(start, end, operators)
        logger.info("Scheduling result - latency %s, placement %s, distribution %s." % (str(latency), str(placement), str(distribution)))
        #TODO: write schedule to pipeline object.
        pipeline.schedule = {'latency': latency, 'placement': placement, 'distribution': distribution}

    def profile_pipeline(self, pid, from_file=False):
        if not from_file:
            self.create_pipeline_profiling_containers(pid)
            self.wait_for_pipeline_profiling_completion(pid)
            logger.info('* Pipeline profiling completed! *')
            #shutdown_pipeline(pid)
            #Todo write pipeline profile to long term storage.
            #return get_pipeline_pipeline_profiling
        else:
        #read from file
            profiling_info_file = open('/nomad/nomad/tests/core/master/pipeline_test.json')
            profiling_info = json.load(profiling_info_file)
            profiling_info_file.close()
            self.submit_pipeline_profiling(pid, profiling_info)

    def create_pipeline_profiling_containers(self, pid):
        """
        Instantiates pipeline for profiling.
        Schedule: [start, profiling_node, ... , profiling_node, end]
        :param pipeline:
        :return:
        """
        pipeline = self.universe.get_pipeline(pid)
        N = len(pipeline.operators)
        placement = [pipeline.start_node] + [MasterConfig.DEFAUL_PROFILING_NODE] * (N - 2)  + [pipeline.end_node]
        logger.info("Now launching profiling containers with the following schedule %s" % str(placement))
        distribution = {pipeline.start_node: 1,
                        pipeline.end_node: 1,
                        MasterConfig.DEFAUL_PROFILING_NODE: N-2}

        pipeline.schedule = {'latency': 0, 'placement': placement, 'distribution': distribution}
        self.instantiate_pipeline(pid)
        #Todo: the master must wait for the pipeline to start running

    def wait_for_pipeline_profiling_completion(self, pid):
        max_time_seconds = 300
        start = time.time()
        logger.info("Waiting for profiling completion (PID: %s)..." % pid)

        """
        Alternative way of implementing this would be add a state attr to the pipeline obj
        to signal completion of the profiling run and to determine what legal next states to perform.
        
        e.g: pipeline states: not_read_for_deployment, profiling, ready_for_deployment, deployed  
        """
        #TODO: use condition to wait for pipeline to be ready for deployment.
        while(not self.pipeline_ready_for_deployment(pid)):
            time.sleep(2)
            logger.info("Waiting for profiling completion (PID: %s)..." % pid)

    def pipeline_ready_for_deployment(self, pid):
        """
        :param pid:
        :return: bool. Returns true if pipeline is ready for deployment false otherwise
        """
        measurements = {"cloud_execution_time", "output_msg_size"}
        pipeline = self.universe.get_pipeline(pid)
        operator_guids = self.universe.get_pipeline(pid).operators
        profiling = self.get_pipeline_profiling(pid)
        logger.info("Current pipeline profiling for pipeline %s: %s" % (pid, str(profiling)))

        #Check that all the operators have the desired measurements and that the pipeline has a valid schedule
        #Check that values are not zero
        return (all(measurements.issubset(profiling[opid].keys()) for opid in operator_guids)
                and pipeline.schedule != None
                and all(profiling[opid][m] for m in measurements for opid in operator_guids))

    def shutdown_pipeline(self, pid):
        #get opinstances.
        #remove kube service and job
        #remove opinstances
        pass

    def update_pipeline_profiling(self, pid, new_profile):
        self.submit_pipeline_profiling(pid, new_profile)

    def update_node_profiling(self, new_node_profile):
        self.submit_node_profiling(new_node_profile)

    def update_network_profiling(self, new_network_profile):
        self.submit_network_profiling(new_network_profile)

    def get_network_profiling(self):
        return self.universe.get_network_profiling()

    def get_node_profiling(self):
        return self.universe.get_node_profiling()

    def get_pipeline_profiling(self, pid):
        return self.universe.get_pipeline_profiling(pid)

    def instantiate_pipeline(self, pipeline_id):
        pipeline = self.universe.get_pipeline(pipeline_id)
        #Here we are assuming that the opids are stored in order
        #Is that a too strong assumption?
        oid_list = [oid for oid in pipeline.operators]

        #Check if pipeline has schedule attr.
        if pipeline.schedule == None:
            logger.exception("Pipeline %d has no valid schedule" % pipeline_id)
            raise Exception("No schedule found for pipeline %d" % pipeline_id)

        #Create operator instances.
        logger.info("Now trying to create the operator instances.")
        for i in range(len(oid_list)):
            op_inst = self.universe.create_and_append_operator_instance(pipeline_id, oid_list[i],
                                                                        node_id=pipeline.schedule['placement'][i])
            logger.info("Setting env for operator_instance %s" % op_inst.guid)
            op_inst.set_envs(construct_xmlrpc_addr(self.ip_address, self.master_rpc_port))

        operator_instance_guids = [self.universe.get_operator(op_guid)._op_instances[0] for op_guid in pipeline.operators]
        operator_instances = [self.universe.get_operator_instance(guid) for guid in operator_instance_guids]

        # Check if pipeline is already instantiated.
        if any([opinst.state == 'running' for opinst in operator_instances]):
            logger.exception("Operator instances already running")
            raise Exception("Pipeline already instantiated")

        #Instantiate in reverse order
        operator_instances.reverse()
        for operator_instance in operator_instances:
            node = self.universe.get_node(operator_instance.node_id)
            #TODO: select image based on node arch
            architecture = node._architecture
            #Select the correct image
            image = self.universe.get_operator(operator_instance.operator_guid).get_image(architecture)
            k8s_service, k8s_job = self.KubernetesAPI.create_kube_service_and_job(operator_instance, image=image)
            #Update operator instance
            operator_instance.update_ip(k8s_service.spec.cluster_ip)    # update the ip from kubernetes
            operator_instance.update_image(image)
            operator_instance.update_state('running')
            operator_instance.update_k8s_service(k8s_service)
            operator_instance.update_k8s_job(k8s_job)

        return operator_instances


    def receive_pipeline(self, ops, start, end, pid, profile=None):
        def write_to_file(binary_obj, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(binary_obj.data)

        def build_op_image(opid, pid, arch, pickle):
            build_src_path = '/tmp/%s/op_%d/' % (arch, opid)
            if not os.path.exists(build_src_path):
                os.makedirs(build_src_path)
            shutil.copy('/nomad/images/client/Dockerfile.operator.%s' % arch, build_src_path + 'Dockerfile')
            file_name = build_src_path + 'operator.pickle'

            # Save pickle
            write_to_file(pickle, file_name)

            pickle_rel_path = os.path.relpath(file_name, build_src_path)
            tag = Architectures.get_operator_img_tag(MasterConfig.DEFAULT_DOCKER_HUB_REPO, pid, opid, arch)
            #TODO: figure out how to specify arch in build process. currently arch is assigned based on ther arch of
            # the host running the docker daemon. Solution: Set platform-arg.
            docker_image, build_log = client.images.build(tag=tag, path=build_src_path,
                                                          buildargs={'PYTHON_PICKLE_PATH': pickle_rel_path}, rm=True, pull=True)
            logger.debug("Build result: \n%s" % str(docker_image))
            for line in build_log:
                logger.debug(line)
            # push image to docker hub
            push_result = client.images.push(repository=tag, auth_config={'username': DockerConfig.USERNAME,
                                                                          'password': DockerConfig.PASSWORD})
        #create client
        client = docker.from_env()
        images = defaultdict(dict)
        processes = []
        start_time = time.time()
        for i, op_pickle in enumerate(ops):
            # TODO: Should we use a process pool instead of spawning a new process for each image?
            for arch in Architectures.SUPPORTED:
                tag = Architectures.get_operator_img_tag(MasterConfig.DEFAULT_DOCKER_HUB_REPO, pid, i, arch)
                #Note: we are storing the image tag before we know that the build succeeded.
                #If the image build fails, k8s will fail to launch the corresponding container.
                images[i][arch] = tag
                p = Process(target=build_op_image, args=(i, pid, arch, op_pickle))
                processes.append(p)

        for p in processes:
            p.start()

        for p in processes:
            p.join()

        logger.info("---Building %d images took %s seconds. ---" % (len(images) * len(Architectures.SUPPORTED),
                                                                    time.time() - start_time))

        op_instances = self.submit_pipeline(images, start, end, pid, profile)
        #TODO: we should return the pipeline id here.
        return [op.guid for op in op_instances]

    def get_last_output(self, op_id):
        return self.universe.get_operator_instance(op_id).get_last_output()

    def get_nodes(self):
        return self.node_list

if __name__ == '__main__':
    master = Master()
