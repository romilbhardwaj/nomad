import xmlrpc.client

rpc = xmlrpc.client.ServerProxy("http://127.0.0.1:30000", allow_none=True)
print(str(rpc.system.listMethods()))

fns = ["read_picamera", "downsample_image", "get_face_boundingbox", "get_face_emotion"]
end = "romilbx1yoga"
start = "raspberrypi"
rpc.submit_pipeline(fns, start, end, 'demo')