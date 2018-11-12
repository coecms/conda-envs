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

import os, sys
from pkgutil import walk_packages, iter_modules
import warnings
import pytest
import subprocess

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
    try:
        raise
    except Warning as e:
        print("Warning loading %s"%name, file=sys.stderr)
    except Exception as e:
        print("Error loading %s"%name, file=sys.stderr)
        if name in exceptions:
            print("{} listed in exceptions, ignoring import error".format(name))
            exceptions.remove(name)
            pass
        else:
            raise

def test_walk_top_level_packages():
    for p in pkgutil.iter_modules():
        if p.ispkg:
            print(p.name)
            importlib.import_module(p.name)

def test_walk_packages():
    import pysal
    import tables
    import skimage.data
    import sklearn
    import sklearn.covariance
    import sklearn.manifold
    global exceptions
    exceptions = import_exceptions()
    for importer, name, ispkg in walk_packages(onerror=handle_error):
        # print("Importing {}".format(name))
        pass

    if len(exceptions) > 0:
        warnstring = "Untripped exceptions should be removed: {}".format(exceptions)
        warnings.warn(UserWarning(warnstring))

def test_import():
    for info in iter_modules():
        if info.ispkg:
            try:
                __import__(info.name)
            except Warning:
                print("Warning loading %s"%info.name, file=sys.stderr)
                pass
            except:
                print("Error loading %s"%info.name, file=sys.stderr)
                raise

def test_cdo():
   assert subprocess.call(['cdo','--version']) == 0


def test_mpi():
    with pytest.raises(ImportError, message="MPI in the Conda environment is a bad idea"):
        import mpi4py

if __name__ == '__main__':
    test_walk_packages()
