# Nomad Tutorial
This tutorial will introduce you to the Nomad programming model. We will start by setting up a virtual Kubernetes cluster locally on our machine and launching the nomad master on this cluster. We will then write a simple sequential pipeline in python and then instantiate it on the nomad cluster.

## Step 0 - Prerequisites
* [Docker 18.09 or above](https://docs.docker.com/install/)
* Python 3 or above

<!---## Step 1 - Launch the Tutorial Container
We will be running this tutorial inside a docker container which has nomad dependencies pre-installed. To launch the container, run:
```bash
chmod +x run_tutorial.sh
./run_tutorial.sh
```
This should pull the latest tutorial image and launch the container.
-->

## Step 1 - Setting up the Virtual Cluster
Nomad uses Kubernetes to orchestrate and schedule pipelines. In deployment this cluster would span across machines on the edge and the cloud, but for this tutorial we'll be creating a virtual cluster locally on our machines. For this, we will be using [kubeadm-dind-cluster](https://github.com/kubernetes-sigs/kubeadm-dind-cluster), a utility which creates kubernetes nodes as local docker containers. To use this, simply run:
```bash
cd ../docker/images/master/k8s

# Run the script
chmod +x dind-cluster-v1.12.sh
./dind-cluster-v1.12.sh up
```

This will take some time to execute. After this is done, you should add kubectl to your PATH. This will allow you to interface with the cluster.

```bash
# Add kubectl binaries to PATH
export PATH="$HOME/.kubeadm-dind-cluster:$PATH"
echo "export PATH=\"$HOME/.kubeadm-dind-cluster:$PATH\"" >> ~/.bashrc
```

It is also recommended to enable kubectl autocompletion by following [this guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/#enabling-shell-autocompletion).

 After kubectl is setup, you should be able to run `kubectl get nodes` to verify that you are running a kubenetes cluster with 3 nodes in it:
```bash
romilb@romilx1:/$ kubectl get nodes
NAME          STATUS   ROLES    AGE     VERSION
kube-master   Ready    master   3m37s   v1.12.1
kube-node-1   Ready    <none>   2m41s   v1.12.1
kube-node-2   Ready    <none>   2m41s   v1.12.1
```

Note: To clean up after the tutorial, you can run `./dind-cluster-v1.12.sh clean`

## Step 2 - Initializing Nomad Master
Nomad master is the pipeline submission service that handles scheduling and orchestration. To launch it, first run `init.sh`
```bash
chmod +x init.sh startup.sh

# init.sh initializes the nomad master namespace in Kubernetes. This needs to be run everytime a new kuberenetes cluster is used.
./init.sh

# startup.sh launches the nomad master deployment on the cluster
./startup.sh
```

The nomad master deployment should now be starting up. To check it's status, run `kubectl get all`. Make sure the pod status is Running before proceeding to the next step:
```bash
romilb@romilx1:/$ kubectl get all
NAME                                         READY   STATUS              RESTARTS   AGE
pod/nomadmaster-deployment-988dbdb4f-vkqjq   1/1     Running   0          55s

NAME                          TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                           AGE
service/nomadmaster-service   NodePort   10.102.255.167   <none>        31000:31000/TCP,30000:30000/TCP   55s

NAME                                     DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/nomadmaster-deployment   1         1         1            0           55s

NAME                                               DESIRED   CURRENT   READY   AGE
replicaset.apps/nomadmaster-deployment-988dbdb4f   1         1         0       55s
```

To check the detailed status of the pod, you can run `kubectl describe pod <pod name>`.

To access the nomad master from localhost, we would need to setup port-forwarding from the local machine to the nomad service inside the virtual kubernetes cluster. To do this, open a new shell and run:
```bash
kubectl port-forward svc/nomadmaster-service 30000:30000
```
This binds port 30000 on localhost to port 30000 on the nomad master service. Verify that you can connect to the nomad master by running:
```bash
curl 127.0.0.1:30000
# This should return a HTTP message with the NOT_IMPLEMENTED flag
```
## Step 3 - Installing the client libraries

To interface with the master service, nomad provides a client library that exposes a pipeline submission interface. Install it by invoking setup.py at the repo root:
```bash
python setup.py install
```

Check if the installation succeeded with:
```bash
python -c "import nomad;print(nomad.__version__)"
# Output: 0.1a
```


## Step 4 - Define a pipeline and submit it
We now define a pipeline which generates a number, squares it and writes it to a file. This can be considered analogous to a IoT application, where data is read from a sensor, transformed by some function, and then written to a database. Launch a python terminal and run:
```python
import nomad

# Write pipeline steps as independent python methods
def source():
    import random
    return random.randint(0,10)

def square(x):
    return x*x

def write_to_file(x):
    # Analogous to writing to a database - this can be a remote call
    with open("/tmp/output.txt", 'a') as f:
        f.write(str(x) + "\n")

# Declare the sequence of operators in a list
operators = [source, square, write_to_file]

# Specify the performance profile of the operators in the same order as operators if you do not want automatic profiling.
# cloud_execution_time is proxy for the compute requirements of the operator, defined as the time taken in seconds to run the operator on the most powerful machine in the cluster.
# output_msg_size is the size of the value returned by the method in bytes.
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

# Specify the devices where the first operator and last operators are to be placed.
# Nodes can be listed by running kubectl get nodes
start_node = "kube-node-1"
end_node = "kube-master"

#Specify a pipline name here:
pipeline_id = # For instance, "demo"
 
# Submit the pipeline to the nomad master.
# This will make latency and compute aware placement decisions and instantiate the pipeline.

nomad.submit_pipeline(operators, start_node, end_node, pipeline_id, master_ip = "http://127.0.0.1:30000", profile=profiling)
```

This should launch the pipeline. You can verify it's functioning by inspecting the result of the final operator, `write_to_file`. This can be done by inspecting the file written by the operator:

```bash
kubectl get pods
kubectl exec -it <name of the final pod> /bin/bash
tail -f /tmp/output.txt
```

## Conclusion