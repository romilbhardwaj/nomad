# Nomad - Hierarchical Computation Framework for IoT applications
Modern IoT applications are computationally monolithic and built assuming a "flat" computing architecture, where processing and inference on data from edge devices is done exclusively on the cloud. Nomad is a distributed data-processing framework that can intelligently split the different stages of a data processing pipeline across the edge-cloud continuum with minimal developer effort.

# Quick Start for Developers
Nomad supports applications that are designed as pipelines, where the output can be expressed as a sequence of independent transformations on the input. For instance, a face recognition  pipeline ingests a frame, performs pre-processing (pixel normalization), detects faces using a statistical model, and then applies a deep neural network to infer the identity of the person.

Such pipelines can be easily partitioned with Nomad. For instance, consider a pipeline which generates a random number at the source node, squares it, and writes it to a file. A monolithic program would express it something like this:
```python
# This method is invoked periodically
def pipeline():
    import random
    r = random.randint(0,10)
    square = r*r
    with open("myfile.txt", 'w') as f:
        f.write(str(square) + "\n")
```

However, distributing this program across multiple machines would be complex, requiring the developer figure out the best possible placement of these operations. Moreover, she would also need to implement coordination between the stages of the pipeline, setting up a message passing system and managing the devices.

Nomad makes this process easier. A similar pipeline in Nomad would look like this:

```python
import nomad

NOMAD_MASTER = "http://127.0.0.1:30000"

# Write pipeline steps as independent python methods
def write_to_file(x):
    with open("/tmp/output.txt", 'a') as f:
        f.write(str(x) + "\n")

def square(x):
    return x*x

def source():
    import random
    return random.randint(0,10)

# Declare the sequence of operators in a list
operators = [source, square, write_to_file]

# Specify the devices where the first operator and last operators are to be placed
start_node = "my_edge_device"
end_node = "my_cloud_VM"

pipeline_id = 'test'
# Submit the pipeline to the nomad master.
# This will make latency and compute aware placement decisions and instantiate the pipeline.

nomad.submit_pipeline(operators, start_node, end_node, pipeline_id, connection_str = NOMAD_MASTER)
```

# Installation
## Prequisites
Nomad has been tested on Python 3.5.6, but should also work on 2.7 The Nomad master requires an installation of Docker 18.09.0 or higher and Kubectl 1.12 or higher.

## Client library installation
Client libraries can be installed by cloning the repo and installing the python client module with:
```
git clone https://github.com/romilbhardwaj/nomad.git
cd nomad
python setup.py install
```

Check if the installation succeeded with:
```
python -c "import nomad;print(nomad.__version__)"
```

## Setting up the Nomad Master
Nomad uses Kubernetes for cluster management and orchestration. It can automatically read cluster information from the the cluster it is instantiated in. If your Kubernetes cluster is already deployed:
 1) Run `docker\images\master\k8s\init.sh` to setup the Nomad namespace and service account.
 2) Run 'docker\images\master\k8s\startup.sh' to start the Nomad master and the associated services.
 3) To stop the Nomad master, run 'docker\images\master\k8s\cleanup.sh'.

### Setting up a virtual kubernetes cluster for development
To experiment and develop with Nomad on a single machine, you can setup a local docker-in-docker Kubernetes cluster.
1) Install [Docker 18.09](https://docs.docker.com/install/) and [kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/#install-kubectl).
2) Run the dind cluster scripts: 

    ```
    cd docker\images\master\k8s
    chmod +x dind-cluster-v1.12.sh
    ./dind-cluster-v1.12.sh up
    ```

3) Run `kubectl get nodes` to verify setup.