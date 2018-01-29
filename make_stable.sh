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

source /g/data3/hh5/public/apps/miniconda3/etc/profile.d/conda.sh

# Mark this version stable
sed -e "s/${ENVIRONMENT}-\S\+ \<\(${ENVIRONMENT}\>\)/${FULLENV} \1/" \
    -i /g/data3/hh5/public/modules/conda/.modulerc

# Next version - add 1 to the year if we're currently in the last quarter
NEXT=$(date +"%y %m" | awk '{printf("%02d%02d", $1+int($2/10), (int(($2-1)/3+1)%4*3+1))}')

if [ "${VERSION}" = "${NEXT}" ]; then
    echo "ERROR: New version ${NEXT} is the same value as the last one" 2>&1
    echo "Please confirm manually" 2>&1
    exit 1
fi

echo "Next unstable version will be ${ENVIRONMENT}-${NEXT}"

# Update 'version' with the new value
sed -e "s/\(VERSION=\).*/\1${NEXT}/" version

conda env export -n "${FULLENV}" > deployed.yml

git add version deployed.yml
git commit -m "Deployed ${FULLENV} as stable"
git tag -a ${FULLENV} -m "Deployed ${FULLENV} as stable"

git push origin ${ENVIRONMENT} ${FULLENV}
