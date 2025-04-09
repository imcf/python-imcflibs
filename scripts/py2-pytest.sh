#!/bin/bash

set -o errexit  # exit on any error
cd "$(dirname "$0")"/..

if [ -n "$VENV_PATH" ]; then
    # can be used for GH actions to cache the venv by giving it a fixed path:
    echo "Using venv path from envvar VENV_PATH='$VENV_PATH'."
    VENV="$VENV_PATH"
else
    VENV="$(mktemp --directory --dry-run --tmpdir=. venv2.pytest-XXX)"
fi

if [ -n "$PYENV_ROOT" ]; then
    # in case pyenv was retrieved e.g. from a GH actions cache, it will be
    # present in the filesystem but not added to the path (this is done when
    # the installer runs, but will not persist to subsequent runs that will get
    # their pyenv extracted from the cache), therefore we're force-adding it:
    echo "Found envvar PYENV_ROOT='$PYENV_ROOT', adjusting PATH..."
    export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
fi

echo "PATH=$PATH"

if [ -n "$PY_VERSION" ]; then
    echo "Calling [pyenv local $PY_VERSION]..."
    pyenv local "$PY_VERSION"
fi

# now we're done checking the environment, so disallow empty variables below:
set -o nounset

# NOTE: the `pip2` calls below were initially using a flag to prevent the
# deprecation warning for Python 2.7 (`--no-python-version-warning`), alas this
# flag only got into pip as of version 20.0, which is newer than the default one
# provided by GitHub's "ubuntu-22.04" image, so these commands would fail -
# therefore we'll have to live with the warnings for now.

if ! [ -d "$VENV" ]; then
    pip2 show virtualenv > /dev/null || {
        echo "== Installing 'virtualenv' for Python2..."
        pip2 install virtualenv
    }
    echo "== Creating a Python2 venv in [$VENV]..."
    python2 -m virtualenv --always-copy "$VENV"
    echo "== Finished creating a Python2 venv."
fi

function vpip() {
    "$VENV/bin/pip" "$@"
}

echo
echo "===== Using venv at: [$VENV] ====="
"$VENV/bin/python" --version
echo

echo "== Installing local version of 'imcflibs' package..."
# NOTE: for being able to use coverage, the package has to be installed in
# editable mode, making it necessary to move `pyproject.toml` out of the way
# and creating a `setup.py` for the actual installation process (will be
# reverted after installing):
### parse the version from 'pom.xml':
PACKAGE_VERSION=$(xmlstarlet sel --template -m _:project -v _:version pom.xml)
PACKAGE_NAME=$(xmlstarlet sel --template -m _:project -v _:artifactId pom.xml)

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
echo "== * Mocking 'setup.py' with package version $PACKAGE_VERSION"
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
vpip install --editable .

echo "== * Installed package version reported by pip:"
vpip show imcflibs | grep ^Version:

echo "== * Re-enabling 'pyproject.toml'..."
mv pyproject_.toml pyproject.toml

echo "== * Removing 'setup.py'..."
rm setup.py

echo "== * Installing dependencies (incl. pre-release and dev versions)..."
vpip install --upgrade --pre \
    imcf-fiji-mocks

echo "== * Installing dependencies..."
vpip install \
    python-micrometa \
    sjlogging \
    olefile==0.46 \
    pytest \
    pytest-cov \
    pip

echo "== * Cleaning up egg-info..."
# NOTE: this can only be done AFTER the pip-install from above as otherwise
# dependency resolution won't work due to lack of package metadata:
rm -r src/imcflibs.egg-info
echo "== Finished installing local 'imcflibs'."
echo

echo "== Running pytest..."
set -o xtrace
set +o errexit  # otherwise the script stops if pytest exits non-zero
"$VENV/bin/pytest" "$@"  # run pytest with the parameters given to the script
RETVAL=$?  # remember the actual exit code of pytest for returning it below!
set +o xtrace

echo
echo "== Done. Leaving venv around: [$VENV]"
echo

exit $RETVAL  # now return the exit code from running pytest
