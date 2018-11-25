import socketserver
import threading
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler


class MultiThreadedXMLRPCServer(socketserver.ThreadingMixIn, SimpleXMLRPCServer):
    pass


class LocalStackTraceHandler(SimpleXMLRPCRequestHandler):
     def _dispatch(self, method, params):
         try:
             return self.server.funcs[method](*params)
         except:
             import traceback
             traceback.print_exc()
             raise

class RPCServerThread(threading.Thread):
    def __init__(self, methods_to_register, rpc_port, rpc_address="", multithreaded=True):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stoprequest = threading.Event()
        if multithreaded:
            self.localServer = MultiThreadedXMLRPCServer((rpc_address, rpc_port), LocalStackTraceHandler, allow_none=True, logRequests=False)
        else:
            self.localServer = SimpleXMLRPCServer((rpc_address, rpc_port), LocalStackTraceHandler, allow_none=True, logRequests=False)
        self.localServer.register_introspection_functions()
        for method in methods_to_register:
            self.localServer.register_function(method)

    def run(self):
        self.localServer.serve_forever()
