#!/bin/bash
source activate cmac_env
export PATH=/home/rjackson/anaconda3/bin:$PATH
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export TMPDIR=$2
export MPLBACKEND="agg"
dask-scheduler --port=8786 --scheduler-file=$1 --local-directory=$2
