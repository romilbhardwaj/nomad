FROM ubuntu:16.04

# Update apt and install wget
RUN  apt-get update \
  && apt-get install -y wget libopenmpi-dev wget nano bzip2 docker.io\
  && rm -rf /var/lib/apt/lists/*

# Expose docker socket volume
# VOLUME /var/run/docker.sock

#Install conda
RUN echo 'export PATH=/opt/conda/bin:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -O ~/miniconda.sh && \
    /bin/bash ~/miniconda.sh -b -p /opt/conda && \
    rm ~/miniconda.sh

ENV PATH /opt/conda/bin:$PATH
	
# Begin setting up python environment
WORKDIR /nomad
ADD nomad/setup/environment.yml /nomad

# update conda and setup environment
RUN conda update conda -y \
    && conda env create --force -f /nomad/environment.yml

# Change conda env
ENV PATH /opt/conda/envs/nomad/bin:$PATH

# Use tini as the entrypoint
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Create folder for logs:
RUN mkdir -p /nomad/logs/

# Expose the RPC Ports
EXPOSE 30000 31000 20000 10000


# Add nomad src
ADD nomad /nomad/nomad
ADD docker/images/ /nomad/images/

ENV PYTHONPATH /nomad/:$PYTHONPATH

# CMD ["/bin/bash"]
# Run the python script
CMD ["python", "/nomad/nomad/core/master/master_launcher.py"]