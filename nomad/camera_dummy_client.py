import os
import xmlrpc.client
import sys

rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:30000", allow_none=True)
print(str(rpc.system.listMethods()))

fns = ["dummy_read_camera", "downsample_image", "get_face_boundingbox", "get_face_emotion2"]
end = "kube-master"
start = "kube-node-1"
rpc.submit_pipeline(fns, start, end, 'demo')