"""Helper functions to work with filenames."""

import platform
from os import sep
import os.path

from .log import LOG as log


def parse_path(path):
    """Parse a path into its components.

    If the path doesn't end with the pathsep, it is assumed being a file!
    No tests based on existing files are done, as this is supposed to also work
    on path strings that don't exist on the system running this code.

    Returns
    -------
    parsed = {
        'orig' : str   # string as passed into this function
        'full' : str   # separators adjusted to current platform
        'path' : str   # like previous, up to (including) the last separator
        'dname' : str  # segment between the last two separators (directory)
        'fname' : str  # segment after the last separator (filename)
        'ext' : str    # filename extension, containing max 1 dot (included)
    }

    Example
    -------

    >>> path_to_file = parse_path('/tmp/foo/file')
    >>> path_to_dir = parse_path('/tmp/foo/')

    orig : The full path string as given to this function.
    full : Backslashes replaced by the current separator.

    path : 'full' up to the last separator (included)
    >>> path_to_file['path']
    '/tmp/foo/'
    >>> path_to_dir['path']
    '/tmp/foo/'

    dname : The last directory of the path in 'full'.
    >>> path_to_file['dname']
    'foo'
    >>> path_to_dir['dname']
    'foo'

    fname : The filename of 'full', empty in case of a directory.
    >>> path_to_file['fname']
    'file'
    >>> path_to_dir['fname']
    ''
    """
    parsed = {}
    parsed['orig'] = path
    path = path.replace('\\', sep)
    parsed['full'] = path
    parsed['path'] = os.path.dirname(path) + sep
    parsed['fname'] = os.path.basename(path)
    parsed['dname'] = os.path.basename(os.path.dirname(parsed['path']))
    parsed['ext'] = os.path.splitext(parsed['fname'])[1]
    return parsed


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


def listdir_matching(path, suffix):
    """Get a list of files in a directory matching a given suffix.

    Parameters
    ----------
    path : str
        The directory to scan for files.
    suffix : str
        The suffix to match filenames against.

    Returns
    -------
    list
        All file names in the directory matching the suffix (without path!).
    """
    matching_files = list()
    for candidate in os.listdir(path):
        if candidate.lower().endswith(suffix.lower()):
            # log.debug("Found file %s", candidate)
            matching_files.append(candidate)

    return matching_files


def image_basename(orig_name):
    """Return the file name component without suffix(es).

    Strip away the path and suffix of a given file name, doing a special
    treatment for the composite suffix ".ome.tif(f)" which will be fully
    stripped as well.

    Parameters
    ----------
    orig_name : str

    Example
    -------
    >>> image_basename('/path/to/some_funny_image_file_01.png')
    'some_funny_image_file_01'

    >>> image_basename('some-more-complex-stack.ome.tif')
    'some-more-complex-stack'

    >>> image_basename('/tmp/FoObAr.OMe.tIf')
    'FoObAr'
    """
    base = os.path.splitext(os.path.basename(orig_name))[0]
    if base.lower().endswith('.ome'):
        base = base[:-4]
    return base


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


# pylint: disable-msg=C0103
#   we use the variable name 'exists' in its common spelling (lowercase), so
#   removing this workaround will be straightforward at a later point
if platform.python_implementation() == 'Jython':
    # pylint: disable-msg=F0401
    #   java.lang is only importable within Jython, pylint would complain
    import java.lang
    exists = jython_fiji_exists
else:
    exists = os.path.exists
