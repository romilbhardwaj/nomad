# This module watches the kubernetes API and handles pod allocation (AKA placement)
import json
import logging

import nomad.core.config.KubernetesConfig as KubernetesConfig

from ..config import CONSTANTS
from ..config import SchedulerConfig

from collections import deque
from kubernetes import client, config, watch

logger = logging.getLogger(__name__)


class KubernetesScheduler(object):

    def __init__(self, universe, scheduler_name=SchedulerConfig.K8S_SCHEDULER_NAME):
        logger.info("Initializing KubernetesScheduler")
        logger.info("Using in-cluster auth.")
        config.load_incluster_config()
        self.universe = universe
        self.kubecoreapi = client.CoreV1Api()
        self.scheduler_name = scheduler_name
        logger.info("Scheduler Pre-init done.")

    def get_allocation(self, op_guid):
        op_inst = self.universe.get_operator_instance(op_guid)
        allotted_node = op_inst.node_id
        return allotted_node

    def k8s_schedule(self, name, node, namespace=SchedulerConfig.K8S_NAMESPACE):
        logger.info("Scheduling object %s on node %s." % (str(name), str(node)))

        body = self.create_k8s_binding(name, node)
        result = False
        try:
            result = self.kubecoreapi.create_namespaced_binding(namespace, body)
        except ValueError as e:  # TODO: Dirty hack till kub-python fixes their api.
            if str(e) != "Invalid value for `target`, must not be `None`":
                raise
            else:
                logger.info("Recieved response from API, but no target value... ignoring exception.")
        return result

    @staticmethod
    def create_k8s_binding(name, node):
        target = client.V1ObjectReference()
        target.kind = "Node"
        target.apiVersion = "v1"
        target.name = node
        meta = client.V1ObjectMeta()
        meta.name = name
        body = client.V1Binding(metadata=meta, target=target)
        return body

    def run(self):
        w = watch.Watch()
        logger.info("Watch initialized")
        waiting_objects = deque()  # This queue maintains list of pods that were not scheduled due to unavailable nodes. This list maintains priority order and tries to schedule waiting ops every time kubernetes state changes
        for new_event in w.stream(self.kubecoreapi.list_namespaced_pod, SchedulerConfig.K8S_NAMESPACE):
            logger.info("Recieved object %s and event type %s, adding to wait queue." % (
            new_event['object'].metadata.name, new_event['type']))
            waiting_objects.append(new_event)
            num_waiting = len(waiting_objects)
            logger.info("Current k8s scheduler wait queue length = %d" % num_waiting)
            for i in range(0, num_waiting):
                event = waiting_objects.popleft()
                if event['object'].status.phase == "Pending" and event['object'].spec.node_name == None and event['object'].spec.scheduler_name == self.scheduler_name:
                    try:
                        logger.info("Trying to schedule k8s object %s" % event['object'].metadata.name)
                        if KubernetesConfig.K8S_LABELS_OPGUID not in event['object'].metadata.labels:
                            logger.warning("Unable to schedule object %s without metadata label %s. Continuing.." % (event['object'].metadata.name,
                                                                                                                     KubernetesConfig.K8S_LABELS_OPGUID))
                            continue
                        op_guid = event['object'].metadata.labels[KubernetesConfig.K8S_LABELS_OPGUID]
                        try:
                            allotted_node_name = self.get_allocation(op_guid)
                            logger.info("Got allocation node - %s" % str(allotted_node_name))
                        except RuntimeWarning as e:
                            logger.exception("Unable to allocate %s: %s, adding it back to the wait queue." % (event['object'].metadata.name, str(e)))
                            waiting_objects.append(event)
                            continue
                        result = self.k8s_schedule(event['object'].metadata.name, allotted_node_name)
                    except client.rest.ApiException as e:
                        logger.warning("API Exception - %s" % str(json.loads(e.body)['message']))
                else:
                    # Do nothing since object is already scheduled.
                    pass


# Only for debugging
if __name__ == '__main__':
    k = KubernetesScheduler()
    k.run()
