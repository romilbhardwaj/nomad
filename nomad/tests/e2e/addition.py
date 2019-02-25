import os
import xmlrpc.client
from nomad import submit_pipeline

connection_str = "http://127.0.0.1:30000"
rpc = xmlrpc.client.ServerProxy(connection_str, allow_none=True)
print(str(rpc.system.listMethods()))

def write_to_file(x):
    with open("/tmp/output.txt", 'a') as f:
        f.write(str(x) + "\n")

def square(x):
    return x*x

def source():
    import random
    return random.randint(0,10)

fns = [source, square, write_to_file]
profiling = [{
    "cloud_execution_time": 0.1,
    "output_msg_size": 1,
    },
    {
    "cloud_execution_time": 0.5,
    "output_msg_size": 1,
    },
    {
    "cloud_execution_time": 1,
    "output_msg_size": 1,
    },
]

end = "kube-master"
start = "kube-node-1"
submit_pipeline(fns, start, end, 'demo', connection_str, profiling)