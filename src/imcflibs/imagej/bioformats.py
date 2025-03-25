"""Bio-Formats related helper functions.

NOTE: this is *NOT* about using [python-bioformats][1] but rather about calling
the corresponding functions provided by ImageJ.

[1]: https://pypi.org/project/python-bioformats/

"""

# Mosts imports will fail with plain C-Python / pylint:
# pylint: disable-msg=import-error

import os

from ij import IJ

from ..log import LOG as log
from ..pathtools import gen_name_from_orig
from ._loci import (
    BF,
    DynamicMetadataOptions,
    ImageReader,
    ImporterOptions,
    Memoizer,
    MetadataTools,
    ZeissCZIReader,
)


def import_image(
    filename,
    color_mode="color",
    split_c=False,
    split_z=False,
    split_t=False,
    series_number=None,
    c_start=None,
    c_end=None,
    c_interval=None,
    z_start=None,
    z_end=None,
    z_interval=None,
    t_start=None,
    t_end=None,
    t_interval=None,
):
    """Open an image file using the Bio-Formats importer.

    Parameters
    ----------
    filename : str
        The full path to the file to be imported through Bio-Formats.
    color_mode : str, optional
        The color mode to be used for the resulting ImagePlus, one of 'color',
        'composite', 'gray' and 'default'.
    split_c : bool, optional
        Whether to split the channels into separate ImagePlus objects.
    split_z : bool, optional
        Whether to split the z-slices into separate ImagePlus objects.
    split_t : bool, optional
        Whether to split the time points into separate ImagePlus objects.
    series_number : int, optional
        open a specific Bio-Formats series
    c_start : int, optional
        only import a subset of channel starting with this one. Requires to set
        c_end and c_interval.
    c_end : int, optional
        only import channel(s) ending with this one. Requires to set c_start and
        c_interval.
    c_interval : int, optional
        only import a subset of channel with this interval. Requires to set
        c_start and c_end.
    z_start : int, optional
        only import a subset of planes starting with this one. Requires to set
        z_end and z_interval.
    z_end : int, optional
        only import a subset of planes ending with this one. Requires to set
        z_start and z_interval.
    z_interval : int, optional
        only import a subset of planes with this interval. Requires to set
        z_start and z_end.
    t_start : int, optional
        only import a subset of time points starting with this one. Requires to
        set t_end and t_interval.
    t_end : int, optional
        only import a subset of time points ending with this one. Requires to
        set t_start and t_interval.
    t_interval : int, optional
        only import a subset of time points with thsi interval. Requires to set
        t_start and t_end.

    Returns
    -------
    list(ij.ImagePlus)
        A list of ImagePlus objects resulting from the import.
    """
    options = ImporterOptions()
    mode = {
        "color": ImporterOptions.COLOR_MODE_COLORIZED,
        "composite": ImporterOptions.COLOR_MODE_COMPOSITE,
        "gray": ImporterOptions.COLOR_MODE_GRAYSCALE,
        "default": ImporterOptions.COLOR_MODE_DEFAULT,
    }
    options.setColorMode(mode[color_mode])
    options.setSplitChannels(split_c)
    options.setSplitFocalPlanes(split_z)
    options.setSplitTimepoints(split_t)
    options.setId(filename)
    if series_number is not None:
        options.setSeriesOn(series_number, True)

    if c_start is not None:
        if series_number is None:
            series_number = 0
        options.setSpecifyRanges(True)
        options.setCBegin(series_number, c_start)
        options.setCEnd(series_number, c_end)
        options.setCStep(series_number, c_interval)

    if z_start is not None:
        if series_number is None:
            series_number = 0
        options.setSpecifyRanges(True)
        options.setZBegin(series_number, z_start)
        options.setZEnd(series_number, z_end)
        options.setZStep(series_number, z_interval)

    if t_start is not None:
        if series_number is None:
            series_number = 0
        options.setSpecifyRanges(True)
        options.setTBegin(series_number, t_start)
        options.setTEnd(series_number, t_end)
        options.setTStep(series_number, t_interval)

    log.info("Reading [%s]", filename)
    orig_imps = BF.openImagePlus(options)
    log.debug("Opened [%s] %s", filename, type(orig_imps))
    return orig_imps


