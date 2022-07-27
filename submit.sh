#!/bin/bash

function submit() {
    for FILE in *; do
        if [[ "$FILE" == *".sbatch"* ]]
        then
            sbatch $FILE
        fi
    done
}

