import os
import xmlrpc.client
rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:30000", allow_none=True)
print(str(rpc.system.listMethods()))

fns = ["generate_random_int", "square_op", "square_op"]
end = "kube-master"
start = "kube-node-1"
rpc.submit_pipeline(fns, start, end, 'demo')