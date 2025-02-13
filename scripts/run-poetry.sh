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

# # sed -i 's/^python = ">=2.7"$/python = ">=3.10"/' pyproject.toml

set +o errexit  # otherwise the script stops if poetry exits non-zero
poetry "$@"  # run poetry with the parameters given to the script
RETVAL=$?  # remember the actual exit code of poetry for returning it below!

### clean up the moved source tree and restore the previous state:
git restore pyproject.toml
git restore "src/*/__init__.py"

exit $RETVAL  # now return the exit code from running poetry
