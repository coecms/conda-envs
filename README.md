# Adding packages

New conda packages are added to `environment.yml`

Sometimes it is necessary to pin a package to a specific version to avoid conflicts and errors. If the package is only being added to environment.yml to pin it's version, please add it after the comment to that effect, so it can be removed when pinning is no longer required.

# Resolving errors

The testing framework will try and import every module in the conda environment.

In some cases modules will not import cleanly and throw an error when the tests are run. To manage these errors packages can be added to `testconfig.yml`. There are three sections in `testconfig.yml`: `skip`, `exception`, and `preload`.

Any module import that errors but does not cleanly throw an exception should be added to `skip`. Any module listed in `skip` is never imported. It may be legitimate to `skip` a module import if that module will not behave correctly in a testing environment, e.g. it needs a valid X11 display. This must be tested manually. Add the module to `skip`, and once the environment has been updated `module load` it and test it appropriately.

Other candidates for adding to `skip` are tests that are not necessary (arguably tests should not be run simply by importing the package in which they are contained). For example the plotly package has a huge number of modules under `plotly.validators` that are currently skipped. 

Note that the python code that checks the `skip` condition use an `in` test, which will match quite promiscuiously. Take care.

Any module that throws a clean exception may be added to `exception`, which will allow this import to fail. Often it may come from a module that is not routinely used, or has been incorrectly imported, but will cause no, or minimal, disruption to the every day use of the package.

In some cases, due to the order in which modules are imported, the error only occurs in the test framework but not in everyday use. In this case add the module to `preload`. If that doesn't fix the error it may be necessary to change the order of the modules in `preload`. If the module still errors, add that module to `skip` if deemed appropriate.


# Updating releases

When updating to a new unstable release environment use the following protocol

1. Remove all version pins
2. Delete all packages below the comment line `Can be removed when pinning no longer required`
3. Check [build is successful](https://accessdev.nci.org.au/jenkins/blue/organizations/jenkins/conda%2Fanalysis3-unstable/activity/)
4. Add back version pins where required. Pin to latest available version as unstable aims to be an updated environment. Packages dependencies which are added simply to pin their version should be added below the comment to that effect.

