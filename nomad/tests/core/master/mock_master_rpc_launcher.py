from xmlrpc.server import SimpleXMLRPCServer
import docker
import os
import pickle
import shutil
from nomad.core.universe.universe import Universe
pid = '123'
pipeline_profiling = {
    '123-0': {
    "cloud_execution_time": 0.1,
    "output_msg_size": 1,
    },

    '123-1': {
    "cloud_execution_time": 0.5,
    "output_msg_size": 1,
    },
    '123-2':{
    "cloud_execution_time": 1,
    "output_msg_size": 1,
    }
}
node_profiling = {
    "romilbx1yoga": {
      "C": 1.0,
      "architecture": "x86"
    },

    "raspberrypi": {
      "C": 0.1,
      "architecture": "rpiarm"
    }
    }
link_profiling = [
    {
            "from": "romilbx1yoga",
            "to": "raspberrypi",
            "bandwidth": 10000,
            "latency": 0.3

    },
    {
            "from": "raspberrypi",
            "to": "romilbx1yoga",
            "bandwidth": 10000,
            "latency": 0.3
    }
    ]

node_list = ["romilbx1yoga", "raspberrypi"]
universe = Universe()
universe.create_cluster(node_list)
universe.update_network_profiling(link_profiling)
universe.update_node_profiling(node_profiling)
universe.add_pipeline(['img1', 'img2', 'img3'], start='romilbx1yoga', end='raspberrypi', id=pid)
universe.update_pipeline_profiling(pid, pipeline_profiling)

def receive_pipeline(ops, start, end, pid):
    # create client
    client = docker.from_env()
    images = []

    for i, op_pickle in enumerate(ops):
        # Copy dockerfile to tmp
        shutil.copy('tests/ext/Dockerfile', 'tests/tmp/Dockerfile')
        shutil.copy('tests/ext/start_script.sh', 'tests/tmp/start_script.sh')
        # add pickle to tmp
        # Writing file to local storage
        file_name = 'tests/tmp/op_%d/op.pickle' % i
        write_to_file(op_pickle, file_name)

        #with open(file_name, 'rb') as f:
        #    fn = pickle.load(f)
        #    print(fn(2))

        tag = "alvinghouas/%s_op_%d_img" % (pid, i)
        # building image using client base image
        docker_image = client.images.build(tag=tag, path='tests/tmp',
                                           buildargs={'python_pickle_path': file_name})
        # push image to docker hub
        client.images.push(repository=tag)
        images.append(tag)

    print(images)
    return 1


#TODO: Make sure master has support for all these methods
def update_node_profiling(new_node_profile): # x
    universe.update_node_profiling(new_node_profile)

def get_node_profiling(): # x
    return universe.get_node_profiling()

def get_network_profiling(): # x
    return universe.get_network_profiling()

def update_network_profiling(new_network_profile): #x
    universe.update_network_profiling(new_network_profile)

def get_pipeline_profiling(pid): #x
    return universe.get_pipeline_profiling(pid)

def update_pipeline_profiling(pid, pipeline_profiling):
    universe.update_pipeline_profiling(pid, pipeline_profiling)

def write_to_file(binary_obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'wb') as f:
        f.write(binary_obj.data)

server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
print("Listening on port 8000...")
server.register_function(receive_pipeline, 'receive_pipeline')
server.register_function(get_node_profiling, 'get_node_profiling')
server.register_function(update_node_profiling,  'update_node_profiling')
server.register_function(get_network_profiling, 'get_network_profiling')
server.register_function(update_network_profiling, 'update_network_profiling')
server.register_function(get_pipeline_profiling, 'get_pipeline_profiling')
server.register_function(update_pipeline_profiling, 'update_pipeline_profiling')
server.serve_forever()