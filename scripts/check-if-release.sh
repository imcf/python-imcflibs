#!/bin/bash

# Very basic script checking for the existence of a file 'release.properties' in
# the root of the repository. If this is present, the state of the checkout
# indicates this is a proper release made through the 'release-version.sh'
# script from the 'scijava-scripts' repo. Will return false if the file is not
# present, can be overridden with an environment variable.

# The idea is to include this in automated builds to prevent accidential
# attempts of publishing non-releases to PyPI.

set -o errexit  # exit on any error

PROPERTIES="release.properties"

test -n "$IGNORE_NO_RELEASE" &&
    echo "⚠ 🔀 NOT checking for file '$PROPERTIES'... ⚠" &&
    exit 0

cd "$(dirname "$0")/.."

echo "Checking if '$PROPERTIES' exists..."
test -f "$PROPERTIES" && echo "All good ✅" && exit 0

echo 🛑🛑🛑
echo '/-----------------------------------------------------\'
echo "| Couldn't find 'release.properties', STOPPING build! |"
echo "| To ignore this, add this to the environment:        |"
echo "|  > export IGNORE_NO_RELEASE=true                    |"
echo '\-----------------------------------------------------/'
echo 🛑🛑🛑

exit 1
