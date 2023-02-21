"""A collection of Python helper functions.

This package contains a diverse collection of Python functions dealing with
paths, I/O (file handles, ...), strings etc.

In addition (to the regular packaging) it is set up to be packaged by Maven to
be ready for being used in [ImageJ2][imagej].

Developed and provided by the [Imaging Core Facility (IMCF)][imcf] of the
Biozentrum, University of Basel, Switzerland.

# Contents

:note: TODO!

# Example usage

:note: TODO!

[imcf]: https://www.biozentrum.unibas.ch/imcf
[imagej]: https://imagej.net
"""

__version__ = "${project.version}"

from . import iotools
from . import log
from . import pathtools
from . import strtools

# check if we're running in Jython, then also import the 'imagej' submodule:
import platform as _python_platform

if _python_platform.python_implementation() == "Jython":
    from . import imagej
del _python_platform
