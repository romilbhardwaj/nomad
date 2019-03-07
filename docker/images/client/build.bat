docker build -t lab11nomad/client:latest -f docker/images/client/Dockerfile .
docker tag lab11nomad/client:latest lab11nomad/client:latest
docker push lab11nomad/client:latest