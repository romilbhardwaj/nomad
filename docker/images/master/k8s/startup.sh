#!/usr/bin/env bash
scriptdir="$(dirname "$0")"
cd "$scriptdir"
kubectl create -f service_nomadmaster.yaml
kubectl create -f deployment_nomadmaster.yaml
kubectl config set-context $(kubectl config current-context) --namespace=nomad