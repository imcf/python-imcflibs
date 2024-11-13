#!/bin/bash

set -o errexit  # exit on any error
set -o nounset  # empty variables are not permitted

# set the version of "imcf-fiji-mocks" to be used:
MOCKS_RELEASE="0.1.1"

cd "$(dirname "$0")"/..

test -d "venv2" || {
    python2 -m virtualenv venv2
    source venv2/bin/activate
    URL_PFX="https://github.com/imcf/imcf-fiji-mocks/releases/download"
    pip install --upgrade \
        $URL_PFX/v$MOCKS_RELEASE/imcf_fiji_mocks-0.1.1-py2.py3-none-any.whl \
        $URL_PFX/v$MOCKS_RELEASE/micrometa-15.2.2-py2.py3-none-any.whl \
        $URL_PFX/v$MOCKS_RELEASE/sjlogging-0.5.2-py2.py3-none-any.whl \
        olefile==0.46 \
        pytest \
        pytest-cov \
        pip

    deactivate
}

poetry build -vv

venv2/bin/pip uninstall --yes imcflibs
venv2/bin/pip install dist/*.whl

# call this script with `--cov --cov-report html` to generate coverage reports:
venv2/bin/pytest "$@"
