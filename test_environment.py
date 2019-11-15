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
import yaml

debug = False

def my_walk_packages(path=None, prefix='', onerror=None, skip=None):
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

    for info in iter_modules(path, prefix):
        yield info

        if info.name not in skip:
            if info.ispkg and info.name:
                if debug: print("Importing {}".format(info.name))
                try:
                    __import__(info.name)
                except ImportError:
                    if onerror is not None:
                        onerror(info.name)
                except Exception:
                    if onerror is not None:
                        onerror(info.name)
                    else:
                        raise
                else:
                    path = getattr(sys.modules[info.name], '__path__', None) or []

                    # don't traverse path items we've seen before
                    path = [p for p in path if not seen(p)]

                    yield from my_walk_packages(path, info.name+'.', onerror, skip)
        else:
            print("Skipping {}".format(info.name))


def import_config(filename):
    """
    Return a configuration dictionary
    """
    try:
        with open(filename, 'r') as config_file:
            config = yaml.load(config_file)
    except IOError as exc:
        if exc.errno == errno.ENOENT:
            print('Warning: config file {0} not found!'
                  .format(config_fname))
            config = {}
        else:
            raise

    return config

def handle_error(name):
    global exception
    try:
        raise
    except Warning as e:
        print("Warning loading {}".format(name), file=sys.stderr)
    except Exception as e:
        print("Error loading {}".format(name), file=sys.stderr)
        if name in exception:
            print("{} listed as exception, ignoring import error".format(name))
            exception.remove(name)
            pass
        else:
            raise

def test_walk_packages():
    global exception
    config = import_config('testconfig.yml')
    for mod in config.get('preload',[]):
        try:
            if debug: print("Preloading {}".format(mod))
            __import__(mod)
        except:
            print("Error preloading {}".format(mod))

    exception = set(config.get('exception',None))
    skip = set(config.get('skip',None))
    if debug: print('Exception: {}'.format(exception))
    if debug: print('Skip: {}'.format(skip))
    for importer, name, ispkg in my_walk_packages(onerror=handle_error,skip=skip):
        pass

    if len(exception) > 0:
        warnstring = "Untripped exceptions should be removed: {}".format(exception)
        warnings.warn(UserWarning(warnstring))

def test_import():
    for info in iter_modules():
        if info.ispkg:
            try:
                __import__(info.name)
            except Warning:
                print("Warning loading {}".format(info.name), file=sys.stderr)
                pass
            except:
                print("Error loading {}".format(info.name), file=sys.stderr)
                raise

def test_cdo():
   assert subprocess.call(['cdo','--version']) == 0


def test_mpi():
    with pytest.raises(ImportError):
        import mpi4py
        pytest.fail("MPI in the Conda environment is a bad idea")

if __name__ == '__main__':
    test_walk_packages()
