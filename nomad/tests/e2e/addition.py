import os
import xmlrpc.client
from nomad.clientlib import nomad

connection_str = "http://127.0.0.1:30000"
rpc = xmlrpc.client.ServerProxy(connection_str, allow_none=True)
print(str(rpc.system.listMethods()))

def square(x):
    return x*x

def source():
    import random
    return random.randint(0,10)

fns = [source, square]
end = "kube-master"
start = "kube-node-1"
nomad.submit_pipeline(fns, start, end, 'demo', connection_str)