docker build -t romilb/nomad_client:latest -f docker/images/client/Dockerfile .
docker tag romilb/nomad_client:latest romilb/nomad_client:latest
docker push romilb/nomad_client:latest