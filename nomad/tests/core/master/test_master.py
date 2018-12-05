import unittest
import xmlrpc
import subprocess

class TestMaster(unittest.TestCase):
    def setUp(self):
        self.master_process = subprocess.Popen(["python", "../../../core/master/master_launcher.py", "--rpc_port=20000"])

    def test_get_next_op(self):
        manager_rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:20000", allow_none=True)
        next_op_addr = manager_rpc.get_next_op_address("test")
        self.assertEqual(next_op_addr, "http://127.0.0.1:10000")

    def tearDown(self):
        self.master_process.terminate()

if __name__ == '__main__':
    unittest.main()
