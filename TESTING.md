# Testing 🧪🧫 in Fiji / ImageJ2

## Using 🎭 Poetry, pytest 🐍🔬 and Python 3 for plain Python code

The easiest way to run [`pytest`][pytest] (using Python 3) is when you're
already having a working [poetry] setup. In that case tests can simply be run by
using the `run-poetry.sh` wrapper script, for example:

```bash
scripts/run-poetry.sh run pytest tests/test_misc.py
```

## Using pytest 🐍🔬 and Python 3 for plain Python code

Those parts of the package that do not interact / depend on ImageJ objects can
be tested via [`pytest`][pytest] up to a certain level, some (most?) of them
should even work in a Python 3 environment.

To perform those tests, the packages otherwise provided by ImageJ need to be
mocked using the `imcf-fiji-mocks` package. For setting up a *venv* use the
steps described here:

```bash
# check if we're "inside" the repo already, otherwise clone it here:
git remote -v 2>/dev/null | grep -q imcf/python-imcflibs || {
  git clone https://github.com/imcf/python-imcflibs/
  cd python-imcflibs
  git checkout -b processing-options-class origin/processing-options-class
}
# create and activate a new venv:
test -d "venv" || python3 -m venv venv
source venv/bin/activate

# install dependencies / requirements:
MOCKS_REL="0.14.0"
URL_PFX="https://github.com/imcf/imcf-fiji-mocks/releases/download/v$MOCKS_REL"
pip install --upgrade \
    $URL_PFX/imcf_fiji_mocks-${MOCKS_REL}-py2.py3-none-any.whl \
    $URL_PFX/micrometa-15.2.2-py2.py3-none-any.whl \
    $URL_PFX/sjlogging-0.5.2-py2.py3-none-any.whl \
    olefile \
    pytest \
    pytest-cov \
    pip

# now install the 'imcflibs' package in editable mode:
pip install -e .
```

Using this *venv*, tests can be triggered just the usual way. To run only
specific tests, use e.g.

```bash
pytest tests/bdv/test_processingoptions.py
```

## Using pytest 🐍🔬 and Python 2 for plain Python code

For running [`pytest`][pytest] in a C-Python 2 environment, things are slightly
more complicated than the approach described for Python 3 above as `pip` for
Python 2 cannot install a project in *editable* mode unless it has a `setup.py`
file (which we don't have and don't want).

Therefore, a wheel needs to be built (e.g. using [`poetry`][poetry]) and
installed (every time) into the corresponding virtualenv when performing the
tests. Assuming you're having a working *poetry* setup on your machine, you can
simply use the provided `scripts/py2-pytest.sh` wrapper that will create the
virtualenv, build and install the `imcflibs` wheel and launch `pytest` with the
parameters specified, e.g.

```bash
bash scripts/py2-pytest.sh -rv --cov --cov-report html
```

## Common (interactive) testing with ImageJ2 / Fiji

Unfortunately there is nothing like `pytest` available for the parts that are
running exclusively in a ImageJ2 / Fiji context. So in order to provide at least
some basic, semi-interactive tests the following conventions are being used:

* Each ***function*** in any of the `imcflibs.imagej` submodules should have its
  own directory underneath `/tests/interactive-imagej/`, using their fully
  qualified name as the path (only skipping the `imcflibs.` prefix). For example
  test scripts for `imcflibs.imagej.bioformats.import_image()` will be placed in
  the directory `/tests/interactive-imagej/bioformats/import_image/`.
* The scripts inside those directories are intended to be run interactively /
  manually in a (freshly started) Fiji instance. Yes, really. Any other
  suggestions are highly welcome!
* To facilitate this, a collection of *test images* (and possibly other input
  data) should be cloned to the local file system. Currently this `sample-data`
  repository is *NOT* publicly available due to legal ⚖ uncertainties. A repo
  containing test data 🗞 that can be published should be assembled over time
  though!
* Any *interactive* test script should start with a header similar to the one
  described below. Paths to input data *inside* the test scripts **has** to be
  relative to the location of the `sample-data` repository mentioned above. This
  will allow for a fairly okay-ish testing workflow like this:
  * Make your changes in VS Code, then trigger a build by pressing `Shift` +
  `Ctrl` + `B`. If things are configured as described in the *DEVELOPMENT*
  document, the resulting `.jar` file will be automatically placed in Fiji's
  `jars/` folder.
  * Next, start a fresh instance of the Fiji that received the newly built JAR.
  * After Fiji has started, simply drag and drop the desired test script onto
    the main window. This will open the *Script Editor*, then press `Ctrl` + `R`
    to launch the script.
  * Only on the first run on the machine being used you will have to select the
    base location of the `sample-data` repository.
  * All subsequent runs of ***any*** test script using the defined *Script
    Parameter* `IMCF_TESTDATA` will remember this selection, so it will be
    sufficient to just confirm the dialog by pressing `Enter`.

### Quick Workflow Summary

First, make sure to have the test data 🔬🔭around (or some mocks 🪨🪵), then:

1. Code 📝
1. Build and deploy locally (`Shift`+`Ctrl`+`B`) 📦
1. Start Fiji 🇫🇯
1. Drag-and-Drop the respective test script 🐍🧪
1. Hit `Ctrl`+`R` to run it 🏃‍♀️
1. Confirm dialog with `Enter` ✅
1. Inspect the output 🔎👀
1. Repeat 🔁

### Test Script Template 🏗

As described above, each test script should use the `IMCF_TESTDATA` parameter to
facilitate the manual testing approach. Simply use this template header for
creating new scripts (or look into existing ones):

```Python
# @ File (label="IMCF testdata location", style="directory") IMCF_TESTDATA

import os
from imcflibs.pathtools import join2

testfile = join2(IMCF_TESTDATA, "systems/lsm700/beads/10x_phmax.czi")
assert os.path.exists(testfile)
```

In case the test requires the components of the testfile's path to be used, this
snippet will do the job:

```Python
# @ File (label="IMCF testdata location", style="directory") IMCF_TESTDATA

import os
from imcflibs.pathtools import parse_path

components = parse_path("systems/lsm700/beads/10x_phmax.czi", IMCF_TESTDATA)
assert os.path.exists(components["full"])
```

[pytest]: https://pytest.org
[poetry]: https://python-poetry.org
