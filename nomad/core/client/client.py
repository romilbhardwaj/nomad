import os
import logging
import threading
import xmlrpc
import time
import sys
from queue import Queue

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
    class OperatorThread(threading.Thread):
        def __init__(self, incoming_queue, outgoing_queue, operator_func, is_first_operator):
            threading.Thread.__init__(self)
            self.daemon = False

            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.operator_func = operator_func
            self.is_first_operator = is_first_operator

        def work(self):
            while (True):
                if not self.is_first_operator:
                    message_dict = self.incoming_queue.get()  # Block, else run the generator op.
                    message = Message(**message_dict)
                    logger.info("Processing message in operator.")
                    args = message.get_args()
                else:
                    logger.info("This is the first operator, sleeping for 1s before working.")
                    args = []
                    time.sleep(1)
                output_message = Message(self.operator_func(*args))
                logger.info("Operator result = %s." % output_message)
                self.outgoing_queue.put(output_message)

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
                        out_message = self.outgoing_queue.get()  # This is a blocking call
                        logger.info("Forwarding message to next operator.")
                        self.next_operator_rpc_proxy.submit_message(out_message)

        def run(self):
            if not self.is_final_operator:
                logger.info("Connecting RPC proxy with the next operator. Connection string %s" % self.next_operator_rpc_uri)
                self.next_operator_rpc_proxy = xmlrpc.client.ServerProxy(self.next_operator_rpc_uri, allow_none=True)
                self.work()
            else:
                logger.info("This is the final operator, thus not launching the forwarding thread.")

    def __init__(self, guid, master_rpc_uri, operator_path=None, client_rpc_port=None, next_op_addr=None,
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
        self.guid = guid
        self.master_rpc_uri = master_rpc_uri
        if operator_path is None:
            self.operator_path = ClientConfig.DEAFULT_OPERATOR_DILL_PATH
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
            self.master_rpc_proxy = xmlrpc.client.ServerProxy(self.master_rpc_uri, allow_none=True)
            if self.next_op_addr is None:
                self.next_op_addr = self.master_rpc_proxy.get_next_op_address(self.guid)
        except:
            logger.exception("Error while setting up RPC connection to server.")
            raise

        # Init RPC Server
        methods_to_register = [self.submit_message, self.ready_check]
        logger.info("Creating RPC server with the port %d" % self.client_rpc_port)
        self.rpcserver = RPCServerThread(methods_to_register, self.client_rpc_port, multithreaded=False)
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
            self.notify_server_onalive()

        # Start threads.
        logger.info("Launching opreator thread.")
        self.opreator_thread = self.OperatorThread(self.incoming_queue, self.outgoing_queue, self.operator_func,
                                                   self.is_first_operator)
        self.opreator_thread.start()

        logger.info("Launching forwarding thread.")
        self.forwarding_thread = self.ForwardingThread(self.outgoing_queue, self.next_op_addr, self.is_final_operator)
        self.forwarding_thread.start()

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

    def submit_message(self, message):
        logger.info("Recieved message, appending to queue. : %s" % str(message))
        self.incoming_queue.put(message)

    def ready_check(self):
        return True

    @staticmethod
    def _load_operator(operator_path):
        with open(operator_path, "rb") as op_file:
            op = pickle.load(op_file)
        return op
