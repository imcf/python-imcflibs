#!/bin/bash

set -o errexit  # exit on any error
set -o nounset  # empty variables are not permitted

# FIXME: the MOCKS_RELEASE is now only used for DOWNLOADING the 'micrometa' and
# 'sjlogging' wheels from github, this should be cleaned up and moved to PyPI as
# well as soon as possible!

# set the version of "imcf-fiji-mocks" to be used for downloading wheels:
MOCKS_RELEASE="0.2.0"

cd "$(dirname "$0")"/..

test -d "venv2" || {
    echo "== Creating a Python2 venv..."
    python2 -m virtualenv venv2
    URL_PFX="https://github.com/imcf/imcf-fiji-mocks/releases/download"
    venv2/bin/pip --no-python-version-warning install --upgrade \
        $URL_PFX/v$MOCKS_RELEASE/micrometa-15.2.2-py2.py3-none-any.whl \
        sjlogging \
        imcf-fiji-mocks \
        olefile==0.46 \
        pytest \
        pytest-cov \
        pip
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
    echo "== Finished installing local 'imcflibs'."
    echo
}

echo "== Running pytest..."
set -x
venv2/bin/pytest "$@"