def export(imp, filename, overwrite=False):
    """Export an ImagePlus object to a given file.

    Parameters
    ----------
    imp : ij.ImagePlus
        The ImagePlus object to be exported by Bio-Formats.
    filename : str
        The output filename, may include a full path.
    overwrite : bool
        A switch to indicate existing files should be overwritten. Default is to
        keep existing files, in this case an IOError is raised.
    """
    log.info("Exporting to [%s]", filename)
    suffix = filename[-3:].lower()
    try:
        unit = imp.calibration.unit
        log.debug("Detected calibration unit: %s", unit)
    except Exception as err:
        log.error("Unable to detect spatial unit: %s", err)
        raise RuntimeError("Error detecting image calibration: %s" % err)
    if unit == "pixel" and (suffix == "ics" or suffix == "ids"):
        log.warn(
            "Forcing unit to be 'm' instead of 'pixel' to avoid "
            "Bio-Formats 6.0.x Exporter bug!"
        )
        imp.calibration.unit = "m"
    if os.path.exists(filename):
        if not overwrite:
            raise IOError("file [%s] already exists!" % filename)
        log.debug("Removing existing file [%s]...", filename)
        os.remove(filename)

    IJ.run(imp, "Bio-Formats Exporter", "save=[" + filename + "]")
    log.debug("Exporting finished.")


def export_using_orig_name(imp, path, orig_name, tag, suffix, overwrite=False):
    """Export an image to a given path, deriving the name from the input file.

    The input filename is stripped to its pure file name, without any path or
    suffix components, then an optional tag (e.g. "-avg") and the new format
    suffix is added.

    Parameters
    ----------
    imp : ij.ImagePlus
        The ImagePlus object to be exported by Bio-Formats.
    path : str or object that can be cast to a str
        The output path.
    orig_name : str or object that can be cast to a str
        The input file name, may contain arbitrary path components.
    tag : str
        An optional tag to be added at the end of the new file name, can be used
        to denote information like "-avg" for an average projection image.
    suffix : str
        The new file name suffix, which also sets the file format for BF.
    overwrite : bool
        A switch to indicate existing files should be overwritten.

    Returns
    -------
    str
        The full name of the exported file.
    """
    out_file = gen_name_from_orig(path, orig_name, tag, suffix)
    export(imp, out_file, overwrite)
    return out_file


def get_series_info_from_ome_metadata(path_to_file, skip_labels=False):
    """Get the Bio-Formats series information from a file on disk.

    Useful to access specific images in container formats like .czi, .nd2, .lif...

    Parameters
    ----------
    path_to_file : str
        The full path to the image file.
    skip_labels : bool, optional
        If True, excludes label and macro images from the series count (default: False).

    Returns
    -------
    tuple
        A tuple containing:
        - int: The number of Bio-Formats series detected (excluding labels if skip_labels=True)
        - list or range: Series indices. If skip_labels=True, returns filtered list of indices,
          otherwise returns range(series_count)

    Examples
    --------
    >>> count, indices = get_series_info_from_ome_metadata("image.czi")
    >>> count, indices = get_series_info_from_ome_metadata("image.nd2", skip_labels=True)
    """

    if not skip_labels:
        reader = ImageReader()
        reader.setFlattenedResolutions(False)
        ome_meta = MetadataTools.createOMEXMLMetadata()
        reader.setMetadataStore(ome_meta)
        reader.setId(path_to_file)
        series_count = reader.getSeriesCount()

        reader.close()
        return series_count, range(series_count)

    else:
        reader = ImageReader()
        # reader.setFlattenedResolutions(True)
        ome_meta = MetadataTools.createOMEXMLMetadata()
        reader.setMetadataStore(ome_meta)
        reader.setId(path_to_file)
        series_count = reader.getSeriesCount()

        series_ids = []
        series_names = []
        x = 0
        y = 0
        for i in range(series_count):
            reader.setSeries(i)

            if reader.getSizeX() > x and reader.getSizeY() > y:
                name = ome_meta.getImageName(i)

                if name not in ["label image", "macro image"]:
                    series_ids.append(i)
                    series_names.append(name)

            x = reader.getSizeX()
            y = reader.getSizeY()

        print(series_names)
        return len(series_ids), series_ids


def write_bf_memoryfile(path_to_file):
    """Write a BF memo-file so subsequent access to the same file is faster.

    The Bio-Formats memo-file is written next to the image file (i.e. in the
    same folder as the given file).

    Parameters
    ----------
    path_to_file : str
        The full path to the image file.
    """
    reader = Memoizer(ImageReader())
    reader.setId(path_to_file)
    reader.close()


