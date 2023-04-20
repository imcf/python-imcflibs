"""Internal wrapper module to import from the (Java) loci package.

This module mostly exists to work around the issue that importing the
`ImporterOptions` class from the Java `loci` package requires syntax to be used
that is considered invalid by any C-Python parser (but is still valid and
working in Jython) and hence will break usage of Black, Pylint, and similar.

By stashing this into an internal submodule only checks on this specific
(minimalistic) file will fail but remain operational for the other code.

So why are the other imports in here then?

This was a conscious decision as it seems to be confusing that *some* parts from
the `loci` package need to be imported from the `imcflibs.imagej._loci`
sub-module while others are imported directly. Instead we're simply importing
proxy-style all loci components through the file here.

NOTE: the actual import of `ImporterOptions` still requires the `# pdoc: skip`
pragma to work with the documentation generation scripts, e.g.

```
from ._loci import ImporterOptions  # pdoc: skip
```
"""

from loci.plugins import BF

from loci.plugins.in import ImporterOptions  # pdoc: skip

from loci.formats import ImageReader, Memoizer