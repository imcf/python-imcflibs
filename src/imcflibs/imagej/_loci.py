"""Internal wrapper module to import from the (Java) loci package.

This module exists to work around the issue that importing some of the classes
from the Java `loci` package would require syntax that is considered invalid by
any C-Python parser (but is still valid and working in Jython) and hence will
break usage of Black, Pylint, and similar.

By aggregating those "special" imports into this (private) submodule we can
properly work around that issue by providing "dummy" objects for C-Python and
importing the actual modules / classes when running within Jython. To avoid the
invalid syntax issue (which would still prevent C-Python-based tools like black
and pdoc to run) those parts are done via `importlib` calls.

Other loci-related imports (i.e. those without problematic syntax) are placed in
here simply for consistency reasons (to have everything in the same place).
"""

#
### *** WARNING *** ### *** WARNING *** ### *** WARNING *** ### *** WARNING ***
#
# Whenever an import is added here, make sure to also update the corresponding
# part in `imcf-fiji-mocks`: https://github.com/imcf/imcf-fiji-mocks/
#
### *** WARNING *** ### *** WARNING *** ### *** WARNING *** ### *** WARNING ***
#


from loci.plugins import BF

# dummy objects to prevent failing imports in a non-ImageJ / Jython context:
ImporterOptions = None
ZeissCZIReader = None
DefaultMetadataOptions = None
MetadataLevel = None
DynamicMetadataOptions = None

# perform the actual imports when running under Jython using `importlib` calls:
import platform as _python_platform

if _python_platform.python_implementation() == "Jython":  # pragma: no cover
    import importlib

    _loci_plugins_in = importlib.import_module("loci.plugins.in")
    ImporterOptions = _loci_plugins_in.ImporterOptions

    _loci_formats_in = importlib.import_module("loci.formats.in")
    ZeissCZIReader = _loci_formats_in.ZeissCZIReader
    DefaultMetadataOptions = _loci_formats_in.DefaultMetadataOptions
    MetadataLevel = _loci_formats_in.MetadataLevel
    DynamicMetadataOptions = _loci_formats_in.DynamicMetadataOptions
    MetadataOptions = _loci_formats_in.MetadataOptions
del _python_platform

from loci.formats import ImageReader, Memoizer, MetadataTools
