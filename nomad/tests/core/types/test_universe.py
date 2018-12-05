import unittest
from core.universe.universe import Universe
class TestUniverseMethods(unittest.TestCase):
    def setUp(self):
        self.universe = Universe()

    def test_add_pipeline(self):
        pid = '123'
        fns = ['fn1.txt', 'fn2.txt', 'fn3.txt']
        start = 1
        end = 4
        pid = self.universe.add_pipeline(fns, start, end, pid)
        pipeline = self.universe.get_pipeline(pid)
        self.assertTrue(len(pipeline.operators) == 3)

        for i, op_guid in enumerate(pipeline.operators):
            self.assertEqual(op_guid, pid + '-%d' % i)

if __name__ == '__main__':
    unittest.main()