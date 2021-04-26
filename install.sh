#!/bin/bash
#  Copyright 2018 
#
#  \author   <scott.wales@unimelb.edu.au>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

set -eu

module purge

source version

FULLENV="${ENVIRONMENT}-${VERSION}"
export PYTHONNOUSERSITE=true

source /g/data/hh5/public/apps/miniconda3/etc/profile.d/conda.sh

MAMBA=/g/data/hh5/public/apps/miniconda3/envs/analysis3-21.04/bin/mamba

unset CONDA_ENVS_PATH
unset CONDA_PKGS_DIRS

conda info

# Check this is not a 'stable' enviornment
if grep "${FULLENV}\>.*\<${ENVIRONMENT}\>\(\s\|$\)" /g/data/hh5/public/modules/conda/.modulerc > /dev/null; then
    echo "${FULLENV} is a 'stable' environment, aborting" 1>&2
    exit 1
fi

function env_install {
    ${MAMBA} env create -p "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}" -f environment.yml
    ln -s /g/data/hh5/public/modules/conda/{.common.v2,"${FULLENV}"}
    
    conda activate "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}"
    py.test -s
}

function env_update {
    conda env export -p "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}" > deployed.old.yml

    # Clear the history - see https://github.com/conda/conda/issues/7279
    cat /g/data/hh5/public/apps/miniconda3/envs/${FULLENV}/conda-meta/history >> /g/data/hh5/public/apps/miniconda3/envs/${FULLENV}/conda-meta/history.log
    echo > /g/data/hh5/public/apps/miniconda3/envs/${FULLENV}/conda-meta/history

    ${MAMBA} env update -p "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}" -f environment.yml
    set +u
    conda activate "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}"
    set -u
    if ! py.test -s; then
        echo "${FULLENV} tests failed, rolling back update" 1>&2
        ${MAMBA} env update -f deployed.old.yml
        exit -1
    fi
}

if [ ! -d "/g/data/hh5/public/apps/miniconda3/envs/${FULLENV}" ]; then
    env_install
else
    env_update
fi

# Refresh jupyter plugins
jupyter lab build

conda env export > deployed.yml

