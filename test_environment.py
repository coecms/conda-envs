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

def check_packages(dirs=None,depth=1):
    """
    For each installed package rummage through python cache directories looking for 
    modules to try and load, in order to check the integrity of the conda installation

    Keyword arguments:
    dirs  -- array of conda package cache directories to search 
    depth -- integer determing the depth of module import namespace. Default 
             only imports top level
    """

    if dirs is None:
        pkgcachedirs = package_dirs()
    else:
        pkgcachedirs = dirs

    print("Searching these package cache directories: {}".format(pkgcachedirs))

    for package in package_list():

        print("Package: {}".format(package["dist_name"]))

        # Look for the "files" file in the package cache directories. This, perhaps
        # unsurprisingly, lists all the files in the package
        files = None
        for directory in pkgcachedirs:
            tmp = os.path.join(directory, package["dist_name"], 'info','files')
            if os.path.exists(tmp):
                files = tmp
                break

        if files is None:
            print("no files file found for package: {}\n".format(package))
        else:

            exceptions = import_exceptions()
            mods = find_imports(files, depth=depth)

            if not mods:
                warnstring ="No imports founds for {}, no testing possible".format(package["dist_name"])
                warnings.warn(UserWarning(warnstring))

            for modname in mods:
                if modname in exceptions:
                    print("{} listed in exceptions, skipping".format(modname))
                else:
                    print("Importing {} ".format(modname),end='')
                    if importmodule(modname):
                        print("... ok")

def find_imports(files, depth):
    """
    Find importable modules from the files listing in a conda package
    """

    mods = set() 

    # Read in all the file paths, find directories containing an __init__.py
    # transform the directory path into a module name and attempt to import it
    with open(files, 'r') as infile:
        for name in infile:
            name = name.rstrip("\n")
            if name.endswith('__init__.py'):
                modname = extract_module(os.path.dirname(name),depth)
                if modname is not None: mods.add(modname)
            elif name.endswith('top_level.txt'):
                with open(os.path.join(os.path.dirname(os.path.dirname(files)),name), 'r') as toplevel:
                    for modname in toplevel:
                        modname = extract_module(modname.rstrip("\n"),depth)
                        if modname is not None: mods.add(modname)
                    
    return mods

def importmodule(modname,fail=True):
    """
    Try to import a python module. By default will raise an exception if import fails
    """

    imported_ok = False
    try:
        import_module(modname, package=None)
    except Exception as e:
        warnstring = "Failed to import {} : Reported error: {}".format(modname,str(e))
        warnings.warn(UserWarning(warnstring))
        if fail: raise
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

def extract_module(path,depth=1):
    """ 
    From a typical python package install path extract out the 
    importable name
    """
    names = []
    for element in nextdir(path):
        if element == 'site-packages' or element.endswith('.egg'): break
        names.append(element)
    if len(names) <= depth:
        return ".".join(reversed(names))
    else:
        return None
            
def test_check_packages():
    check_packages(depth=2)

def test_python_version():
    import sys
    assert sys.version_info > (3,0)
