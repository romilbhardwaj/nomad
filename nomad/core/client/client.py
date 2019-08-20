import os
import logging
import threading
import xmlrpc
import time
import sys
from queue import Queue
from pympler.asizeof import asizeof
import pickle
from nomad.core.config import CONSTANTS
from nomad.core.types.message import Message

from nomad.core.utils.LoggerWriter import LoggerWriter
from nomad.core.utils.RPCServerThreads import RPCServerThread
import nomad.core.config.ClientConfig as ClientConfig

# ====== BEGIN SETUP LOGGING =========

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-4s] %(message)s")

# Setup logging to file
os.makedirs(ClientConfig.DEFAULT_LOG_DIR, exist_ok=True)
fileHandler = logging.FileHandler("{0}/{1}".format(ClientConfig.DEFAULT_LOG_DIR, ClientConfig.CLIENT_LOG_FILE_NAME))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

# Setup logging to console for Docker
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

sys.stderr = LoggerWriter(logger.warning)


# ======= LOGGER SETUP DONE =========


class NomadClient(object):
    last_output = None
    class OperatorThread(threading.Thread):
        def __init__(self, incoming_queue, outgoing_queue, operator_func, is_first_operator, is_final_operator, op_inst_guid, pid,
                     master_rpc_proxy):
            threading.Thread.__init__(self)
            self.daemon = False
            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.operator_func = operator_func
            self.is_first_operator = is_first_operator
            self.is_final_operator = is_final_operator
            self.master_rpc_proxy = master_rpc_proxy
            self.pid = pid
            self.op_inst_guid = op_inst_guid

        def work(self):
            global last_output
            while (True):
                message_start_timestamp = None
                if not self.is_first_operator:
                    logger.info("OpThread: Blocked on incoming queue.")
                    message = self.incoming_queue.get()  # Block, else run the generator op.
                    logger.info("OpThread: UNBlocked on incoming queue.")
                    message_start_timestamp = message.start_timestamp
                    args = message.get_args()
                else:
                    logger.info("This is the first operator, sleeping for 1s before working.")
                    args = []
                    time.sleep(1)
                op_start_time = time.time()
                if not self.is_first_operator:
                    op_result = self.operator_func(args) # REMOVED THE STAR (*args)
                else:
                    op_result = self.operator_func()
                op_end_time = time.time()
                last_output = op_result
                output_message = Message(op_result, start_timestamp=message_start_timestamp)
                if not self.is_final_operator:
                    self.outgoing_queue.put(output_message)
                logger.info("Operator result = %.10s (truncated), time taken = %f. Current out queue size = %d" % (output_message, (op_end_time - op_start_time), self.outgoing_queue.qsize()))

                #Submit Profiling data. TODO: Add mechanism to controll rate of profiling.
                msg_size = asizeof(op_result)
                self._submit_profiling_measurements({'cloud_execution_time': op_end_time - op_start_time, 'output_msg_size': msg_size})

        def _submit_profiling_measurements(self, measurements):

            op_guid = self.op_inst_guid.split('-instance')[0]
            logger.info('Submitting the following measurements for operator %s : %s' % (op_guid, str(measurements)))
            """
            Note: In order to update pipeline profiling we must use the operator guid, not op inst guid. 
                If we allow multiple instances pr operator in the future, we must change the format of the profiling data.
            For instance, we could average data across all instances. 
            """
            self.master_rpc_proxy.update_pipeline_profiling(self.pid, {op_guid:measurements})

        def run(self):
            self.work()


    class ForwardingThread(threading.Thread):
        def __init__(self, outgoing_queue, next_operator_rpc_uri, is_final_operator):
            threading.Thread.__init__(self)
            self.daemon = False

            self.outgoing_queue = outgoing_queue
            self.next_operator_rpc_uri = next_operator_rpc_uri
            self.is_final_operator = is_final_operator

            self.next_operator_rpc_proxy = None

        def work(self):
            while (1):
                ready = False
                try:
                    logger.info("Checking if next operator is ready.")
                    ready = self.next_operator_rpc_proxy.ready_check()
                except:
                    logger.exception("Next operator is not ready yet. Sleeping for %d seconds." % ClientConfig.RETRY_SLEEP_DURATION)
                    time.sleep(ClientConfig.RETRY_SLEEP_DURATION)
                if ready:
                    logger.info("Next operator is ready, starting forwarding loop.")
                    while (1):
                        logger.info("FWDThread: Blocked on outgoing queue.")
                        out_message = self.outgoing_queue.get()  # This is a blocking call
                        logger.info("FWDThread: UNBlocked on outgoing queue, forwarding message to next operator.")
                        if not out_message.start_timestamp: # It's the first operator sending the message
                            out_message.start_timestamp = time.time()
                        logger.info("FWDThread: Trying to submit message over RPC")
                        self.next_operator_rpc_proxy.submit_message(out_message)
                        logger.info("FWDThread: Message submitted over RPC")

        def run(self):
            if not self.is_final_operator:
                logger.info("Connecting RPC proxy with the next operator. Connection string %s" % self.next_operator_rpc_uri)
                self.next_operator_rpc_proxy = xmlrpc.client.ServerProxy(self.next_operator_rpc_uri, allow_none=True)
                self.work()
            else:
                logger.info("This is the final operator, thus not launching the forwarding thread.")

    def __init__(self, guid, master_rpc_uri, pid, operator_path=None, client_rpc_port=None, next_op_addr=None,
                 is_first_operator=False, is_final_operator=False, debug=False):
        '''
        :param guid: GUID for this client
        :type guid: str
        :param master_rpc_uri: RPC URI for the master
        :type master_rpc_uri: str
        :param operator_path: path to the dill file of the operator
        :type operator_path: str
        :param client_rpc_port: RPC port of the client
        :type client_rpc_port: int
        :param next_op_addr: Address of the next operator. If not specified, fetched from the master
        :type next_op_addr: str
        '''
        logger.info("Instantiating client")
        self.guid = guid
        self.master_rpc_uri = master_rpc_uri
        self.pid = pid
        if operator_path is None:
            self.operator_path = ClientConfig.DEAFULT_OPERATOR_PATH
        else:
            self.operator_path = operator_path
        self.next_op_addr = next_op_addr

        self.is_first_operator = is_first_operator
        self.is_final_operator = is_final_operator
        self.debug = debug

        if client_rpc_port is None:
            self.client_rpc_port = ClientConfig.RPC_DEFAULT_PORT
        else:
            if isinstance(client_rpc_port, int) and (client_rpc_port < CONSTANTS.MAX_PORT_NUM) and (
                    client_rpc_port > CONSTANTS.MIN_PORT_NUM):
                self.client_rpc_port = client_rpc_port
            else:
                raise TypeError(
                    "RPC Port must be int between %d and %d" % (CONSTANTS.MIN_PORT_NUM, CONSTANTS.MAX_PORT_NUM))

        self.operator_func = self._load_operator(self.operator_path)

        self.incoming_queue = Queue(maxsize=ClientConfig.MAX_INCOMING_QUEUE_SIZE)
        self.outgoing_queue = Queue(maxsize=ClientConfig.MAX_OUTGOING_QUEUE_SIZE)

        # Setup master RPCProxy
        self.standalone_mode = False  # When no server uri specified.
        try:
            logger.info("Setting up RPC connection to master with connection string %s" % self.master_rpc_uri)
            self.master_rpc_proxy = xmlrpc.client.ServerProxy(self.master_rpc_uri, allow_none=True)
            if not self.next_op_addr:
                logger.info("Querying master for the next operator address")
                self.next_op_addr = self.master_rpc_proxy.get_next_op_address(self.guid)
            else:
                logger.info("I already have a next_op address: %s. Not querying master." % str(self.next_op_addr))
        except:
            logger.exception("Error while setting up RPC connection to server.")
            raise

        # Init RPC Server
        methods_to_register = [self.submit_message, self.ready_check, self.get_last_output]
        logger.info("Creating client RPC server with the port %d" % self.client_rpc_port)
        self.rpcserver = RPCServerThread(methods_to_register, self.client_rpc_port, multithreaded=True)
        self.rpcserver.start()  # Run RPC server in separate thread

        # Test if RPC server is alive. Wait if it isn't.
        is_rpc_ready = False

        while not is_rpc_ready:
            is_rpc_ready = self.test_self_rpcserver()
            if not is_rpc_ready:
                logger.info("RPC Server is not ready. Sleeping for %d" % ClientConfig.RPC_INIT_WAIT_INTERVAL)
                time.sleep(ClientConfig.RPC_INIT_WAIT_INTERVAL)
            else:
                logger.info("RPC is ready. Proceed to notifying nomad master.")

        if not self.debug:
            logger.info("Notifying master that I'm alive!")
            self.notify_server_onalive()

        # Start threads.
        logger.info("Launching opreator thread.")
        self.opreator_thread = self.OperatorThread(self.incoming_queue, self.outgoing_queue, self.operator_func,
                                                   self.is_first_operator, self.is_final_operator, self.guid, self.pid, self.master_rpc_proxy)
        self.opreator_thread.start()

        logger.info("Launching forwarding thread with next_operator_addr: %s" % str(self.next_op_addr))
        self.forwarding_thread = self.ForwardingThread(self.outgoing_queue, self.next_op_addr, self.is_final_operator)
        self.forwarding_thread.start()

        logger.info("Client instantiated with fields: %s" % str(self.__dict__))

    def test_self_rpcserver(self):
        uri = "http://localhost:%d" % int(self.client_rpc_port)
        rpc = xmlrpc.client.ServerProxy(uri, allow_none=True)
        try:
            rpc.system.listMethods()
        except:
            return False
        return True

    def notify_server_onalive(self):
        logger.info("Notifying server onalive.")
        self.master_rpc_proxy.register_client_onalive(self.guid)

    def get_last_output(self):
        # TODO(romilb): We should probably serialize last_output since xmlrpc wont work well with nested datatypes.
        return last_output

    def submit_message(self, message_dict):
        logger.info("Recieved message.")
        message = Message(**message_dict)
        logger.info("Total time since start = %f." % (time.time() - message.start_timestamp))
        logger.info("Content: %.10s (truncated)" % str(message))
        self.incoming_queue.put(message)
        logger.info("Incoming Queue size: %d" % self.incoming_queue.qsize())

    def ready_check(self):
        return True

    @staticmethod
    def _load_operator(operator_path):
        with open(operator_path, "rb") as op_file:
            op = pickle.load(op_file)
        return op
