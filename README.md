# IMCFlibs

[![DOI](https://zenodo.org/badge/156891364.svg)](https://zenodo.org/badge/latestdoi/156891364)

## Python convenience helpers. 🐍 ☕ 🔩 🔧 🪛

This package contains a diverse collection of Python functions dealing with
paths, I/O (file handles, ...), strings etc. and tons of [Fiji][fiji] /
[ImageJ2][imagej] convenience wrappers to simplify scripting and reduce
cross-script redundanciees.

Initially this has been a multi-purpose package where a substantial part had
been useful in **CPython** as well. However, since the latest Jython
release is still based on Python 2.7 (see the [Jython 3 roadmap][jython3] for
more info), *imcflibs* is now basically limited to the **Fiji/ImageJ2
ecosystem** (which is also the reason there is no `pip install`able package
provided).

Releases are made through Maven and published to the [SciJava Maven
repository][sj_maven]. The easiest way to use the lib is by adding the **`IMCF
Uni Basel`** [update site][imcf_updsite] to your ImageJ installation.

Developed and provided by the [Imaging Core Facility (IMCF)][imcf] of the
Biozentrum, University of Basel, Switzerland.

## Contents

📝 TODO!

## Example usage

📝 TODO!

[imcf]: https://www.biozentrum.unibas.ch/imcf
[imagej]: https://imagej.net
[fiji]: https://fiji.sc
[jython3]: https://www.jython.org/jython-3-roadmap
[sj_maven]: https://maven.scijava.org/#nexus-search;gav~ch.unibas.biozentrum.imcf~~~~
[imcf_updsite]: https://imagej.net/list-of-update-sites/
