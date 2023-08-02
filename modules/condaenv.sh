#!/bin/bash
# Prints the environment variables set by 'conda activate $1', for processing by the modules
export PATH=/usr/bin:/bin
source /g/data/hh5/public/apps/miniconda3/etc/profile.d/conda.sh
conda activate $1
/bin/env
