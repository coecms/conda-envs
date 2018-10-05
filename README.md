# Anaconda environments

Environment files are in this repository's branches

Install from anaconda.org

    conda env create accessdev/analysis

Load on Raijin

    module use ~access/modules
    module load conda/analysis

Install development version from file

    conda env create -f analysis.yml

## Updating the environment

We update the environments once a quarter, around when NCI does their quarterly maintenance

We maintain three versions of the analysis environments - 'unstable', 'stable' and 'old'. 'stable' and 'old' are frozen environments, they do not recieve updates to their libraries. 'unstable' is where updates and new packages are installed into.

During the update, the current 'unstable' branch becomes the new 'stable', the current 'stable' becomes the new 'old', and the current 'old' environment gets removed. An entirely new environment is created to be the new 'unstable', to make sure there are no bits of packages hanging around that should have been cleaned up.

The environments are named like YY.MM, e.g. the Q4 2018 install is named 18.10 (like ubuntu versions). There is an alias in the module files to the 'unstable' etc. names.

### Installing a new version

1. Update the version number in this repository (in the file `version` of the branch you want to update). This will trigger a Jenkins build to install the new unstable environment (done automatically by the `install.sh` script)

2. Wait for Jenkins to install the new environment (see progress at https://accessdev.nci.org.au/jenkins/job/conda/)

2. Update the module aliases by editing the file `/g/data3/hh5/public/modules/conda/.modulerc`. Increase the versions in the file to the new 'stable' and 'unstable' versions

3. Remove the oldest environment by moving the environment directory in `/g/data3/hh5/public/apps/miniconda3/envs` into the `archive` subdirectory (this should be possible for a hh5 admin regardless of who owns the environment) and asking the environment owner to delete it.
