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

ENVIRONMENT=analysis3
VERSION=18.01

FULLENV="${ENVIRONMENT}-${VERSION}"

source g/data3/hh5/public/apps/miniconda3/etc/profile.d/conda.sh

unset CONDA_ENVS_PATH
unset CONDA_PKGS_DIRS

conda info

conda env create -n "${FULLENV}" -f environment.yml

conda activate "${FULLENV}"
py.test

conda env export > deployed.yml

ln -s /g/data3/hh5/public/modules/conda/{.common,"${FULLENV}"}
