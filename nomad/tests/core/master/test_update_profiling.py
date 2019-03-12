import time
import unittest
import subprocess
import xmlrpc.client
import os
import signal

import nomad.clientlib.nomad as nomad

class TestSubmitPipeline(unittest.TestCase):
    def setUp(self):
        #self.rpc_server_process = subprocess.Popen(["python", "mock_master_rpc_launcher.py", "--rpc_port=20000"])
        #self.rpc_uri = "http://127.0.0.1:20000"
        #time.sleep(2)
        #self.client = NomadClient("myclient", master_rpc_uri="http://127.0.0.1:20000", operator_path="add_op.dill", client_rpc_port=10000)
        self.pid = '123'
        self.rpc_uri = "http://127.0.0.1:8000"
        self.rpc_process = subprocess.Popen(['python', 'nomad/tests/core/master/mock_master_rpc_launcher.py'], preexec_fn=os.setsid)
        time.sleep(2)

    def test_get_node_profiling(self):
        try:
            #TODO: make sure this returns a dict with node labels as keys.
            node_profiling = nomad.get_node_profiling(self.rpc_uri)
            print(node_profiling)
        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def test_update_node_profiling(self):
        new_node_profile = {
                "romilbx1yoga": {
                "C": 2.0,
                "architecture": "x86"
            },

                "raspberrypi": {
                "C": 1.1,
                "architecture": "arm"
                }
            }
        try:

            nomad.update_node_profiling(new_node_profile, self.rpc_uri)
            node_profiling = nomad.get_node_profiling(self.rpc_uri)
            print(node_profiling)
        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def test_get_network_profiling(self):
        links = [
            {
                    "from": "romilbx1yoga",
                    "to": "raspberrypi",
                    "bandwidth": 10000,
                    "latency": 0.3

            },
            {
                    "from": "raspberrypi",
                    "to": "romilbx1yoga",
                    "bandwidth": 10000,
                    "latency": 0.3
            }
        ]
        try:
            network_profiling = nomad.get_network_profiling(self.rpc_uri)
            print(network_profiling)
            for l in links:
                self.assertTrue(l in network_profiling)


        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def test_update_network_profiling(self):
        new_links = [
            {
                "from": "romilbx1yoga",
                "to": "raspberrypi",
                "bandwidth": 20000,
                "latency": 0.4

            },
            {
                "from": "raspberrypi",
                "to": "romilbx1yoga",
                "bandwidth": 50000,
                "latency": 0.5
            }
        ]
        try:
            nomad.update_network_profiling(new_links, self.rpc_uri)
            network_profiling = nomad.get_network_profiling(self.rpc_uri)
            print(network_profiling)
            for l in new_links:
                self.assertTrue(l in network_profiling)

        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def test_get_pipeline_profiling(self):

        initial_pipeline_profile = {
            '123-0': {
            "cloud_execution_time": 0.1,
            "output_msg_size": 1,
            },

            '123-1': {
            "cloud_execution_time": 0.5,
            "output_msg_size": 1,
            },
            '123-2':{
            "cloud_execution_time": 1,
            "output_msg_size": 1,
            }
        }
        try:
            pipeline_profiling = nomad.get_pipeline_profiling(self.pid, self.rpc_uri)
            print(pipeline_profiling)
            for k, v in initial_pipeline_profile.items():
                self.assertTrue(k in pipeline_profiling and pipeline_profiling[k] == v)

        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)

    def test_update_pipeline_profiling(self):
        new_pipeline_profile = {
            '123-0': {
                "cloud_execution_time": 1,
                "output_msg_size": 5,
            },

            '123-1': {
                "cloud_execution_time": 1.5,
                "output_msg_size": 1,
            },
            '123-2': {
                "cloud_execution_time": 2,
                "output_msg_size": 3,
            }
        }
        try:
            nomad.update_pipeline_profiling('123', new_pipeline_profile, self.rpc_uri)
            pipeline_profiling = nomad.get_pipeline_profiling(self.pid, self.rpc_uri)
            print(pipeline_profiling)
            for k, v in new_pipeline_profile.items():
                self.assertTrue(k in pipeline_profiling and pipeline_profiling[k] == v)

        except xmlrpc.client.Fault as err:
            print("A fault occurred")
            print("Fault code: %d" % err.faultCode)
            print("Fault string: %s" % err.faultString)


    def tearDown(self):
        os.killpg(os.getpgid(self.rpc_process.pid), signal.SIGTERM)
        self.rpc_process.wait()

if __name__ == '__main__':
    unittest.main()