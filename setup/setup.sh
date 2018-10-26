# Shell script to update/create the nomad conda environment.
# $ source setup/setup.sh 
# Run this scrip every time you pull from github as dependancies may change.
conda env update --name nomad --file setup/environment.yml
source activate nomad 