#!/bin/bash 

if [ "$1" != "" ]; then
    cd ..\.. && docker build -t romilb/nomad_master:$1 -f images/master/Dockerfile .
else
    echo "Please supply version tag as argument"
fi

if [ "$2" != "" ]; then
	echo "Tagging and pushing"
	docker tag romilb/nomad_master:$1 romilb/nomad_master:$2
	docker push romilb/nomad_master:$2
fi