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
###########################################################################
###
### The new and improved all-purpose do everything conda env script
### 
### To be run by Jenkins
### 

set -eu

export CONDA_INSTALLATION_PATH=${CONDA_INSTALLATION_PATH:-/g/data/hh5/public/apps/miniconda3}
export CONDA_MODULE_PATH=${CONDA_MODULE_PATH:-/g/data/hh5/public/modules}

module purge

function get_aliased_module () {
    alias_name="${1}"
    while read al arrow mod; do 
        if [[ "${al}" == "${alias_name}" ]]; then
            echo "${mod}"
            return
        fi
    done < <( MODULEPATH="${CONDA_MODULE_PATH}" module aliases 2>&1 )
    echo ""
    return
}

function write_modulerc() {
    stable="${1}"
    unstable="${2}"
    env_name="${3}"

    cat<<EOF > "${CONDA_MODULE_PATH}/conda/.modulerc"
#%Module1.0

module-version conda/${stable} analysis ${env_name} default
module-version conda/${unstable} ${env_name}-unstable

module-version conda/analysis27-18.10 analysis27
EOF
}

function symlink_atomic_update() {
    link_name="${1}"
    link_target="${2}"

    tmp_link_name=$( mktemp -u -p ${link_name%/*} .tmp.XXXXXXXX )

    ln -s "${link_target}" "${tmp_link_name}"
    mv -T "${tmp_link_name}" "${link_name}"

}

source version

FULLENV="${ENVIRONMENT}-${VERSION_TO_MODIFY}"
export PYTHONNOUSERSITE=true

source "${CONDA_INSTALLATION_PATH}"/etc/profile.d/conda.sh

MAMBA=/g/data3/hh5/public/apps/miniconda3/envs/analysis3/bin/mamba

unset CONDA_ENVS_PATH
unset CONDA_PKGS_DIRS

conda info

# Check this is not a 'stable' enviornment
if [[ $( get_aliased_module conda/analysis ) == "conda/${FULLENV}" ]]; then
    echo "${FULLENV} is a 'stable' environment, aborting" 1>&2
    exit 1
fi

function env_install {
    ${MAMBA} env create -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" -f environment.yml
    ln -s "${CONDA_MODULE_PATH}"/conda/{.common.v2,"${FULLENV}"}
    set +u
    conda activate "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}"
    set -u

    conda env export > deployed.yml

    py.test -s
    # Refresh jupyter plugins
    jupyter lab build
}

function env_update {
    conda env export -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" > deployed.old.yml

    # Clear the history - see https://github.com/conda/conda/issues/7279
    cat "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history >> "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history.log
    echo > "${CONDA_INSTALLATION_PATH}"/envs/${FULLENV}/conda-meta/history

    ${MAMBA} env update -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" -f environment.yml

    conda env export -p "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" > deployed.yml
    if diff -q deployed.yml deployed.old.yml; then
        echo "No changes detected in the environment, skipping tests"
        return
    fi

    set +u
    conda activate "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}"
    set -u

    if ! py.test -s; then
        echo "${FULLENV} tests failed, rolling back update" 1>&2
        ${MAMBA} env update -f deployed.old.yml
        exit -1
    fi
    # Refresh jupyter plugins
    jupyter lab build
}

if [ ! -d "${CONDA_INSTALLATION_PATH}/envs/${FULLENV}" ]; then
    env_install
else
    env_update
fi

CURRENT_STABLE=$( get_aliased_module conda/analysis )
NEXT_STABLE="${ENVIRONMENT}-${STABLE_VERSION}"
CURRENT_UNSTABLE=$( get_aliased_module conda/analysis3-unstable )
NEXT_UNSTABLE="${ENVIRONMENT}-${UNSTABLE_VERSION}"

if ! [[ "${CURRENT_STABLE}" == "conda/${NEXT_STABLE}" ]]; then
    echo "Updating stable environment to ${NEXT_STABLE}"
    write_modulerc "${NEXT_STABLE}" "${NEXT_UNSTABLE}" "${ENVIRONMENT}"
    symlink_atomic_update "${CONDA_INSTALLATION_PATH}"/envs/"${ENVIRONMENT}" "${NEXT_STABLE}"
fi
if ! [[ "${CURRENT_UNSTABLE}" == "conda/${NEXT_UNSTABLE}" ]]; then
    echo "Updating unstable environment to ${NEXT_UNSTABLE}"
    write_modulerc "${NEXT_STABLE}" "${NEXT_UNSTABLE}" "${ENVIRONMENT}"
    symlink_atomic_update "${CONDA_INSTALLATION_PATH}"/envs/"${ENVIRONMENT}"-unstable "${NEXT_UNSTABLE}"
fi

