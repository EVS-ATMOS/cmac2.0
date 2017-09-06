#!/bin/bash
echo "number of nodes"
export PBS_NUM_NODES=`wc -l ${PBS_NODEFILE} | cut -f1 -d" "`
echo $PBS_NUM_NODES
echo "===================="
echo "ssh into each node"


#====================================================================
scheduler_node=$1
hostIndex=0
echo "Pulling from schedule node:"
echo $scheduler_node
echo $localscratch
export PATH=/home/rjackson/anaconda3/bin:$PATH
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8
export TMPDIR=$2
export MPLBACKEND="agg"
source activate cmac_env
dask-worker --nprocs 1 --nthreads 16 --scheduler-file=$1 --local-directory=$2 --no-nanny

