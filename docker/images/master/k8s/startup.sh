#!/usr/bin/env bash
scriptdir="$(dirname "$0")"
clusterConfig="deployment_nomadmaster.yaml"
cd "$scriptdir"
kubectl create -f service_nomadmaster.yaml
while getopts ":t" opt; do
  case $opt in
    t)
      echo "Using nomad master:test image" >&2
      clusterConfig="deployment_nomadmaster_test.yaml"
      echo $clusterConfig
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done
kubectl create -f $clusterConfig
kubectl config set-context $(kubectl config current-context) --namespace=nomad