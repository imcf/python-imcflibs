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


class ImageMetadata(object):
    """A class to store metadata information from an image.

    This class stores metadata information extracted from an image file, such as image dimensions,
    pixel dimensions, and calibration units. It provides a method to convert the attributes to a
    dictionary and a string representation of the object.

    Attributes
    ----------
    unit_width : float or None
        Physical width of a pixel in the given unit.
    unit_height : float or None
        Physical height of a pixel in the given unit.
    unit_depth : float or None
        Physical depth of a voxel in the given unit.
    pixel_width : int or None
        Width of the image in pixels.
    pixel_height : int or None
        Height of the image in pixels.
    slice_count : int or None
        Number of Z-slices in the image.
    channel_count : int or None
        Number of channels in the image.
    timepoints_count : int or None
        Number of timepoints in the image.
    dimension_order : str or None
        Order of dimensions (e.g., "XYZCT").
    pixel_type : str or None
        Data type of the pixel values (e.g., "uint16").

    Examples
    --------
    >>> metadata = ImageMetadata(
    ...     unit_width=0.1,
    ...     unit_height=0.1
    ...     )
    >>> print(metadata)
    <ImageMetadata(unit_width=0.1, unit_height=0.1, ...)>
    """

    def __init__(
        self,
        unit_width=None,
        unit_height=None,
        unit_depth=None,
        unit=None,
        pixel_width=None,
        pixel_height=None,
        slice_count=None,
        channel_count=None,
        timepoints_count=None,
        dimension_order=None,
        pixel_type=None,
    ):
        self.unit_width = unit_width
        self.unit_height = unit_height
        self.unit_depth = unit_depth
        self.unit = unit
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.slice_count = slice_count
        self.channel_count = channel_count
        self.timepoints_count = timepoints_count
        self.dimension_order = dimension_order
        self.pixel_type = pixel_type

    def to_dict(self):
        """Convert the object attributes to a dictionary.

        Returns
        -------
        dict
            A dictionary representation of the object attributes.
        """
        return self.__dict__


