'''
This class defines the kubernetes API helper methods
'''
import logging
from kubernetes import client, config
from kubernetes.client import V1EnvVar, V1ContainerPort, V1Job, V1JobSpec, V1PodTemplateSpec, V1Service, V1ServicePort, \
    V1ServiceSpec, V1DeleteOptions, V1SecurityContext, V1Capabilities

from nomad.core.config import KubernetesConfig
from nomad.core.config.CONSTANTS import ClientDockerImages
from nomad.core.graph.node import Architectures
from nomad.core.utils.helpers import merge_dicts

# logging.basicConfig(level=logging.INFO)

# TODO: Better setup logging
logger = logging.getLogger(__name__)


class KubernetesAPI(object):
    def __init__(self):
        config.load_incluster_config()
        self.kubecoreapi = client.CoreV1Api()
        self.kubebatchapi = client.BatchV1Api()

    def get_nodes(self):
        '''
        Queries the kubernetes API to get a list of nodes containing strings of their names
        :return: List of names of nodes
        :rtype: list
        '''
        logger.info("Getting nodes from the kubernetes API")
        node_list = self.kubecoreapi.list_node().items
        node_names = [node.metadata.name for node in node_list]
        logger.info("Got nodes from kubernetes: %s" % str(node_names))
        return node_names


    def create_kube_service_and_job(self, op_inst, ports=[["nomadmaster", 31000, 31000], ["nomadclient", 30000, 30000],
                                                          ["ssh", 22, 22]], namespace=KubernetesConfig.K8S_NAMESPACE, architecture=Architectures.x86):
        k8s_service = self.launch_kube_service(op_inst, ports, namespace)

        # TODO: Use multiple arch images.
        '''
        if architecture == Architectures.x86:
            image = ClientDockerImages.x86
        elif architecture == Architectures.rpiarm:
            image = ClientDockerImages.rpiarm
        else:
            raise Exception("Unknown architecture %s" % str(architecture))
        '''
        k8s_job = self.launch_kube_job(op_inst, image, namespace=namespace)
        return k8s_service, k8s_job

    def delete_kube_service_and_job(self, guid, namespace='gandiva'):
        service_status = self.delete_kube_service(guid, namespace)
        job_status = self.delete_kube_job(guid, namespace)
        return service_status, job_status

    def launch_kube_service(self, op_inst, ports, namespace=KubernetesConfig.K8S_NAMESPACE):
        '''
        Creates a kubernetes service for the given OperatorInstance
        :param op_inst: OperatorInstance
        :param namespace:
        :return: Service object from the API
        '''
        service = self._create_kube_service(op_inst.guid, ports)
        kubeservice = self.kubecoreapi.create_namespaced_service(namespace=namespace, body=service)
        return kubeservice

    def delete_kube_service(self, k8s_id, namespace=KubernetesConfig.K8S_NAMESPACE):
        '''
        Deletes a kubernetes service for the given JobInfo
        :param kubeapi: V1CoreApi object
        :param k8s_id: k8s_id of the job
        :param namespace:
        :return: Status object from the API
        '''
        name = k8s_id + "-service"
        status = self.kubecoreapi.delete_namespaced_service(name, namespace)
        return status

    def delete_kube_job(self, k8s_id, namespace=KubernetesConfig.K8S_NAMESPACE):
        '''
        Deletes a kubernetes job for the given k8s_id (op_inst guid).
        :param k8s_id: k8s_id of the job
        :param namespace:
        :return: Status object from the API
        '''
        name = k8s_id + "-job"
        status = self.kubebatchapi.delete_namespaced_job(name, namespace,
                                                         V1DeleteOptions(propagation_policy="Background"))
        return status

    def launch_kube_job(self, op_inst, image, namespace=KubernetesConfig.K8S_NAMESPACE):
        '''
        Creates a Kube job from JobInfo and launches it on the cluster.
        :param op_inst: OperatorInstance
        :param namespace:
        :return: Job object form the API
        '''
        container = self._create_kube_container(op_inst, image=image)
        podspec = self._create_kube_podspec(container, scheduler_name=KubernetesConfig.DEFAULT_SCHEDULER,
                                            namespace=namespace)  # Specify scheduler...
        kube_job = self._create_kube_job(op_inst, podspec, namespace=namespace)

        result_job = self.kubebatchapi.create_namespaced_job(namespace, body=kube_job)
        return result_job

    def _create_kube_job(self, op_inst, podspec, namespace=KubernetesConfig.K8S_NAMESPACE):
        job_name = op_inst.guid + "-job"
        job_metadata = client.V1ObjectMeta(name=job_name, namespace=namespace, labels={
            KubernetesConfig.K8S_LABELS_OPGUID: op_inst.guid})  # Label for the service to bind to
        pod_name = op_inst.guid + "-pod"
        pod_metadata = client.V1ObjectMeta(name=pod_name, namespace=namespace,
                                           labels={
                                               KubernetesConfig.K8S_LABELS_OPGUID: op_inst.guid})  # Label for the service to bind to
        jobspec = V1JobSpec(template=V1PodTemplateSpec(metadata=pod_metadata, spec=podspec))
        kube_job = V1Job(metadata=job_metadata, spec=jobspec)
        return kube_job

    def _create_kube_podspec(self, container, shm_size=None, scheduler_name=KubernetesConfig.DEFAULT_SCHEDULER,
                             namespace=KubernetesConfig.K8S_NAMESPACE):
        logger.info("Creating pod with scheduler_name = %s, namespace = %s" % (scheduler_name, namespace))
        volumes = []
        if shm_size and isinstance(shm_size, int):
            dshm_vol = client.V1EmptyDirVolumeSource(medium="Memory", size_limit=shm_size)
            volumes.append(client.V1Volume(name='dshm', empty_dir=dshm_vol))
        if not volumes:
            volumes = None
        spec = client.V1PodSpec(containers=[container], scheduler_name=scheduler_name, restart_policy="OnFailure",
                                volumes=volumes,
                                image_pull_secrets=[client.V1LocalObjectReference(KubernetesConfig.IMAGE_PULL_SECRET)])
        return spec

    def _create_kube_container(self, op_inst, shm_size=None, image="romilb/nomad_client:latest"):
        name = op_inst.guid + "-container"
        assert(isinstance(name, str))
        env_vars = op_inst.get_envs()
        assert(isinstance(env_vars, dict))
        # env_vars = merge_dicts(op_inst.get_envs(), op_inst.custom_envs)
        logger.info("Creating container with image %s, envs = %s" % (image, str(env_vars)))
        container_envs = [V1EnvVar(k, str(v)) for k, v in env_vars.items()]
        container_ports = [V1ContainerPort(container_port=30000, name="rpc")]

        security_capabilites = V1Capabilities()
        security_capabilites.add = ['SYS_PTRACE', 'SYS_ADMIN']
        security_context = V1SecurityContext(allow_privilege_escalation=True,
                                             privileged=True,
                                             capabilities=security_capabilites)

        volume_mounts = []
        if shm_size and isinstance(shm_size, int):
            volume_mounts.append(client.V1VolumeMount(mount_path='/dev/shm', name='dshm'))
        if not volume_mounts:
            volume_mounts = None
        container = client.V1Container(name=name, image=image, tty=True,
                                       env=container_envs, ports=container_ports,
                                       volume_mounts=volume_mounts, security_context=security_context,
                                       image_pull_policy="Never")
        return container

    def _create_kube_service(self, k8s_id, ports, namespace=KubernetesConfig.K8S_NAMESPACE):
        '''
        :param ports: List of [[int targetport, int port]] to expose thru the service
        :return: Service object
        '''
        name = k8s_id + "-service"
        serviceports = []
        for portname, targetport, portnumber in ports:
            serviceports.append(V1ServicePort(name=portname, target_port=targetport, port=portnumber))
        metadata = client.V1ObjectMeta(name=name, namespace=namespace)
        spec = V1ServiceSpec(selector={KubernetesConfig.K8S_LABELS_OPGUID: k8s_id}, ports=serviceports)
        service = V1Service(metadata=metadata, spec=spec)
        return service
