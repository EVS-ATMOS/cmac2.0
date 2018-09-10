#!/bin/bash
# Based on install.sh from arm-pyart.
# https://github.com/ARM-DOE/pyart/blob/master/continuous_integration/install.sh

# Install Miniconda
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -O miniconda.sh
chmod +x miniconda.sh
./miniconda.sh -b
export PATH=/home/travis/miniconda3/bin:$PATH
conda config --set always_yes yes
conda config --set show_channel_urls true
conda update -q conda

## Create a testenv with the correct Python version
conda env create -f continuous_integration/environment-$PYTHON_VERSION.yml
source activate test_env

pip install git+https://github.com/jjhelmus/CyLP.git@py3
pip install -e .
