#!/bin/bash

source ./submit.sh
cd ./src/

# this is specifically for bluehive
# module load python3/3.10.5b

# exception catching for bluehive
{
    python3 ./sim_setup.py
} || {
    python3.10 ./sim_setup.py 
}
