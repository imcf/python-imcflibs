"""Functions for creating Z projections."""

from .bioformats import export_using_orig_name
from ..log import LOG as log

from ij.plugin import ZProjector


def average(imp):
    """Create an average intensity projection.

    Parameters
    ----------
    imp : ij.ImagePlus
        The input stack to be projected.

    Returns
    -------
    ij.ImagePlus
        The result of the projection.
    """
    log.debug("Creating average projection...")
    proj = ZProjector.run(imp, "avg")
    return proj


def maximum(imp):
    """Create a maximum intensity projection.

    Parameters
    ----------
    imp : ij.ImagePlus
        The input stack to be projected.

    Returns
    -------
    ij.ImagePlus
        The result of the projection.
    """
    log.debug("Creating maximum intensity projection...")
    proj = ZProjector.run(imp, "max")
    return proj


def create_and_save(imp, projections, path, filename, export_format):
    """Wrapper to create one or more projections and export the results.

    Parameters
    ----------
    imp : ij.ImagePlus
        The image stack to create the projections from.
    projections : list(str)
        A list of projection types to be done, valid options are 'Average',
        'Maximum' and 'Sum'.
    path : str
        The path to store the results in. Existing files will be overwritten.
    filename : str
        The original file name to derive the results name from.
    export_format : str
        The suffix to be given to Bio-Formats, determining the storage format.
    """
    command = {
        'Average': 'avg',
        'Maximum': 'max',
        'Sum': 'sum',
    }
    for projection in projections:
        log.debug("Creating '%s' projection...", projection)
        proj = ZProjector.run(imp, command[projection])
        export_using_orig_name(proj,
                               path, filename,
                               "-%s" % command[projection],
                               export_format,
                               overwrite=True)
        proj.close()
