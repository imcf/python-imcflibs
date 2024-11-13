"""Bio-Formats related helper functions.

NOTE: this is *NOT* about using [python-bioformats][1] but rather about calling
the corresponding functions provided by ImageJ.

[1]: https://pypi.org/project/python-bioformats/

"""

# Mosts imports will fail with plain C-Python / pylint:
# pylint: disable-msg=import-error

import os

from ij import IJ

from ._loci import BF, ImageReader, ImporterOptions, DynamicMetadataOptions, Memoizer, ZeissCZIReader

from ..pathtools import gen_name_from_orig
from ..log import LOG as log


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
    """Simple wrapper to export an image to a given file.

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


def get_series_count_from_ome_metadata(path_to_file):
    """Get the Bio-Formates series count from a file on disk.

    Useful to access a specific image in a container format like .czi, .nd2, .lif...

    Parameters
    ----------
    path_to_file : str
        The full path to the image file.

    Returns
    -------
    int
        The number of Bio-Formats series detected in the image file metadata.
    """
    reader = ImageReader()
    ome_meta = MetadataTools.createOMEXMLMetadata()
    reader.setMetadataStore(ome_meta)
    reader.setId(path_to_file)
    series_count = reader.getSeriesCount()
    reader.close()

    return series_count


def write_bf_memoryfile(path_to_file):
    """Write a BF memo-file so subsequent access to the same file is faster.

    The Bio-Formats memo-file is written next to the image file (i.e. in the
    same folder as the given file).

    Parameters
    ----------
    string
        The full path to the image file.
    """
    reader = Memoizer(ImageReader())
    reader.setId(path_to_file)
    reader.close()
