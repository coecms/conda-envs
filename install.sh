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

export CONDA_INSTALLATION_PATH=${CONDA_INSTALLATION_PATH:-/g/data/hh5/public/apps/miniconda3}
export CONDA_MODULE_PATH=${CONDA_MODULE_PATH:-/g/data/hh5/public/modules}

module purge

source version

FULLENV="${ENVIRONMENT}-${VERSION}"
export PYTHONNOUSERSITE=true

source "${CONDA_INSTALLATION_PATH}"/etc/profile.d/conda.sh

MAMBA=/g/data3/hh5/public/apps/miniconda3/envs/analysis3/bin/mamba

unset CONDA_ENVS_PATH
unset CONDA_PKGS_DIRS

conda info

# Check this is not a 'stable' enviornment
if grep "${FULLENV}\>.*\<${ENVIRONMENT}\>\(\s\|$\)" "${CONDA_MODULE_PATH}"/conda/.modulerc > /dev/null; then
    echo "${FULLENV} is a 'stable' environment, aborting" 1>&2
    exit 1
fi

function env_install {
    ${MAMBA} env create -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" -f environment.yml
    ln -s "${CONDA_MODULE_PATH}"/conda/{.common.v2,"${FULLENV}"}
    
    conda activate "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}"
    py.test -s
}

function env_update {
    conda env export -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" > deployed.old.yml

    # Clear the history - see https://github.com/conda/conda/issues/7279
    cat "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history >> "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history.log
    echo > "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history

    ${MAMBA} env update -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" -f environment.yml
    set +u
    conda activate "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}"
    set -u
    if ! py.test -s; then
        echo "${FULLENV} tests failed, rolling back update" 1>&2
        ${MAMBA} env update -f deployed.old.yml
        exit -1
    fi
}

if [ ! -d "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" ]; then
    env_install
else
    env_update
fi

# Refresh jupyter plugins
jupyter lab build

conda env export > deployed.yml

