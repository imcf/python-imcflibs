"""I/O related functions."""

import io

import glob
import zipfile

import os
from os.path import splitext, join

from .log import LOG as log
from .strtools import flatten


try:
    # Python 2: "file" is built-in
    file_types = file, io.IOBase
except NameError:
    # Python 3: "file" fully replaced with IOBase
    file_types = (io.IOBase,)


def filehandle(fname, mode="r"):
    """Make sure a variable is either a filehandle or create one from it.

    This function takes a variable and checks whether it is already a
    filehandle with the desired mode or a string that can be turned into a
    filehandle with that mode. This can be used e.g. to make functions agnostic
    against being supplied a file-type parameter that was gathered via argparse
    (then it's already a filehandle) or as a plain string.

    Parameters
    ----------
    fname : str or filehandle
    mode : str
        The desired mode of the filehandle (default=read).

    Returns
    -------
    A valid (open) filehandle with the given mode. Raises an IOError
    otherwise.

    Example
    -------
    >>> fname = __file__
    >>> type(fname)
    <type 'str'>
    >>> type(filehandle(fname))
    <type 'file'>
    >>> fh = open(__file__, 'r')
    >>> type(fh)
    <type 'file'>
    >>> type(filehandle(fh))
    <type 'file'>
    """
    log.debug(type(fname))
    if isinstance(fname, str):
        try:
            return open(fname, mode)
        except IOError as err:
            message = "can't open '%s': %s"
            raise SystemExit(message % (fname, err))
    elif isinstance(fname, file_types):
        if fname.mode != mode:
            message = "mode mismatch: %s != %s"
            raise IOError(message % (fname.mode, mode))
        return fname
    else:
        message = "unknown data type (expected string or filehandle): %s"
        raise SystemExit(message % type(fname))


def readtxt(fname, path="", flat=False):
    """Commodity function for reading text files plain or zipped.

    Read a text file line by line either plainly from a directory or a .zip or
    .jar file. Return as a list of strings or optionally flattened into a
    single string.

    BEWARE: this is NOT intended for HUGE text files as it actually reads them
    in and returns the content, not a handle to the reader itself!

    Parameters
    ----------
    fname : str
        The name of the file to read in. Can be a full or relative path if
        desired. For automatic archive handling use the 'path' parameter.
    path : str (optional)
        The directory where to look for the file. If the string has the suffix
        '.zip' or '.jar' an archive is assumed and the corresponding mechanisms
        are used to read 'fname' from within this archive.
    flat : bool (optional)
        Used to request a flattened string instead of a list of strings.

    Returns
    -------
    txt : str or list(str)

    Example
    -------
    >>> readtxt('foo', '/tmp/archive.zip', flat=True)
    ... # doctest: +SKIP
    """
    zipread = None
    suffix = splitext(path)[1].lower()
    if (suffix == ".zip") or (suffix == ".jar"):
        # ZipFile only works as a context manager from Python 2.7 on
        # tag:python25
        zipread = zipfile.ZipFile(path, "r")
        fin = zipread.open(fname)
    else:
        fin = open(join(path, fname), "r")
    txt = fin.readlines()  # returns file as a list, one entry per line
    try:
        txt = [x.decode("utf-8") for x in txt]
    except AttributeError:
        pass  # in Python2 decoding isn't necessary
    if flat:
        txt = flatten(txt)
    fin.close()
    if zipread is not None:
        zipread.close()
    return txt
