import unittest
from core.master.master import Master

class TestMaster(unittest.TestCase):
    def setUp(self):
        self.master = Master()

    def test_submit_pipeline(self):
        fns = ['fn1.txt', 'fn2.txt', 'fn3.txt']
        start = 'phone'
        end = 'pc'
        pid = '123'
        self.master.submit_pipeline(fns, start, end, pid)
        print('hello')

if __name__ == '__main__':
    unittest.main()