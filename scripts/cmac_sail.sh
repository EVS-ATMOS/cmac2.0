#!/bin/bash

srun --time=36:00:00 -A atm124 -N 1 python cmac_sail.py $1
