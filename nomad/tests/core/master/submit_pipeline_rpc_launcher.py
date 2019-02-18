from xmlrpc.server import SimpleXMLRPCServer
import docker
import os
import pickle
import shutil

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

def write_to_file(binary_obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'wb') as f:
        f.write(binary_obj.data)

server = SimpleXMLRPCServer(("localhost", 8000))
print("Listening on port 8000...")
server.register_function(receive_pipeline, 'receive_pipeline')
server.serve_forever()