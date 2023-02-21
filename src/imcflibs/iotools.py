"""I/O related functions."""

import glob
import zipfile

import os
from os.path import splitext, join

from .log import LOG as log
from .strtools import flatten


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
    if type(fname).__name__ == "str":
        try:
            return open(fname, mode)
        except IOError as err:
            message = "can't open '%s': %s"
            raise SystemExit(message % (fname, err))
    elif type(fname).__name__ == "file":
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
    if flat:
        txt = flatten(txt)
    fin.close()
    if zipread is not None:
        zipread.close()
    return txt


def list_dirs_containing_filetype(source, filetype):
    """List all directories (recursive) that contain files with the given suffix.

    Parameters
    ----------
    source : str
        Path to source dir.
    filetype : str
        Filetype (string pattern) that should be matched against filenames in
        the directories.

    Returns
    -------
    list(str)
        List of all dirs that contain files of the given filetype.
    """
    dirs_containing_filetype = []

    # walk recursively through all directories
    # list their paths and all files inside (=os.walk)
    for dirname, _, filenames in os.walk(source):
        # stop when encountering a directory that contains "filetype"
        # and store the directory path
        for filename in filenames:
            if filetype in filename:
                dirs_containing_filetype.append(dirname + "/")
                break

    return dirs_containing_filetype


def list_all_filenames(source, filetype):
    """Get a sorted list of all files of specified filetype in a given directory.

    Parameters
    ----------
    source : str
        Path to the directory to scan for desired files.
    filetype : str
        The file extension to look for.

    Returns
    -------
    list(str)
        List of all files with the given suffix in the source directory.
    """
    os.chdir(str(source))
    allimages = sorted(glob.glob("*" + filetype))  # sorted by name

    return allimages


def get_folder_size(source):
    """Get the total size of a given directory and its subdirectories.

    Parameters
    ----------
    source : str
        Directory for which the size should be determined.

    Returns
    -------
    int
        The total size of all files in the source dir and subdirs in bytes.
    """
    total_size = 0
    for dirpath, _, filenames in os.walk(source):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            # skip if it is symbolic link
            if not os.path.islink(fpath):
                total_size += os.path.getsize(fpath)

    return total_size
