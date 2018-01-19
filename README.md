# Anaconda environments

Environment files are in this repository's branches

Install from anaconda.org

    conda env create accessdev/analysis

Load on Raijin

    module use ~access/modules
    module load conda/analysis

Install development version from file

    conda env create -f analysis.yml
