import time
import unittest
import xmlrpc
import subprocess

from nomad.core.client.client import NomadClient


class TestMaster(unittest.TestCase):
    def setUp(self):
        self.master_process = subprocess.Popen(["python", "../../../core/master/master_launcher.py", "--rpc_port=20000"])
        time.sleep(2)
        self.client = NomadClient("myclient", master_rpc_uri="http://127.0.0.1:20000", operator_path="add_op.dill", client_rpc_port=10000)


    def test_register(self):
        self.client.notify_server_onalive()

    def tearDown(self):
        self.master_process.terminate()

if __name__ == '__main__':
    unittest.main()
