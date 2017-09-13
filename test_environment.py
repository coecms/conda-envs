#!/usr/bin/env python
# Copyright 2017 ARC Centre of Excellence for Climate Systems Science
# author: Scott Wales <scott.wales@unimelb.edu.au>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function

# Nicked this code from https://github.com/conda/conda-api
# Didn't want the tests to rely on any external packages, so included
# stripped down version of the code rather than use the package as-is 

import os, sys
from pkgutil import walk_packages

exceptions = set()

def import_exceptions():
    """
    Return a set of python modules that are exempt in check_packages
    """
    exceptionsfile = 'exceptions'
    mods = set()

    if os.path.exists(exceptionsfile):
        with open(exceptionsfile, 'r') as f:
            for line in f:
                mods.add(line.rstrip("\n"))

    return mods

def handle_error(name):
    global exceptions
    if name in exceptions:
        print("{} listed in exceptions, ignoring import error".format(name))
        pass
    else:
        print("ERROR>>>>",name)
        raise

def test_walk_packages():
    global exceptions
    exceptions = import_exceptions()
    for p in walk_packages(onerror=handle_error):
        print("Importing {}".format(p.name))

def test_python_version():
    import sys
    assert sys.version_info > (3,0)
