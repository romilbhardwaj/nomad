#!/usr/bin/env bash

../docker/images/master/k8s/dind-cluster-v1.12.sh clean
docker rm --force $(docker ps -aq)
docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'lab11*')