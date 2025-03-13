
# IMCFlibs 🐍 ☕ 🔩 🔧 🪛

[![Build Status](https://github.com/imcf/python-imcflibs/actions/workflows/build.yml/badge.svg)][build]
[![DOI](https://zenodo.org/badge/156891364.svg)][doi]

This package contains a diverse collection of Python functions dealing with
paths, I/O (file handles, ...), strings etc. and tons of [Fiji][fiji] /
[ImageJ2][imagej] convenience wrappers to simplify scripting and reduce
cross-script redundanciees.

Initially this has been a multi-purpose package where a substantial part had
been useful in **CPython** as well. However, since the latest Jython
release is still based on Python 2.7 (see the [Jython 3 roadmap][jython3] for
more info), *imcflibs* is now basically limited to the **Fiji / ImageJ2
ecosystem**.

Releases are made through Maven and published to the [SciJava Maven
repository][sj_maven]. The easiest way to use the lib is by adding the **`IMCF
Uni Basel`** [update site][imcf_updsite] to your ImageJ installation.

The [`pip install`able package][pypi] is probably only useful for two cases:
running `pytest` (where applicable) and rendering [HTML-based API docs][apidocs]
using [`pdoc`][pdoc]. Let us know in case you're having another use case 🎪 for
it.

Developed and provided by the [Imaging Core Facility (IMCF)][imcf] of the
Biozentrum, University of Basel, Switzerland.

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

* See the [Split_TIFFs_By_Channels_And_Slices.py][script_split] script.

### Use status and progress bar updates

* See the [FluoView_OIF_OIB_OIR_Simple_Stitcher.py][script_fvstitch] script.

[imcf]: https://www.biozentrum.unibas.ch/imcf
[imagej]: https://imagej.net
[fiji]: https://fiji.sc
[jython3]: https://www.jython.org/jython-3-roadmap
[sj_maven]: https://maven.scijava.org/#nexus-search;gav~ch.unibas.biozentrum.imcf~~~~
[imcf_updsite]: https://imagej.net/list-of-update-sites/
[script_split]: https://github.com/imcf/imcf-fiji-scripts/blob/master/src/main/resources/scripts/Plugins/IMCF_Utilities/Convert/Split_TIFFs_By_Channels_And_Slices.py
[script_fvstitch]: https://github.com/imcf/imcf-fiji-scripts/blob/master/src/main/resources/scripts/Plugins/IMCF_Utilities/Stitching_Registration/FluoView_OIF_OIB_OIR_Simple_Stitcher.py
[doi]: https://zenodo.org/badge/latestdoi/156891364
[build]: https://github.com/imcf/python-imcflibs/actions/workflows/build.yml
[apidocs]: https://imcf.one/apidocs/imcflibs/imcflibs.html
[pdoc]: https://pdoc.dev/
[pypi]: https://pypi.org/project/imcflibs/
