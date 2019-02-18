import unittest
import clientlib.nomad as nomad

class TestNomad(unittest.TestCase):

    def setUp(self):
        self.start_node = 'n1'
        self.end_node ='n2'
        self.pipeline_id = 'some_id'
        self.master_ip = 'ipaddrej'

    def test_submit_pipeline(self):
        def op1(n):
            return n - 1

        def op2(n):
            return  n**2

        nomad.submit_pipeline([op1, op2], self.start_node, self.end_node, self.pipeline_id, self.master_ip)


if __name__ == '__main__':
    unittest.main()
