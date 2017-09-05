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

import warnings
import os
import json
import subprocess
from subprocess import Popen, PIPE
from importlib import import_module

def _call_conda(extra_args):
    # call conda with the list of extra arguments, and return the tuple
    # stdout, stderr
    cmd_list = ['conda']

    cmd_list.extend(extra_args)

    try:
        p = Popen(cmd_list, stdout=PIPE, stderr=PIPE)
    except OSError:
        raise Exception("could not invoke %r\n" % args)
    return p.communicate()

def _call_and_parse(extra_args):
    stdout, stderr = _call_conda(extra_args)
    if stderr.decode().strip():
        raise Exception('conda %r:\nSTDERR:\n%s\nEND' % (extra_args,
                                                         stderr.decode()))
    return json.loads(stdout.decode())

def package_dirs():
    """
    Return a list of the package directories
    """
    info = _call_and_parse(['info', '--json'])
    return(info['pkgs_dirs'])

def package_list():
    """
    Return a dictionary with list of installed packages
    """
    return _call_and_parse(['list', '--json'])

def find_file(paths, filename):

    filepath = None
    for path in paths:

        if not os.path.isdir(path): continue
            
        print(path)

        try:
            output = subprocess.check_output(['find',path,'-name',filename])
            filepath = output.decode('ascii').rstrip("\n")
        except Exception as e:
            print("path: {} filename: {}\n".format(path,filename))
            print(str(e))
            continue

    return filepath
            
def check_packages(exhaustive=True):
    """
    For each installed package rummage through python cache directories looking for 
    modules to try and load, in order to check the integrity of the conda installation
    """

    pkgcachedirs = package_dirs()

    pkgcachedirs.insert(0, "/short/w35/saw562/conda/pkgs")
        
    print(pkgcachedirs)

    for package in package_list():

        if not exhaustive:
            
            toplevel = find_file([ os.path.join(d, package["dist_name"]) for d in pkgcachedirs], 'top_level.txt')
            
            if toplevel is None:
                print("cachedir not found for package: {}\n".format(package))
            if len(toplevel) == 0:
                print("no toplevel.txt file found in cachedir")
            else:
                with open(toplevel, 'r') as infile:
                    for name in infile:
                        name = name.rstrip("\n")
                        try:
                            import_module(name, package=None)
                            # except ModuleNotFoundError :
                            #     print("Module not found, ignoring {}".format(package['name']))
                        except Exception as e:
                            print(str(e))
                        else:
                            print("Imported {} successfully".format(name))
                            # Skip to next package unless specify exhaustive testing
                            # if not exhaustive: continue

        else:

            # Look for the "files" file which, perhaps unsurprisingly, lists all the
            # files in the package
            files = None
            for directory in pkgcachedirs:
                tmp = os.path.join(directory, package["dist_name"], 'info','files')
                if os.path.exists(tmp):
                    files = tmp
                    break

            if files is None:
                print("no files file found for package: {}\n".format(package))
            else:
                with open(files, 'r') as infile:
                    for name in infile:
                        name = name.rstrip("\n")
                        if name.endswith('__init__.py'):
                            name = os.path.dirname(name)
                            names = []
                            for element in nextdir(name):
                                if element == 'site-packages': break
                                names.append(element)
                            modname = ".".join(reversed(names))
                            if importmodule(modname):
                                print("Imported {} successfully".format(modname))
                            

def importmodule(modname):

    imported_ok = False
    try:
        import_module(modname, package=None)
    except Exception as e:
        warnstring = "Failed to import {} : Reported error: {}".format(modname,str(e))
        warnings.warn(UserWarning(warnstring))
    else:
        imported_ok = True

    return imported_ok

def nextdir(path):
    """
    Sequentially return elements from a path
    """
    while True:
        path, base = os.path.split(path)
        if base == '': break
        yield base

def extract_module(path):
    """ 
    From a typical python package install path extract out the 
    importable name
    """
    pass
            
def test_package_list():
    print("Hello\n")
    print(package_list())

def test_python_version():
    import sys
    assert sys.version_info > (3,0)

def test_numpy_import():
    import numpy

def test_scipy_import():
    import scipy

def test_pandas_import():
    import pandas

def test_xarray_import():
    import xarray

def test_dask_import():
    import dask
    import dask.bag
