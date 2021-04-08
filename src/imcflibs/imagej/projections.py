"""Functions for creating Z projections."""

from ij.plugin import ZProjector  # pylint: disable-msg=E0401

from .bioformats import export_using_orig_name  # pylint: disable-msg=E0401
from ..log import LOG as log


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
    if imp.getDimensions()[3] < 2:
        log.warn("ImagePlus is not a z-stack, not creating a projection!")
        return imp

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
    if imp.getDimensions()[3] < 2:
        log.warn("ImagePlus is not a z-stack, not creating a projection!")
        return imp

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

    Returns
    -------
    bool
        True in case projections were created, False otherwise (e.g. if the
        given ImagePlus is not a Z-stack).
    """
    if not projections:
        log.debug("No projection type requested, skipping...")
        return False

    if imp.getDimensions()[3] < 2:
        log.error("ImagePlus is not a z-stack, not creating any projections!")
        return False

    command = {
        "Average": "avg",
        "Maximum": "max",
        "Sum": "sum",
    }
    for projection in projections:
        log.debug("Creating '%s' projection...", projection)
        proj = ZProjector.run(imp, command[projection])
        export_using_orig_name(
            proj,
            path,
            filename,
            "-%s" % command[projection],
            export_format,
            overwrite=True,
        )
        proj.close()

    return True
