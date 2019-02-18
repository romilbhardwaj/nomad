import time
import unittest
import subprocess
import xmlrpc.client
import os
import signal

import clientlib.nomad as nomad

class TestSubmitPipeline(unittest.TestCase):
    def setUp(self):
        #self.rpc_server_process = subprocess.Popen(["python", "submit_pipeline_rpc_launcher.py", "--rpc_port=20000"])
        #self.rpc_uri = "http://127.0.0.1:20000"
        #time.sleep(2)
        #self.client = NomadClient("myclient", master_rpc_uri="http://127.0.0.1:20000", operator_path="add_op.dill", client_rpc_port=10000)
        self.rpc_uri = "http://127.0.0.1:8000"
        self.rpc_process = subprocess.Popen(['python', 'tests/core/master/submit_pipeline_rpc_launcher.py'], preexec_fn=os.setsid)
        time.sleep(2)

    def test_receive_pipeline(self):
        def op1(s):
            return s - 1

        def op2(n):
            return  n**2

        try:
            nomad.submit_pipeline([op1, op2], 'start', 'end', '123', self.rpc_uri)

        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def tearDown(self):
        os.killpg(os.getpgid(self.rpc_process.pid), signal.SIGTERM)
        self.rpc_process.wait()

if __name__ == '__main__':
    unittest.main()