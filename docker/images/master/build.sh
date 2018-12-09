docker build -t romilb/nomad_master:latest -f docker/images/master/Dockerfile .
docker tag romilb/nomad_master:latest romilb/nomad_master:latest
docker push romilb/nomad_master:latest