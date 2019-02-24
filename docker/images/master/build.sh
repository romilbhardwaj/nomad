docker build -t lab11nomad/master:latest -f docker/images/master/Dockerfile .
docker tag lab11nomad/master:latest lab11nomad/master:latest
docker push lab11nomad/master:latest