#!/bin/bash
#  Copyright 2016 ARC Centre of Excellence for Climate Systems Science
#
#  \author  Scott Wales <scott.wales@unimelb.edu.au>
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

set -eux

for env in *.yml; do

    name=${env%%.yml}

    md5=$(curl -s https://api.anaconda.org/dist/$ANACONDA_USER/$name/latest/$env | sed -n 's/.*"md5":\s*"\([^"]\+\)".*/\1  '$env'/p')

    # If md5 sum has changed upload the environment
    if ! md5sum -c <<< $md5
    then
        anaconda --token $ANACONDA_TOKEN upload -u $ANACONDA_USER $env
    fi

done
