# Testing 🧪🧫 in Fiji / ImageJ2

## Using `pytest` 🐍🔬 and Python 3 for plain Python code

Those parts of the package that do not interact / depend on ImageJ objects can
be tested via [`pytest`][pytest] up to a certain level, some (most?) of them
should even work in a Python 3 environment.

To perform those tests, the packges otherwise provided by ImageJ need to be
mocked using the `imcf-fiji-mocks` package. For seting up a _venv_ use the steps
described here:

```bash
# check if we're "inside" the repo already, otherwise clone it here:
git remote -v 2>/dev/null | grep -q imcf/python-imcflibs || {
  git clone https://github.com/imcf/python-imcflibs/
  cd python-imcflibs
  git checkout -b pytest origin/pytest
}
# create and activate a new venv:
test -d "venv" || python3 -m venv venv
source venv/bin/activate

# install dependencies / requirements:
MOCKS_REL="0.1.1"
URL_PFX="https://github.com/imcf/imcf-fiji-mocks/releases/download/v$MOCKS_REL"
pip install --upgrade \
    $URL_PFX/imcf_fiji_mocks-0.1.1-py2.py3-none-any.whl \
    $URL_PFX/micrometa-15.2.2-py2.py3-none-any.whl \
    $URL_PFX/sjlogging-0.5.2-py2.py3-none-any.whl \
    olefile \
    pytest \
    pytest-cov \
    pip

# now install the 'imcflibs' package in editable mode:
pip install -e .
```

Using this _venv_, tests can be triggered just the usual way. To run only
specific tests, use e.g.

```bash
pytest tests/bdv/test_processingoptions.py
```

## Common testing with ImageJ2 / Fiji

Unfortunately there is nothing like `pytest` available for the parts that are
running exclusively in a ImageJ2 / Fiji context. So in order to provide at least
some basic, semi-interactive tests the following conventions are being used:

* Each _**function**_ in any of the `imcflibs.imagej` submodules should have its
  own directory underneath `/tests/imagej/`, using their fully qualified name
  as the path (only skipping the `imcflibs.` prefix). For example test scripts
  for `imcflibs.imagej.bioformats.import_image()` will be placed in the
  directory `/tests/imagej/bioformats/import_image/`.
* The scripts inside those directories are intended to be run interactively /
  manually in a (freshly started) Fiji instance. Yes, really. Any other
  suggestions are highly welcome!
* To facilitate this, a collection of _test images_ (and possibly other input
  data) should be cloned to the local file system. Currently this `sample_data`
  repository is _NOT_ publicly available due to legal ⚖ uncertainties. A repo
  containing test data 🗞 that can be published should be assembled over time
  though!
* Any _interactive_ test script should start with a header similar to the one
  described below. Paths to input data _inside_ the test scripts **has** to be
  relative to the location of the `sample_data` repository mentioned above. This
  will allow for a fairly okayish testing workflow like this:
  * Make your changes in VS Code, then trigger a build by pressing `Shift` +
  `Ctrl` + `B`. If things are configured as described in the *DEVELOPMENT*
  document, the resulting `.jar` file will be automatically placed in Fiji's
  `jars/` folder.
  * Next, start a fresh instance of the Fiji that received the newly built JAR.
  * After Fiji has started, simply drag and drop the desired test script onto
    the main window. This will open the _Script Editor_, then press `Ctrl` + `R`
    to launch the script.
  * Only on the first run on the machine being used you will have to select the
    base location of the `sample_data` repository.
  * All subsequent runs of _**any**_ test script using the defined _Script
    Parameter_ `IMCF_TESTDATA` will remember this selection, so it will be
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
