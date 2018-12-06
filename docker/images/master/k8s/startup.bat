kubectl create -f service_nomadmaster.yaml
kubectl create -f deployment_nomadmaster.yaml
kubectl config set-context docker-for-windows --namespace=nomad