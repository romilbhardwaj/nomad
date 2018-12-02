import logging
import shlex
import threading
import unittest
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()

logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(name)-4s] %(message)s")

#

def launch_client_process_and_stream(command):
    args = shlex.split(command)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    logger.info("Launched process %s " % command)
    for line in process.stdout:
        print(line)

class TestClient(unittest.TestCase):
    def test_message_passing(self):
        '''
        Launches two client processes, one generating random numbers and the other operator squares it
        '''
        self.assertEqual(True,True)
        print("HELLO")
        logger.info("Logged hello")
        source_client_command = "python ../../../core/client/client_launcher.py source_op http://127.0.0.1:10000 --operator_path ../master/generate_random_int.pickle --debug --is_first --next_op_addr http://127.0.0.1:20208"
        final_client_command = "python ../../../core/client/client_launcher.py final_op http://127.0.0.1:10000 --operator_path ../master/square_op.pickle --debug --is_final --rpc_port 20208"
        source_thread = threading.Thread(target=launch_client_process_and_stream, args=[source_client_command])
        final_thread = threading.Thread(target=launch_client_process_and_stream, args=[final_client_command])
        final_thread.start()
        source_thread.start()
        source_thread.join()
        final_thread.join()

if __name__ == '__main__':
    unittest.main()
