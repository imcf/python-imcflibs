"""Python convenience from and for the IMCF (Imaging Core Facility).

.. include:: ../../README.md

.. include:: ../../TESTING.md

.. include:: ../../CHANGELOG.md
"""

__version__ = "${project.version}"

from . import iotools
from . import log
from . import pathtools
from . import strtools

# check if we're running in Jython, then also import the 'imagej' submodule:
import platform as _python_platform

if _python_platform.python_implementation() == "Jython":  # pragma: no cover
    from . import imagej
del _python_platform
