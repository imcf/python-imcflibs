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
    ### parse the version from 'pom.xml':
    PACKAGE_VERSION=$(xmlstarlet sel --template -m _:project -v _:version pom.xml)
    echo "Package version from POM: [$PACKAGE_VERSION]"
    ### make sure to have a valid Python package version:
    case $PACKAGE_VERSION in
    *-SNAPSHOT*)
        PACKAGE_VERSION=${PACKAGE_VERSION/-SNAPSHOT/}
        ### calculate the distance to the last release tag:
        LAST_TAG=$(git tag --list "${PACKAGE_NAME}-*" | sort | tail -n1)
        # echo "Last git tag: '$LAST_TAG'"
        COMMITS_SINCE=$(git rev-list "${LAST_TAG}..HEAD" | wc -l)
        # echo "Nr of commits since last tag: $COMMITS_SINCE"
        HEAD_ID=$(git rev-parse --short HEAD)
        # echo "HEAD commit hash: $HEAD_ID"
        PACKAGE_VERSION="${PACKAGE_VERSION}.dev${COMMITS_SINCE}+${HEAD_ID}"
        ;;
    esac

    echo "Using Python package version: [$PACKAGE_VERSION]"

    echo "== * Mocking 'setup.py' (package version: $PACKAGE_VERSION)..."
    echo "import setuptools
setuptools.setup(
    name='imcflibs',
    version='$PACKAGE_VERSION',
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
