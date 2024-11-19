"""Helper functions to work with filenames, directories etc."""

import os.path
import platform
from os import sep
import re

from . import strtools
from .log import LOG as log


def parse_path(path, prefix=""):
    """Parse a path into its components.

    If the path doesn't end with the pathsep, it is assumed being a file!
    No tests based on existing files are done, as this is supposed to also work
    on path strings that don't exist on the system running this code.

    The function accepts `java.io.File` objects (as retrieved by using ImageJ2's
    *Script Parameter* `#@ File`) for either of the parameters, so it is safe to
    use this in ImageJ Python scripts without additional measures.

    Parameters
    ----------
    path : str or str-like
        The path to be parsed into components.
    prefix : str or str-like, optional
        An optional path component that will be prefixed to the given path using
        `os.path.join()`.

    Returns
    -------
    dict
        The parsed (and possibly combined) path split into its components, with
        the following keys:
        - `orig` : The full string as passed into this function (possibly
          combined with the prefix in case one was specified).
        - `full` : The same as `orig` with separators adjusted to the current
          platform.
        - `parent` : The parent folder of the selected file.
        - `path` : The same as `full`, up to (including) the last separator.
        - `dname` : The segment between the last two separators (directory).
        - `fname` : The segment after the last separator (filename).
        - `basename` : The filename without extension. Note that *OME-TIFF*
          files (having a suffix like `.ome.tif` or `.ome.tiff`) are treated as
          special case in the sense that the `.ome` part is also stripped from
          the basename and added to the `ext` key (see below).
        - `ext` : The filename extension, containing max 1 dot (included) with
          the special case of `.ome.tif` / `.ome.tiff` where 2 dots are
          contained to represent the full suffix.

    Examples
    --------

    POSIX-style path to a file with a suffix:

    >>> parse_path('/tmp/foo/file.suffix')
    {'dname': 'foo',
     'ext': '',
     'fname': 'file',
     'full': '/tmp/foo/file',
     'basename': 'file',
     'orig': '/tmp/foo/file',
     'parent': '/tmp/',
     'path': '/tmp/foo/'}

    POSIX-style path to a directory:

    >>> parse_path('/tmp/foo/')
    {'dname': 'foo',
     'ext': '',
     'fname': '',
     'full': '/tmp/foo/',
     'basename': '',
     'orig': '/tmp/foo/',
     'parent': '/tmp/',
     'path': '/tmp/foo/'}

    Windows-style path to a file:

    >>> parse_path('C:\\Temp\\foo\\file.ext')
    {'dname': 'foo',
     'ext': '.ext',
     'fname': 'file.ext',
     'full': 'C:/Temp/foo/file.ext',
     'basename': 'file',
     'orig': 'C:\\Temp\\foo\\file.ext',
     'parent': 'C:/Temp/',
     'path': 'C:/Temp/foo/'}

    Special treatment for *OME-TIFF* suffixes:

    >>> parse_path("/path/to/some/nice.OME.tIf")
    {'basename': 'nice',
    'dname': 'some',
    'ext': '.OME.tIf',
    'fname': 'nice.OME.tIf',
    'full': '/path/to/some/nice.OME.tIf',
    'orig': '/path/to/some/nice.OME.tIf',
    'parent': '/path/to/',
    'path': '/path/to/some/'}
    """
    path = str(path)
    if prefix:
        # remove leading slash, otherwise join() will discard the first path:
        if path.startswith("/"):
            path = path[1:]
        path = os.path.join(str(prefix), path)
    parsed = {}
    parsed["orig"] = path
    path = path.replace("\\", sep)
    parsed["full"] = path
    folder = os.path.dirname(path)
    parsed["path"] = folder + sep
    parsed["parent"] = os.path.dirname(folder)
    parsed["fname"] = os.path.basename(path)
    parsed["dname"] = os.path.basename(os.path.dirname(parsed["path"]))
    base, ext = os.path.splitext(parsed["fname"])
    parsed["ext"] = ext
    parsed["basename"] = base
    if base.lower().endswith(".ome") and ext.lower().startswith(".tif"):
        parsed["basename"] = base[:-4]
        parsed["ext"] = base[-4:] + ext

    return parsed


def join2(path1, path2):
    """Join two paths into one, much like os.path.join().

    The main difference is that `join2()` takes exactly two arguments, but they
    can be non-str (as long as they're having a `__str__()` method), so this is
    safe to be used with stuff like `java.io.File` objects as retrieved when
    using ImageJ2's *Script Parameter* `#@ File`.

    In addition some sanitizing is done, e.g. in case one of the components is
    containing double backslashes (`\\`), they will be replaced by the current
    OS's path separator.

    Parameters
    ----------
    path1 : str or str-like
        The first component of the path to be joined.
    path2 : str or str-like
        The second component of the path to be joined.

    Returns
    -------
    str
    """
    return parse_path(path2, prefix=path1)["full"]


