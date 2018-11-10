import os
import logging
import threading
import xmlrpc
import time
import sys

from nomad.core.utils.LoggerWriter import LoggerWriter
from nomad.utils.RPCServerThreads import RPCServerThread

# ====== BEGIN SETUP LOGGING =========

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-4s] %(message)s")

# Setup logging to file
os.makedirs(CONFIG.DEFAULT_LOG_DIR, exist_ok=True)
fileHandler = logging.FileHandler("{0}/{1}".format(CONFIG.DEFAULT_LOG_DIR, CONFIG.CLIENT_LOG_FILE_NAME))
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
        def __init__(self, incoming_queue, outgoing_queue, operator_func):
            threading.Thread.__init__(self)
            self.daemon = False

            self.incoming_queue = incoming_queue
            self.outgoing_queue = outgoing_queue
            self.operator_func = operator_func

        def work(self):
            while (True):
                for message in self.incoming_queue:
                    kwargs = message.get_args()
                    output = self.operator_func(kwargs)
                    self.outgoing_queue.append(output)

        def run(self):
            self.work()

    class ForwardingThread(threading.Thread):
        def __init__(self, outgoing_queue):
            raise NotImplementedError

    def __init__(self, guid, manager_rpc_uri, operator_func):
        self.guid = guid
        self.manager_rpc_uri = manager_rpc_uri
        self.operator_func = operator_func

        self.incoming_queue = []
        self.outgoing_queue = []

        # Setup manager RPCProxy
        self.standalone_mode = False    # When no server uri specified.
        try:
            self.master_rpc_proxy = xmlrpc.client.ServerProxy(self.master_rpc_uri, allow_none=True)
            self.next_op_addr = self.master_rpc_proxy.get_next_op_address(self.guid)
        except:
            logger.exception("Error while setting up RPC connection to server.")
            raise

        # Init RPC Server
        methods_to_register = [self.submit_message]
        self.rpcserver = RPCServerThread(methods_to_register, self.client_rpc_address, self.client_rpc_port, multithreaded=False)
        self.rpcserver.start()  # Run RPC server in separate thread

        # Test if RPC server is alive. Wait if it isn't.
        is_rpc_ready = False

        while not is_rpc_ready:
            is_rpc_ready = self.test_self_rpcserver()
            if not is_rpc_ready:
                logger.info("RPC Server is not ready. Sleeping for %d" % CONFIG.RPC_INIT_WAIT_INTERVAL)
                time.sleep(CONFIG.RPC_INIT_WAIT_INTERVAL)
            else:
                logger.info("RPC is ready. Proceed to notifying nomad master.")

        self.notify_server_onalive()

        # Start threads.
        self.opreator_thread = self.OperatorThread(self.incoming_queue, self.outgoing_queue, self.operator_func)
        self.opreator_thread.start()

        self.forwarding_thread = self.ForwardingThread(self.outgoing_queue)
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
        self.master_rpc_proxy.register_client_onalive(self.guid)
        logger.info("Registered client with GUID %s on the master." % str(self.client_info.gpus_allocated))

    def submit_message(self, message):
        self.incoming_queue.append(message)
