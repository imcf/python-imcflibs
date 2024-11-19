#!/bin/bash

set -o errexit  # exit on any error
set -o nounset  # empty variables are not permitted

cd "$(dirname "$0")"/..

test -d "venv2" || {
    echo "== Creating a Python2 venv..."
    python2 -m virtualenv venv2
    echo "== Finished creating a Python2 venv."

    echo "== Installing local version of 'imcflibs' package..."
    # NOTE: for being able to use coverage, the package has to be installed in
    # editable mode, making it necessary to move `pyproject.toml` out of the way
    # and creating a `setup.py` for the actual installation process (will be
    # reverted after installing):
    echo "== * Mocking 'setup.py'..."
    echo "import setuptools
setuptools.setup(
    name='imcflibs',
    package_dir={'': 'src'},
)
" > setup.py
    echo "== * Temporarily disabling 'pyproject.toml'..."
    mv pyproject.toml pyproject_.toml
    echo "== * Installing package in editable mode..."
    venv2/bin/pip --no-python-version-warning install --editable .
    echo "== * Re-enabling 'pyproject.toml'..."
    mv pyproject_.toml pyproject.toml
    echo "== * Removing 'setup.py'..."
    rm setup.py
    echo "== * Cleaning up egg-info..."
    rm -r src/imcflibs.egg-info
    echo "== Finished installing local 'imcflibs'."
    echo
    venv2/bin/pip --no-python-version-warning install \
        python-micrometa \
        sjlogging \
        "imcf-fiji-mocks>=0.3.0" \
        olefile==0.46 \
        pytest \
        pytest-cov \
        pip
}

echo "== Running pytest..."
set -x
venv2/bin/pytest "$@"