def get_metadata_from_file(path_to_image):
    """Extract metadata from an image file using Bio-Formats.

    This function reads an image file using the Bio-Formats library and extracts
    various metadata properties including physical dimensions, pixel dimensions,
    and other image characteristics.

    Parameters
    ----------
    path_to_image : str or pathlib.Path
        Path to the image file from which metadata should be extracted.

    Returns
    -------
    dict
        A dictionary containing the following metadata:

            {
                unit_width : float,  # physical width of a pixel
                unit_height : float,  # physical height of a pixel
                unit_depth : float,  # physical depth of a voxel
                pixel_width : int,  # width of the image in pixels
                pixel_height : int,  # height of the image in pixels
                slice_count : int,  # number of Z-slices
                channel_count : int,  # number of channels
                timepoints_count : int,  # number of timepoints
                dimension_order : str,  # order of dimensions, e.g. "XYZCT"
                pixel_type : str,  # data type of the pixel values
            }
    """
    reader = ImageReader()
    ome_meta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(ome_meta)
    reader.setId(str(path_to_image))

    phys_size_x = ome_meta.getPixelsPhysicalSizeX(0)
    phys_size_y = ome_meta.getPixelsPhysicalSizeY(0)
    phys_size_z = ome_meta.getPixelsPhysicalSizeZ(0)
    pixel_size_x = ome_meta.getPixelsSizeX(0)
    pixel_size_y = ome_meta.getPixelsSizeY(0)
    pixel_size_z = ome_meta.getPixelsSizeZ(0)
    channel_count = ome_meta.getPixelsSizeC(0)
    timepoints_count = ome_meta.getPixelsSizeT(0)
    dimension_order = ome_meta.getPixelsDimensionOrder(0)
    pixel_type = ome_meta.getPixelsType(0)

    image_calibration = {
        "unit_width": phys_size_x.value(),
        "unit_height": phys_size_y.value(),
        "unit_depth": phys_size_z.value(),
        "pixel_width": pixel_size_x.getNumberValue(),
        "pixel_height": pixel_size_y.getNumberValue(),
        "slice_count": pixel_size_z.getNumberValue(),
        "channel_count": channel_count.getNumberValue(),
        "timepoints_count": timepoints_count.getNumberValue(),
        "dimension_order": dimension_order,
        "pixel_type": pixel_type,
    }

    reader.close()

    return image_calibration


