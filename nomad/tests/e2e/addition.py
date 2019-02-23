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

import docker
import os
client = docker.from_env()
i=1
base_dir = '/tmp/op_%d/' % i
file_name = base_dir + 'operator.pickle'
#TODO: the docker repo should be loaded from a config file
tag = "lab11nomad/operators:%s_op_%d_img" % ("demo", i)

#build image using client base image
build_src_path = '/tmp'
pickle_rel_path = os.path.relpath(file_name, build_src_path)


docker_image, build_log = client.images.build(tag=tag, path='/tmp', buildargs={'PYTHON_PICKLE_PATH': pickle_rel_path}, rm=True)
print("Build result: \n%s" % str(docker_image))
for line in build_log:
    print(line)

#push_result = client.images.push(repository=tag, auth_config={'username': DockerConfig.USERNAME, 'password': DockerConfig.PASSWORD})