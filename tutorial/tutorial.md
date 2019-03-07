# Nomad Tutorial
This tutorial will introduce you to the Nomad programming model. We will start by setting up a virtual Kubernetes cluster locally on our machine and launching the nomad master on this cluster. We will then write a simple sequential pipeline in python and then instantiate it on the nomad cluster.

## Step 0 - Prerequisites
* [Docker 18.09 or above](https://docs.docker.com/install/)
* Nomad repository `git clone https://github.com/romilbhardwaj/nomad.git`

<!---## Step 1 - Launch the Tutorial Container
We will be running this tutorial inside a docker container which has nomad dependencies pre-installed. To launch the container, run:
```bash
chmod +x run_tutorial.sh
./run_tutorial.sh
```
This should pull the latest tutorial image and launch the container.


## Step 1 - Setting up the Virtual Cluster
Nomad uses Kubernetes to orchestrate and schedule pipelines. In deployment this cluster would span across machines on the edge and the cloud, but for this tutorial we'll be creating a virtual cluster locally on our machines. For this, we will be using [kubeadm-dind-cluster](https://github.com/kubernetes-sigs/kubeadm-dind-cluster), a utility which creates kubernetes nodes as local docker containers. To use this, simply run:
```bash
cd docker/images/master/k8s

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

## Step 3 - Get shell access to a terminal in the virtual cluster

For the purposes of this tutorial, we will use the python interpreter in the nomad master container. To gain shell access to the nomad master, run:
```bash
kubectl exec -it $(kubectl get pod -l "app=nomadmaster" -o jsonpath='{.items[0].metadata.name}') -- bash
```
-->

## Step 1 - Creating a virtual cluster
Nomad uses Kubernetes to orchestrate and schedule pipelines. In a real deployment, this cluster would span across machines on the edge and the cloud, but for this tutorial we'll be creating a virtual cluster locally on our machines. For this, we will be using [kubeadm-dind-cluster](https://github.com/kubernetes-sigs/kubeadm-dind-cluster), a utility which creates kubernetes nodes as local docker containers. For the purposes of this tutorial, we have simplified the setup process - just run
```bash
./tutorial_setup.sh
```

This will take care of setting up the cluster on your machine and launching Nomad on this virtual cluster. When the script completes, you should find yourself in a python shell.

## Step 2 - Define a pipeline and submit it
We will now define a pipeline which generates a number, squares it and writes it to a file. This can be considered analogous to a IoT application, where data is read from a sensor, transformed by some function, and then written to a database. Note that all following steps are run in the interactive shell created from the previous step, but they can also written to a file and executed separately. 

The first step is to import nomad.
```python
import nomad
```

We will now define the operators that compose the sample pipeline as independent methods. We have a `source` method which generates integers between 0 and 10, a `square` method that squares any input and a `write_to_file` method, that appends the input to a local file.
```python
def source():
    import random
    return random.randint(0,10)

def square(x):
    return x*x

def write_to_file(x):
    # Analogous to writing to a database - this can be a remote call
    with open("/tmp/output.txt", 'a') as f:
        f.write(str(x) + "\n")
    return x
```

Next, we need to define a logical ordering of these operators in the pipeline. We do so by specifying them in a python list:
```python
operators = [source, square, write_to_file] # source -> square -> write_to_file
```

Next, the nomad scheduler needs to know the computational and network costs of these operators so it can place them optimally on the infrastructure. This profiling will (soon) be automatic, or you could manually specify the performance profile of the operators.  This is specified as a list of dictionaries, with each dictionary containing two keys, `cloud_execution_time` and `output_msg_size`. `cloud_execution_time` is proxy for the compute requirements of the operator, defined as the time taken in seconds to run the operator on the most powerful machine in the cluster. `output_msg_size` is the size of the value returned by the method in bytes.

```python
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
```

For any distributed pipeline, we must also specify the start and the end nodes for the pipeline. This is important since the source operator, which may typically read a value from a sensor, is run on a specific edge device. 

```python
# Specify the devices where the first operator and last operators are to be placed.
# Nodes can alos be listed by running kubectl get nodes in your shell
start_node = "kube-node-1"
end_node = "kube-master"
```

Next, specify a unique name for your pipeline.
```python
#Specify a pipline name here:
pipeline_id = <Insert name here> # For instance, "mydemo"
``` 

The pipeline is now ready for submission. Submit it with the nomad client library.
```python
# Submit the pipeline to the nomad master.
# This will make latency and compute aware placement decisions and instantiate the pipeline.

conn_str = "http://127.0.0.1:30000"
ops = nomad.submit_pipeline(operators, start_node, end_node, pipeline_id, master_conn_str = conn_str, profile=profiling)
```

`nomad.submit_pipeline` is a blocking call and might take some time to complete. In this call, the nomad master builds new containers with our operators and then launches them on the cluster. It returns a list of GUIDs for the operators that have been launched. 

Once the above call returns, you can get the result from the square operator by calling `nomad.get_last_output(op_guid, conn_str)`.
```python
result = nomad.get_last_output(ops[1], master_conn_str = conn_str)
print(result)
```

<!--
```bash
kubectl get pods
kubectl exec -it <name of the final pod> /bin/bash
tail -f /tmp/output.txt
```
-->

## Conclusion
To cleanup, run `docker\images\master\k8s\tutorial_shutdown.sh`.