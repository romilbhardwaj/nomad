kubectl delete --all pods,jobs,services,deployments,secrets,daemonset --namespace=nomad --now
kubectl config set-context $(kubectl config current-context) --namespace=default