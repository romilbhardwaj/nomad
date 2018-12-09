import os
import xmlrpc.client
import sys

num = str(sys.argv[1])
rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:30000", allow_none=True)
print(str(rpc.system.listMethods()))

fns = ["generate_" + num, "no_op"]
end = "kube-master"
start = "kube-master"
rpc.submit_pipeline(fns, start, end, 'bench')