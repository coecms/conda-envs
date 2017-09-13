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
import os, sys
from importlib import import_module
from pkgutil import iter_modules

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

def walk_packages_depth(path=None, prefix='', onerror=None, depth=0):
    """Yields ModuleInfo for all modules recursively
    on path, or, if path is None, all accessible modules.
    'path' should be either None or a list of paths to look for
    modules in.
    'prefix' is a string to output on the front of every module name
    on output.
    Note that this function must import all *packages* (NOT all
    modules!) on the given path, in order to access the __path__
    attribute to find submodules.
    'onerror' is a function which gets called with one argument (the
    name of the package which was being imported) if any exception
    occurs while trying to import a package.  If no onerror function is
    supplied, ImportErrors are caught and ignored, while all other
    exceptions are propagated, terminating the search.
    Examples:
    # list all modules python can access
    walk_packages()
    # list all submodules of ctypes
    walk_packages(ctypes.__path__, ctypes.__name__+'.')
    """

    def seen(p, m={}):
        if p in m:
            return True
        m[p] = True

    for importer, name, ispkg in iter_modules(path, prefix):
        yield importer, name, ispkg

        if ispkg:
            # Check depth
            if name.count('.') > depth:
                # print(name,name.count('.'),depth)
                continue
            try:
                print('import ',name,end=' ')
                __import__(name)
            except ImportError:
                if onerror is not None:
                    onerror(name)
            except Exception:
                if onerror is not None:
                    onerror(name)
                else:
                    raise
            else:
                print('... ok')
                path = getattr(sys.modules[name], '__path__', None) or []

                # don't traverse path items we've seen before
                path = [p for p in path if not seen(p)]

                for item in walk_packages_depth(path, name+'.', onerror,depth):
                    yield item

def test_walk_packages_depth(depth=3):
    global exceptions
    exceptions = import_exceptions()
    for p in walk_packages_depth(depth=depth,onerror=handle_error):
        pass

def test_python_version():
    import sys
    assert sys.version_info >= (2,7)
    assert sys.version_info <= (3,0)