class StageMetadata(object):
    """A class to store stage coordinates and calibration metadata for a set of images.

    Attributes
    ----------
    dimensions : int
        Number of dimensions (2D or 3D).
    stage_coordinates_x : list of float
        Absolute stage x-coordinates.
    stage_coordinates_y : list of float
        Absolute stage y-coordinates.
    stage_coordinates_z : list of float
        Absolute stage z-coordinates.
    relative_coordinates_x : list of float
        Relative stage x-coordinates in pixels.
    relative_coordinates_y : list of float
        Relative stage y-coordinates in pixels.
    relative_coordinates_z : list of float
        Relative stage z-coordinates in pixels.
    image_calibration : list of float
        Calibration values for x, y, and z in unit/px.
    calibration_unit : str
        Unit used for image calibration.
    image_dimensions_czt : list of int
        Number of images in dimensions (channels, z-slices, timepoints).
    series_names : list of str
        Names of all series in the image files.
    max_size : list of float
        Maximum physical size (x/y/z) across all files.
    """

    def __init__(
        self,
        dimensions=2,
        stage_coordinates_x=None,
        stage_coordinates_y=None,
        stage_coordinates_z=None,
        relative_coordinates_x=None,
        relative_coordinates_y=None,
        relative_coordinates_z=None,
        image_calibration=None,
        calibration_unit="unknown",
        image_dimensions_czt=None,
        series_names=None,
        max_size=None,
    ):
        self.dimensions = dimensions
        self.stage_coordinates_x = stage_coordinates_x or []
        self.stage_coordinates_y = stage_coordinates_y or []
        self.stage_coordinates_z = stage_coordinates_z or []
        self.relative_coordinates_x = relative_coordinates_x or []
        self.relative_coordinates_y = relative_coordinates_y or []
        self.relative_coordinates_z = relative_coordinates_z or []
        self.image_calibration = image_calibration or [1.0, 1.0, 1.0]
        self.calibration_unit = calibration_unit or "unknown"
        self.image_dimensions_czt = image_dimensions_czt or [1, 1, 1]
        self.series_names = series_names or []
        self.max_size = max_size or [1.0, 1.0, 1.0]

    def __repr__(self):
        """Return a string representation of the object."""
        return "<StageMetadata({})>".format(
            ", ".join("{}={}".format(k, v) for k, v in self.__dict__.items())
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
    ImageMetadata
        An instance of `imcflibs.imagej.bioformats.ImageMetadata` containing the extracted metadata.
    """

    reader = ImageReader()
    ome_meta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(ome_meta)
    reader.setId(str(path_to_image))

    metadata = ImageMetadata(
        unit_width=ome_meta.getPixelsPhysicalSizeX(0).value(),
        unit_height=ome_meta.getPixelsPhysicalSizeY(0).value(),
        unit_depth=ome_meta.getPixelsPhysicalSizeZ(0).value(),
        unit=ome_meta.getPixelsPhysicalSizeX(0).unit().symbol,
        pixel_width=ome_meta.getPixelsSizeX(0),
        pixel_height=ome_meta.getPixelsSizeY(0),
        slice_count=ome_meta.getPixelsSizeZ(0),
        channel_count=ome_meta.getPixelsSizeC(0),
        timepoints_count=ome_meta.getPixelsSizeT(0),
        dimension_order=ome_meta.getPixelsDimensionOrder(0),
        pixel_type=ome_meta.getPixelsType(0),
    )
    reader.close()

    return metadata


def get_stage_coords(filenames):
    """Get stage coordinates and calibration for a given list of images.

    Parameters
    ----------
    filenames : list of str
        List of image filepaths.

    Returns
    -------
    StageMetadata
        An object containing extracted stage metadata.
    """
    # Initialize lists to store stage coordinates and series names
    stage_coordinates_x = []
    stage_coordinates_y = []
    stage_coordinates_z = []
    series_names = []

    # Intiialize default values
    dimensions = 2
    image_calibration = []
    calibration_unit = "unknown"
    image_dimensions_czt = []
    max_size = []

    # Initialize max_size variables to track the maximums
    max_phys_size_x = 0.0
    max_phys_size_y = 0.0
    max_phys_size_z = 0.0

    for counter, image in enumerate(filenames):
        reader = ImageReader()
        reader.setFlattenedResolutions(False)
        ome_meta = MetadataTools.createOMEXMLMetadata()
        reader.setMetadataStore(ome_meta)
        reader.setId(str(image))
        series_count = reader.getSeriesCount()

        # Process only the first image to get values not dependent on series
        if counter == 0:
            frame_size_x = reader.getSizeX()
            frame_size_y = reader.getSizeY()
            frame_size_z = reader.getSizeZ()
            frame_size_c = reader.getSizeC()
            frame_size_t = reader.getSizeT()

            dimensions = 2 if frame_size_z == 1 else 3

            # Retrieve physical size coordinates safely
            phys_size_x = getattr(
                ome_meta.getPixelsPhysicalSizeX(0), "value", lambda: 1.0
            )()
            phys_size_y = getattr(
                ome_meta.getPixelsPhysicalSizeY(0), "value", lambda: 1.0
            )()
            phys_size_z = getattr(
                ome_meta.getPixelsPhysicalSizeZ(0), "value", lambda: None
            )()

            z_interval = phys_size_z if phys_size_z is not None else 1.0

            # Handle missing Z calibration
            if phys_size_z is None and frame_size_z > 1:
                first_plane = getattr(
                    ome_meta.getPlanePositionZ(0, 0), "value", lambda: 0
                )()
                next_plane_index = frame_size_c + frame_size_t - 1
                second_plane = getattr(
                    ome_meta.getPlanePositionZ(0, next_plane_index), "value", lambda: 0
                )()
                z_interval = abs(first_plane - second_plane)

            image_calibration = [phys_size_x, phys_size_y, z_interval]
            calibration_unit = (
                getattr(
                    ome_meta.getPixelsPhysicalSizeX(0).unit(),
                    "getSymbol",
                    lambda: "unknown",
                )()
                if phys_size_x
                else "unknown"
            )
            image_dimensions_czt = [frame_size_c, frame_size_z, frame_size_t]

        reader.close()

        for series in range(series_count):
            if ome_meta.getImageName(series) == "macro image":
                continue

            if series_count > 1 and not str(image).endswith(".vsi"):
                series_names.append(ome_meta.getImageName(series))
            else:
                series_names.append(str(image))

            current_position_x = getattr(
                ome_meta.getPlanePositionX(series, 0), "value", lambda: 0
            )()
            current_position_y = getattr(
                ome_meta.getPlanePositionY(series, 0), "value", lambda: 0
            )()
            current_position_z = getattr(
                ome_meta.getPlanePositionZ(series, 0), "value", lambda: 1.0
            )()

            max_phys_size_x = max(
                max_phys_size_x, ome_meta.getPixelsPhysicalSizeX(series).value()
            )
            max_phys_size_y = max(
                max_phys_size_y, ome_meta.getPixelsPhysicalSizeY(series).value()
            )
            max_phys_size_z = max(
                max_phys_size_z,
                ome_meta.getPixelsPhysicalSizeZ(series).value()
                if phys_size_z
                else z_interval,
            )

            stage_coordinates_x.append(current_position_x)
            stage_coordinates_y.append(current_position_y)
            stage_coordinates_z.append(current_position_z)

    max_size = [max_phys_size_x, max_phys_size_y, max_phys_size_z]

    relative_coordinates_x_px = [
        (stage_coordinates_x[i] - stage_coordinates_x[0]) / (phys_size_x or 1.0)
        for i in range(len(stage_coordinates_x))
    ]
    relative_coordinates_y_px = [
        (stage_coordinates_y[i] - stage_coordinates_y[0]) / (phys_size_y or 1.0)
        for i in range(len(stage_coordinates_y))
    ]
    relative_coordinates_z_px = [
        (stage_coordinates_z[i] - stage_coordinates_z[0]) / (z_interval or 1.0)
        for i in range(len(stage_coordinates_z))
    ]

    return StageMetadata(
        dimensions=dimensions,
        stage_coordinates_x=stage_coordinates_x,
        stage_coordinates_y=stage_coordinates_y,
        stage_coordinates_z=stage_coordinates_z,
        relative_coordinates_x=relative_coordinates_x_px,
        relative_coordinates_y=relative_coordinates_y_px,
        relative_coordinates_z=relative_coordinates_z_px,
        image_calibration=image_calibration,
        calibration_unit=calibration_unit,
        image_dimensions_czt=image_dimensions_czt,
        series_names=series_names,
        max_size=max_size,
    )
