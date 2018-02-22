#!/bin/bash
export PATH=/home/rjackson/anaconda3/envs/cmac_env/bin:$PATH
source activate cmac_env
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export TMPDIR=$2
export MPLBACKEND="agg"
dask-scheduler --port=8786 --scheduler-file=$1 --local-directory=$2 
