import xmlrpc

from nomad.core.config import ClientConfig
from nomad.core.utils.helpers import construct_xmlrpc_addr


class Operator:
    def __init__(self, guid, l='', fn_images=None, t=0, s=0, is_first=False, is_final=False):
        self.guid = guid
        self._label = l #Name of operator
        self._fn_images = fn_images # dictionary mapping arch -> image string
        self._cloud_execution_time = t #Time to execute the operator in a cloud environment on a typical workload. Measured in seconds
        self._output_msg_size = s # Size of operator output in bytes assuming a typical input.
        self._next = None # GUID of next op in pipeline
        self._op_instances = []
        self.is_first = is_first
        self.is_final = is_final

    def get_op_inst_guid(self):
        return self.guid + "-instance" + str(len(self._op_instances))

    def append_op_instance(self, op_inst_guid):
        self._op_instances.append(op_inst_guid)

    def cloud_execution_time(self):
        return self._cloud_execution_time
    
    def msg_size_bytes(self):
        return self._output_msg_size

    def set_cloud_execution_time(self, t):
        self._cloud_execution_time = t

    def set_output_msg_size(self, s):
        self._output_msg_size = s

class OperatorInstance(object):
    def __init__(self, guid, pipeline_guid, operator_guid, node_id=None, client_ip=None, operator_path=None, is_first=False, is_final=False, image=None):
        '''
        Defines an operator instance running on the network. Associated with an operator and a pipeline.
        :param guid: GUID, typically of the form <pipeline_guid>-<operator_guid>-<instance_guid>
        :type guid: str
        :param pipeline_guid: GUID of the parent pipeline
        :type pipeline_guid: str
        :param operator_guid: GUID of the operator
        :type operator_guid: str
        :param node_id: id of the node in kubernetes where it is launched
        :type node_id: str
        :param client_ip: IP of the client
        :type client_ip: str
        :param operator_path: path of the operator in the client docker image
        :type image: str
        '''
        self.guid = guid
        self.node_id = node_id  # Node Id where it is has been placed by the scheduler
        self.client_guid = guid     #TODO: Redundant, can this be removed?
        self.client_ip = client_ip
        self.operator_path = operator_path
        self.operator_guid = operator_guid
        self.pipeline_guid = pipeline_guid
        self.is_first = is_first
        self.is_final = is_final
        self.envs = None
        self.image = image #Docker image tag
        self.state = None

    def update_ip(self, client_ip):
        self.client_ip = client_ip

    def update_image(self, image_tag):
        self.image = image_tag

    def update_state(self, state):
        self.state = state

    def set_envs(self, master_rpc_address, client_rpc_port = ClientConfig.RPC_DEFAULT_PORT, debug=False):
        self.envs = {
            ClientConfig.ENVVAR_GUID: self.guid,
            ClientConfig.ENVVAR_MASTERRPC: master_rpc_address,
            ClientConfig.ENVVAR_RPCPORT: client_rpc_port,
            ClientConfig.ENVVAR_OPERATORPATH: self.operator_path,
            ClientConfig.ENVVAR_IS_FIRST: self.is_first,
            ClientConfig.ENVVAR_IS_FINAL: self.is_final,
            ClientConfig.ENVVAR_DEBUG: debug
        }

    def get_envs(self):
        return self.envs

    def get_last_output(self):
        '''
        Gets the last output from the operator instance. Must be instantiated. Returns none if no output has been produced yet.
        '''
        if self.client_ip is None:
            # TODO(romilb): Return None instead of exception?
            raise Exception("Operator is not instantiated yet.")
        instance_rpc = xmlrpc.client.ServerProxy(construct_xmlrpc_addr(self.client_ip, ClientConfig.RPC_DEFAULT_PORT), allow_none=True)
        try:
            result = instance_rpc.get_last_output()
        except:
            result = None
        return result