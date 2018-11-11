#!/usr/bin/env python

"""Doctest runner for the imcflibs package.

Needs to be run from imcflibs's parent directory.
"""

if __name__ == "__main__":
    import doctest
    import sys

    VERB = '-v' in sys.argv

    import imcflibs
    import imcflibs.pathtools
    import imcflibs.iotools
    import imcflibs.strtools

    doctest.testmod(imcflibs, verbose=VERB)
    doctest.testmod(imcflibs.pathtools, verbose=VERB)
    doctest.testmod(imcflibs.iotools, verbose=VERB)
    doctest.testmod(imcflibs.strtools, verbose=VERB)
