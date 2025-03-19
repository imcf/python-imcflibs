"""Functions for creating projections."""

from ij.plugin import ZProjector  # pylint: disable-msg=E0401

from .bioformats import export_using_orig_name  # pylint: disable-msg=E0401
from ..log import LOG as log

from net.imagej.axis import Axes
from net.imagej.ops import Ops
from ij import ImagePlus, IJ
from net.imagej import Dataset


def average(imp):
    """Create an average intensity Z projection.

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

    log.debug("Creating average Z projection...")
    proj = ZProjector.run(imp, "avg")
    return proj


def maximum(imp):
    """Create a maximum intensity Z projection.

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

    log.debug("Creating maximum intensity Z projection...")
    proj = ZProjector.run(imp, "max")
    return proj


def create_and_save(imp, projections, path, filename, export_format):
    """Create one or more projections and export (save) them.

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


def project_stack(imp, projected_dimension, projection_type, ops, ds, cs):
    """Project along a defined axis using the given projection type.

    Parameters
    ----------
    imp : ImagePlus
        The input image to be projected.
    projected_dimension : str
        The dimension along which to project the data. Must be one of {"X", "Y", "Z",
        "TIME", "CHANNEL"}.
    projection_type : str
        The type of projection to perform. Must be one of {"Max", "Mean", "Median",
        "Min", "StdDev", "Sum"}.
    ops : OpService
        The service used to access image processing operations. Use e.g. from script
        parameter: `#@ OpService ops`
    ds : DatasetService
        The service used to create new datasets. Use e.g. from script parameter:
        `#@ DatasetService ds`
    cs : ConvertService
        The service used to convert between formats. Use e.g. from script parameter:
        `#@ ConvertService cs`

    Returns
    -------
    ImagePlus
        The resulting projected image as an ImagePlus object.

    Raises
    ------
    Exception
        If the specified dimension is not found or if the dimension has only one frame.
    """
    bit_depth = imp.getBitDepth()
    data = cs.convert(imp, Dataset)
    # Select which dimension to project
    dim = data.dimensionIndex(getattr(Axes, projected_dimension))
    if dim == -1:
        raise Exception("%s dimension not found." % projected_dimension)
    if data.dimension(dim) < 2:
        raise Exception("%s dimension has only one frame." % projected_dimension)

    # Write the output dimensions
    new_dimensions = [
        data.dimension(d) for d in range(0, data.numDimensions()) if d != dim
    ]

    # Create the output image
    projected = ops.create().img(new_dimensions)

    # Create the op and run it
    proj_op = ops.op(getattr(Ops.Stats, projection_type), data)
    ops.transform().project(projected, data, proj_op, dim)

    # Create the output Dataset and convert to ImagePlus
    output = ds.create(projected)
    output_imp = cs.convert(output, ImagePlus)
    output_imp = output_imp.duplicate()
    output_imp.setTitle("%s %s projection" % (projected_dimension, projection_type))
    IJ.run(output_imp, "Enhance Contrast", "saturated=0.35")

    # Rescale bit depth if possible
    if projection_type in ["Max", "Min", "Median"]:
        IJ.run("Conversions...", " ")
        if bit_depth in [8, 16]:
            IJ.run(output_imp, str(bit_depth) + "-bit", "")
        if bit_depth == 12:
            IJ.run(output_imp, "16-bit", "")

        IJ.run("Conversions...", "scale")

    return output_imp
