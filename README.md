
# IMCFlibs 🐍 ☕ 🔩 🔧 🪛

[![Linting ⚡](https://github.com/imcf/python-imcflibs/actions/workflows/lint.yml/badge.svg)](https://github.com/imcf/python-imcflibs/actions/workflows/lint.yml)
[![Pytest-Python2 🧪🐍](https://github.com/imcf/python-imcflibs/actions/workflows/pytest-python2.yml/badge.svg)](https://github.com/imcf/python-imcflibs/actions/workflows/pytest-python2.yml)
[![Pytest-Poetry 🧪🎭](https://github.com/imcf/python-imcflibs/actions/workflows/pytest-poetry.yml/badge.svg)](https://github.com/imcf/python-imcflibs/actions/workflows/pytest-poetry.yml)
[![codecov](https://codecov.io/github/imcf/python-imcflibs/branch/devel/graph/badge.svg?token=JTDK74OT79)](https://codecov.io/github/imcf/python-imcflibs)

[![Build Status](https://github.com/imcf/python-imcflibs/actions/workflows/build.yml/badge.svg)][build]
[![DOI](https://zenodo.org/badge/156891364.svg)][doi]

This package contains a diverse collection of Python functions dealing with
paths, I/O (file handles, ...), strings etc. and tons of [Fiji] / [ImageJ2]
convenience wrappers to simplify scripting and reduce cross-script redundancies.

Initially this has been a multi-purpose package where a substantial part had
been useful in **CPython** as well. However, since the latest Jython release is
still based on Python 2.7 (see the [Jython 3 roadmap][jython3] for more info),
*imcflibs* is now basically limited to the **Fiji / ImageJ2 ecosystem**.

Releases are made through Maven and published to the [SciJava Maven
repository][sj_maven]. The easiest way to use the lib is by adding the **`IMCF
Uni Basel`** [update site][imcf_updsite] to your ImageJ installation.

The [`pip install`able package][pypi] is probably only useful for two cases:
running `pytest` (where applicable) and rendering [HTML-based API docs][apidocs]
using [pdoc]. Let us know in case you're having another use case 🎪 for it.

Developed and provided by the [Imaging Core Facility (IMCF)][imcf] of the
Biozentrum, University of Basel, Switzerland.

## Installation Instructions

Two ways of installing the `imcflibs` package are described here, the "*easy*"
one through the *Fiji Update Sites* and the "*manual*" method using packages
explicitly downloaded from [SciJava Maven][sj_maven].

### 🧿 Default: Installation via Update Sites

After a fresh install of [Fiji], navigate to *Help* -> *Update* and in the
resulting window, press *Manage Update Sites*. Here, search for and tick the
following necessary update sites for this package.

- ImageJ
- Fiji
- 3D ImageJ-Suite
- clij2
- IJPB-plugins
- IMCF Uni Basel
- StarDist
- CALM
- TrackMate-Cellpose
- TrackMate-Helper
- TrackMate-StarDist
- TrackMate-Weka
- TrackMate-MorpholibJ

The **`IMCF Uni Basel`** update-site will always provide the latest compatible
combination of *official* `.jar` files to use this package.

### Manual Downloads

In addition to the update sites, two manual downloads concerning OMERO are necessary:

- [simple-omero-client]
- [omero-insight]

### 🏗 Alternative: SciJava Maven Package 👷

💡 **IMPORTANT:** 💡 same as for the *default* installation previously
described, you will need to enable **all Update Sites listed above** in your
Fiji as well when using the method described here!

The most up-to-date `.jar` (or any other published version, including
pre-releases) for this package can be always found on the [Scijava Maven
repository][sj_maven]. Navigate to the `python-imcflibs` folder, pick the
desired version (can also be a pre-release) and download the contained `.jar`
file, e.g. `python-imcflibs-2.0.0.jar`.

Then simply place that file in the `jars` folder of your Fiji installation, e.g
`D:\Development\Fiji.app\jars\` or `/opt/Fiji.app/jars/`, possibly removing
other versions of the same package from that folder - then (re-)start Fiji.

If you'd prefer to use the cutting-edge version from GitHub, look into the
[development instructions](DEVELOPMENT.md) for details.

### Installation Testing

To check the package's correct installation in Fiji, search for *Script
Interpreter* in the Search bar, and type `:lang python`, followed by e.g.
`import imcflibs.imagej.misc`. If no errors are shown, the installation was
successful. Alternatively, you can scroll in the sidebar of the Interpreter to
search for imcflibs.

## Example usage

### Shading correction / projection

Apply a shading correction model and create a maximum-intensity projection:

```Python
from imcflibs.imagej.shading import correct_and_project

model = "/path/to/shading_model.tif"
raw_image = "/path/to/raw_data/image.ome.tif"
out_path = "/path/to/processed_data/"

correct_and_project(raw_image, out_path, model, "Maximum", ".ics")
```

### Split TIFFs by channels and slices

- See the [Split_TIFFs_By_Channels_And_Slices.py][script_split] script.

### Use status and progress bar updates

- See the [FluoView_OIF_OIB_OIR_Simple_Stitcher.py][script_fvstitch] script.

[imcf]: https://www.biozentrum.unibas.ch/imcf
[imagej2]: https://imagej.net
[fiji]: https://fiji.sc
[jython3]: https://www.jython.org/jython-3-roadmap
[sj_maven]: https://maven.scijava.org/service/rest/repository/browse/releases/ch/unibas/biozentrum/imcf/
[imcf_updsite]: https://imagej.net/list-of-update-sites/
[script_split]: https://github.com/imcf/imcf-fiji-scripts/blob/master/src/main/resources/scripts/Plugins/IMCF_Utilities/Convert/Split_TIFFs_By_Channels_And_Slices.py
[script_fvstitch]: https://github.com/imcf/imcf-fiji-scripts/blob/master/src/main/resources/scripts/Plugins/IMCF_Utilities/Stitching_Registration/FluoView_OIF_OIB_OIR_Simple_Stitcher.py
[doi]: https://zenodo.org/badge/latestdoi/156891364
[build]: https://github.com/imcf/python-imcflibs/actions/workflows/build.yml
[apidocs]: https://imcf.one/apidocs/imcflibs/imcflibs.html
[pdoc]: https://pdoc.dev/
[pypi]: https://pypi.org/project/imcflibs/
[simple-omero-client]: https://github.com/GReD-Clermont/simple-omero-client
[omero-insight]: https://github.com/ome/omero-insight