def jython_fiji_exists(path):
    """Wrapper to work around problems with Jython 2.7 in Fiji.

    In current Fiji, the Jython implementation of os.path.exists(path) raises a
    java.lang.AbstractMethodError iff 'path' doesn't exist. This function
    catches the exception to allow normal usage of the exists() call.
    """
    try:
        return os.path.exists(path)
    except java.lang.AbstractMethodError:
        return False


def listdir_matching(path, suffix, fullpath=False, sort=False, regex=False):
    """Get a list of files in a directory matching a given suffix.

    Parameters
    ----------
    path : str
        The directory to scan for files.
    suffix : str
        The suffix to match filenames against.
    fullpath : bool, optional
        If set to True, the list returned by the function will contain the full
        paths to the matching files (the default is False, which will result in
        the file names only, without path).
    sort : bool, optional
        If set to True, the returned list will be sorted using
        `imcflibs.strtools.sort_alphanumerically()`.
    regex : bool, optional
        If set to True, uses the suffix-string as regular expression to match
        filenames. By default False.

    Returns
    -------
    list
        All file names in the directory matching the suffix (without path!).
    """
    matching_files = list()
    for candidate in os.listdir(path):
        if not regex and candidate.lower().endswith(suffix.lower()):
            # log.debug("Found file %s", candidate)
            if fullpath:
                matching_files.append(os.path.join(path, candidate))
            else:
                matching_files.append(candidate)
        if regex and re.match(suffix.lower(), candidate.lower()):
            if fullpath:
                matching_files.append(os.path.join(path, candidate))
            else:
                matching_files.append(candidate)

    if sort:
        matching_files = strtools.sort_alphanumerically(matching_files)

    return matching_files


def image_basename(orig_name):
    """Return the file name component without suffix(es).

    Strip away the path and suffix of a given file name, doing a special
    treatment for the composite suffix ".ome.tif(f)" which will be fully
    stripped as well.

    Parameters
    ----------
    orig_name : str

    Examples
    --------
    >>> image_basename('/path/to/some_funny_image_file_01.png')
    'some_funny_image_file_01'

    >>> image_basename('some-more-complex-stack.ome.tif')
    'some-more-complex-stack'

    >>> image_basename('/tmp/FoObAr.OMe.tIf')
    'FoObAr'
    """
    return parse_path(orig_name)["basename"]


def gen_name_from_orig(path, orig_name, tag, suffix):
    """Derive a file name from a given input file, an optional tag and a suffix.

    Parameters
    ----------
    path : str or object that can be cast to a str
        The output path.
    orig_name : str or object that can be cast to a str
        The input file name, may contain arbitrary path components.
    tag : str
        An optional tag to be added at the end of the new file name, can be used
        to denote information like "-avg" for an average projection image.
    suffix : str
        The new file name suffix, which also sets the file format for BF.

    Returns
    -------
    out_file : str
        The newly generated file name with its full path.
    """
    name = os.path.join(path, image_basename(orig_name) + tag + suffix)
    return name


def derive_out_dir(in_dir, out_dir):
    """Derive `out_dir` from its own value and the value of `in_dir`.

    In case the supplied value of `out_dir` is one of '-' or 'NONE', the
    returned value will be set to `in_dir`. Otherwise the value of `out_dir`
    will be returned unchanged.

    Parameters
    ----------
    in_dir : str
        The full path to the input directory.
    out_dir : str
        Either the full path to an output directory or one of '-' or 'NONE'.

    Returns
    -------
    str
        The full path to the directory to be used for output and temp files.
    """
    if out_dir.upper() in ["-", "NONE"]:
        out_dir = in_dir
        log.info("No output directory given, using input dir [%s].", out_dir)
    else:
        log.info("Using directory [%s] for results and temp files.", out_dir)

    return out_dir


def find_dirs_containing_filetype(source, filetype):
    """Recursively list directories containing files with a given suffix.

    Parameters
    ----------
    source : str
        Path to base directory to start recursive search in.
    filetype : str
        Filetype (string pattern) that should be matched against filenames in
        the directories.

    Returns
    -------
    list(str)
        List of all dirs that contain files with the given suffix / filetype.
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


def folder_size(source):
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


def create_directory(new_path):
    """create a new directory if it does not already exist

    Parameters
    ----------
    new_path : str
        Path to the new directory
    """
    if not os.path.exists(new_path):
        os.makedirs(new_path)


# pylint: disable-msg=C0103
#   we use the variable name 'exists' in its common spelling (lowercase), so
#   removing this workaround will be straightforward at a later point
if platform.python_implementation() == "Jython":  # pragma: no cover
    # pylint: disable-msg=F0401
    #   java.lang is only importable within Jython, pylint would complain
    import java.lang

    exists = jython_fiji_exists
else:
    exists = os.path.exists