def get_stage_coords(source, filenames):
    """Get stage coordinates and calibration for a given list of images.

    Parameters
    ----------
    source : str
        Path to the images.
    filenames : list of str
        List of images filenames.

    Returns
    -------
    dict

        {
            dimensions : int,  # number of dimensions (2D or 3D)
            stage_coordinates_x : list,  # absolute stage x-coordinated
            stage_coordinates_y : list,  # absolute stage y-coordinated
            stage_coordinates_z : list,  # absolute stage z-coordinated
            relative_coordinates_x : list,  # relative stage x-coordinates in px
            relative_coordinates_y : list,  # relative stage y-coordinates in px
            relative_coordinates_z : list,  # relative stage z-coordinates in px
            image_calibration : list,  # x,y,z image calibration in unit/px
            calibration_unit : str,  # image calibration unit
            image_dimensions_czt : list,  # number of images in dimensions c,z,t
            series_names : list of str,  # names of all series in the files
            max_size : list of int,  # max size (x/y/z) across all files
        }
    """

    # open an array to store the abosolute stage coordinates from metadata
    stage_coordinates_x = []
    stage_coordinates_y = []
    stage_coordinates_z = []
    series_names = []

    for counter, image in enumerate(filenames):
        # parse metadata
        reader = ImageReader()
        reader.setFlattenedResolutions(False)
        omeMeta = MetadataTools.createOMEXMLMetadata()
        reader.setMetadataStore(omeMeta)
        reader.setId(source + str(image))
        series_count = reader.getSeriesCount()

        # get hyperstack dimensions from the first image
        if counter == 0:
            frame_size_x = reader.getSizeX()
            frame_size_y = reader.getSizeY()
            frame_size_z = reader.getSizeZ()
            frame_size_c = reader.getSizeC()
            frame_size_t = reader.getSizeT()

            # note the dimensions
            if frame_size_z == 1:
                dimensions = 2
            if frame_size_z > 1:
                dimensions = 3

            # get the physical calibration for the first image series
            physSizeX = omeMeta.getPixelsPhysicalSizeX(0)
            physSizeY = omeMeta.getPixelsPhysicalSizeY(0)
            physSizeZ = omeMeta.getPixelsPhysicalSizeZ(0)

            # workaround to get the z-interval if physSizeZ.value() returns None.
            z_interval = 1
            if physSizeZ is not None:
                z_interval = physSizeZ.value()

            if frame_size_z > 1 and physSizeZ is None:
                log.debug("no z calibration found, trying to recover")
                first_plane = omeMeta.getPlanePositionZ(0, 0)
                next_plane_imagenumber = frame_size_c + frame_size_t - 1
                second_plane = omeMeta.getPlanePositionZ(0, next_plane_imagenumber)
                z_interval = abs(abs(first_plane.value()) - abs(second_plane.value()))
                log.debug("z-interval seems to be: " + str(z_interval))

            # create an image calibration
            image_calibration = [
                physSizeX.value(),
                physSizeY.value(),
                z_interval,
            ]
            calibration_unit = physSizeX.unit().getSymbol()
            image_dimensions_czt = [
                frame_size_c,
                frame_size_z,
                frame_size_t,
            ]

        reader.close()

        for series in range(series_count):
            if omeMeta.getImageName(series) == "macro image":
                continue

            if series_count > 1 and not str(image).endswith(".vsi"):
                series_names.append(omeMeta.getImageName(series))
            else:
                series_names.append(str(image))
            # get the plane position in calibrated units
            current_position_x = omeMeta.getPlanePositionX(series, 0)
            current_position_y = omeMeta.getPlanePositionY(series, 0)
            current_position_z = omeMeta.getPlanePositionZ(series, 0)

            physSizeX_max = (
                physSizeX.value()
                if physSizeX.value() >= omeMeta.getPixelsPhysicalSizeX(series).value()
                else omeMeta.getPixelsPhysicalSizeX(series).value()
            )
            physSizeY_max = (
                physSizeY.value()
                if physSizeY.value() >= omeMeta.getPixelsPhysicalSizeY(series).value()
                else omeMeta.getPixelsPhysicalSizeY(series).value()
            )
            if omeMeta.getPixelsPhysicalSizeZ(series):
                physSizeZ_max = (
                    physSizeZ.value()
                    if physSizeZ.value()
                    >= omeMeta.getPixelsPhysicalSizeZ(series).value()
                    else omeMeta.getPixelsPhysicalSizeZ(series).value()
                )

            else:
                physSizeZ_max = 1.0

            # get the absolute stage positions and store them
            pos_x = current_position_x.value()
            pos_y = current_position_y.value()

            if current_position_z is None:
                log.debug("the z-position is missing in the ome-xml metadata.")
                pos_z = 1.0
            else:
                pos_z = current_position_z.value()

            stage_coordinates_x.append(pos_x)
            stage_coordinates_y.append(pos_y)
            stage_coordinates_z.append(pos_z)

    max_size = [physSizeX_max, physSizeY_max, physSizeZ_max]

    # calculate the store the relative stage movements in px (for the grid/collection stitcher)
    relative_coordinates_x_px = []
    relative_coordinates_y_px = []
    relative_coordinates_z_px = []

    for i in range(len(stage_coordinates_x)):
        rel_pos_x = (
            stage_coordinates_x[i] - stage_coordinates_x[0]
        ) / physSizeX.value()
        rel_pos_y = (
            stage_coordinates_y[i] - stage_coordinates_y[0]
        ) / physSizeY.value()
        rel_pos_z = (stage_coordinates_z[i] - stage_coordinates_z[0]) / z_interval

        relative_coordinates_x_px.append(rel_pos_x)
        relative_coordinates_y_px.append(rel_pos_y)
        relative_coordinates_z_px.append(rel_pos_z)

    return {
        "dimensions": dimensions,
        "stage_coordinates_x": stage_coordinates_x,
        "stage_coordinates_y": stage_coordinates_y,
        "stage_coordinates_z": stage_coordinates_z,
        "relative_coordinates_x": relative_coordinates_x_px,
        "relative_coordinates_y": relative_coordinates_y_px,
        "relative_coordinates_z": relative_coordinates_z_px,
        "image_calibration": image_calibration,
        "calibration_unit": calibration_unit,
        "image_dimensions_czt": image_dimensions_czt,
        "series_names": series_names,
        "max_size": max_size,
    }
