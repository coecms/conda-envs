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

ROOT_DIR=/g/data/hh5/public

CONDA_DIR=${ROOT_DIR}/apps/miniconda3

MOD_DIR=${ROOT_DIR}/modules/conda

source ${CONDA_DIR}/etc/profile.d/conda.sh

MAMBA=${CONDA_DIR}/envs/analysis3/bin/mamba

# Next version should be the year and the current month (1, 4, 7 or 10)
NEXT=$(date +"%y %m" | awk '{printf("%02d.%02d", $1, $2)}')

if [ "${VERSION}" = "${NEXT}" ]; then
    echo "ERROR: New version ${NEXT} is the same value as the last one" 2>&1
    echo "Please confirm manually" 2>&1
    exit 1
fi

UNSTABLE="${ENVIRONMENT}-${NEXT}"
echo "Next unstable version will be ${UNSTABLE}"

# Update 'version' with the new value
sed -e "s/\(VERSION=\).*/\1${NEXT}/" -i version

# Create new unstable environment
${MAMBA} env create -p "${CONDA_DIR}/envs/${UNSTABLE}" -f environment.yml
ln -s ${MOD_DIR}/{.common.v2,"${UNSTABLE}"}

# Make new unstable environment
sed -E -e "s#${VERSION}#${NEXT}#" -i ${MOD_DIR}/.modulerc

# Make current version default
sed -E -e "s#conda/${ENVIRONMENT}-\S+ (.*) default#conda/${ENVIRONMENT}-${VERSION} \1 default#" \
    -i ${MOD_DIR}/.modulerc

conda env export -n "${FULLENV}" > deployed.yml

git add version deployed.yml
git commit -m "Deployed ${FULLENV} as stable"
git tag -a ${FULLENV} -m "Deployed ${FULLENV} as stable"

git push origin ${ENVIRONMENT} ${FULLENV}
