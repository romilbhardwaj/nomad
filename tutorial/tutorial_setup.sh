#!/usr/bin/env bash

# Install md5sha1sum on OSX
if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install md5sha1sum
fi

# Run the DIND script
../docker/images/master/k8s/dind-cluster-v1.12.sh up

# Add kubectl binaries to PATH
export PATH="$HOME/.kubeadm-dind-cluster:$PATH"
# echo "export PATH=\"$HOME/.kubeadm-dind-cluster:$PATH\"" >> ~/.bashrc

# init.sh initializes the nomad master namespace in Kubernetes. This needs to be run everytime a new kuberenetes cluster is used.
../docker/images/master/k8s/init.sh

# startup.sh launches the nomad master deployment on the cluster
../docker/images/master/k8s/startup.sh

#Wait for master container to start running.
while !(kubectl get pod -l "app=nomadmaster" | grep "Running");
do
    echo "Waiting for Nomad master to start running..."
    sleep 2
done

#Get shell at running container and launch python.
kubectl exec -it $(kubectl get pod -l "app=nomadmaster" -o jsonpath='{.items[0].metadata.name}') -- bash -c "python"