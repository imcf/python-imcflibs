"""Bio-Formats related helper functions.

NOTE: this is *NOT* about using [python-bioformats][1] but rather about calling
the corresponding functions provided by ImageJ.

[1]: https://pypi.org/project/python-bioformats/

"""

import os

from ij import IJ
from loci.plugins import BF
from loci.plugins.in import ImporterOptions

from ..pathtools import gen_name_from_orig
from ..log import LOG as log


def import_image(filename,
                 color_mode='color',
                 split_c=False, split_z=False, split_t=False):
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

    Returns
    -------
    ij.ImagePlus[]
        A list of ImagePlus objects resulting from the import.
    """
    options = ImporterOptions()
    mode = {
        'color' : ImporterOptions.COLOR_MODE_COLORIZED,
        'composite' : ImporterOptions.COLOR_MODE_COMPOSITE,
        'gray' : ImporterOptions.COLOR_MODE_GRAYSCALE,
        'default' : ImporterOptions.COLOR_MODE_DEFAULT,
    }
    options.setColorMode(mode[color_mode])
    options.setSplitChannels(split_c)
    options.setSplitFocalPlanes(split_z)
    options.setSplitTimepoints(split_t)
    options.setId(filename)
    log.info("Reading [%s]", filename)
    orig_imps = BF.openImagePlus(options)
    log.debug("Opened [%s] %s", filename, type(orig_imps))
    return orig_imps


def export(imp, filename, overwrite=False):
    """Simple wrapper to export an image to a given file.

    Parameters
    ----------
    imp : ImagePlus
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
    if unit == 'pixel' and (suffix == 'ics' or suffix == 'ids'):
        log.warn("Forcing unit to be 'm' instead of 'pixel' to avoid "
                 "Bio-Formats 6.0.x Exporter bug!")
        imp.calibration.unit = 'm'
    if os.path.exists(filename):
        if not overwrite:
            raise IOError('file [%s] already exists!' % filename)
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
    imp : ImagePlus
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
    out_file : str
        The full name of the exported file.
    """
    out_file = gen_name_from_orig(path, orig_name, tag, suffix)
    export(imp, out_file, overwrite)
    return out_file
