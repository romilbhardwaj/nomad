#!/usr/bin/env bash

./dind-cluster-v1.12.sh clean
docker rm --force $(docker ps -aq)
docker rmi $(docker images --format '{{.Repository}}:{{.Tag}}' | grep 'lab11*')