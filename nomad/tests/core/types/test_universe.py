import unittest
from core.universe.universe import Universe
class TestUniverseMethods(unittest.TestCase):
    def setUp(self):
        self.universe = Universe()
        self.pid = '123'
        self.fns = ['fn1.txt', 'fn2.txt', 'fn3.txt']
        self.start = 1
        self.end = 4

    def test_add_pipeline(self):
        pid = self.universe.add_pipeline(self.fns, self.start, self.end, self.pid)
        pipeline = self.universe.get_pipeline(pid)
        self.assertTrue(len(pipeline.operators) == 3)

        for i, op_guid in enumerate(pipeline.operators):
            self.assertEqual(op_guid, pid + '-%d' % i)

    def test_update_pipeline_profiling(self):
        pid = self.universe.add_pipeline(self.fns, self.start, self.end, self.pid)

        pipeline_profiling_info = {
            "123-0": {

                    "label": "pre_processing",
                    "order": 0,
                    "cloud_execution_time": 10,
                    "output_msg_size": 100
            },

            "123-1": {
                    "label": "resampling",
                    "order": 1,
                    "cloud_execution_time": 5,
                    "output_msg_size": 5
            },

            "123-2": {
                    "label": "inference",
                    "order": 2,
                    "cloud_execution_time": 1,
                    "output_msg_size": 1
            }
        }

        self.universe.update_pipeline_profiling(pid, pipeline_profiling_info)
        for op_id, operator_profile in pipeline_profiling_info.items():
            op = self.universe.get_operator(op_id)

            self.assertEqual(op._cloud_execution_time, operator_profile["cloud_execution_time"])






if __name__ == '__main__':
    unittest.main()