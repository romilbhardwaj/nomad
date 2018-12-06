#!/bin/bash 

if [ "$1" != "" ]; then
    cd ..\..\..\.. && docker build -t nomad/nomad_dummy:$1 -f docker/images/samples/dummy/Dockerfile .
else
    echo "Please supply version tag as argument"
fi

if [ "$2" != "" ]; then
	echo "Tagging and pushing"
	docker tag nomad/nomad_dummy:$1 nomad/nomad_dummy:$2
	docker push nomad/nomad_dummy:$2
fi