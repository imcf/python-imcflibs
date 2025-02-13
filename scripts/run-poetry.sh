#!/bin/bash

set -o errexit  # exit on any error

cd "$(dirname "$0")/.."

STATUS=$(git status --porcelain)

if [ -z "$RUN_ON_UNCLEAN" ]; then
    if [ -n "$STATUS" ]; then
        echo "==== ERROR: repository unclean, stopping! ===="
        echo
        git status
        echo
        echo "--------"
        echo "To ignore this (you have been warned!), set an environment var:"
        echo
        echo "> export RUN_ON_UNCLEAN=true"
        echo
        exit 1
    fi
fi

### clean up old poetry artifacts:
rm -rf dist/

# adjust metadata version strings:
scripts/pom-to-pyproject.sh

# in case the project needs to be "installed" (e.g. to run pytest and generate
# coverage reports), the Python version specified in the project's dependencies
# needs to be set to a version satisfying the other dependencies requirements -
# this can be turned off e.g. for simply packaging for PyPi.
PYPROJ="pyproject.toml"
DEPS_PYTHON='>=3.10'
if [ -z "$IGNORE_DEPS_PYTHON" ]; then
    echo "$PYPROJ: setting [python = \"$DEPS_PYTHON\"]"
    echo "Use 'export IGNORE_DEPS_PYTHON=true' to skip this step."
    sed -i 's/^python = ">=2.7"$/python = "'"$DEPS_PYTHON"'"/' $PYPROJ
else
    echo "$PYPROJ: found 'IGNORE_DEPS_PYTHON' envvar, not modifying."
fi

set +o errexit  # otherwise the script stops if poetry exits non-zero
poetry "$@"  # run poetry with the parameters given to the script
RETVAL=$?  # remember the actual exit code of poetry for returning it below!

### clean up the moved source tree and restore the previous state:
git restore pyproject.toml
git restore "src/*/__init__.py"

exit $RETVAL  # now return the exit code from running poetry
