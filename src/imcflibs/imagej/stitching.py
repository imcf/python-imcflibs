"""Functions to work on stitching datasets."""

from os.path import join

from java.lang.System import getProperty  # pylint: disable-msg=import-error

import micrometa  # pylint: disable-msg=import-error
import ij  # pylint: disable-msg=import-error

from .misc import show_status, show_progress, error_exit
from ..strtools import flatten
from ..log import LOG as log


def process_fluoview_project(infile):
    """Process a FluoView mosaic project file.

    Parameters
    ----------
    infile : str
        The full path to either an `MATL_Mosaic.log` or any `*.omp2info` file
        from a FluoView MATL acquisition.

    Returns
    -------
    micrometa.experiment.MosaicExperiment
        The mosaic object if parsing the project file has been successful.
    """
    if infile[-9:] == ".omp2info":
        mosaicclass = micrometa.fluoview.FluoView3kMosaic
    elif infile[-4:] == ".log":
        mosaicclass = micrometa.fluoview.FluoViewMosaic
    else:
        error_exit("Unsupported input file: %s" % infile)

    log.info("Parsing project file: [%s]", infile)
    ij.IJ.showStatus("Parsing mosaics...")

    mosaics = mosaicclass(infile, runparser=False)
    total = len(mosaics.mosaictrees)
    ij.IJ.showProgress(0.0)
    show_status("Parsed %s / %s mosaics" % (0, total))
    for i, subtree in enumerate(mosaics.mosaictrees):
        log.info("Parsing mosaic %s...", i + 1)
        try:
            mosaics.add_mosaic(subtree, i)
        except (ValueError, IOError) as err:
            log.warn("Skipping mosaic %s: %s", i, err)
        except RuntimeError as err:
            log.warn("Error parsing mosaic %s, SKIPPING: %s", i, err)
        show_progress(i, total)
        show_status("Parsed %s / %s mosaics" % (i + 1, total))
    show_progress(total, total)
    show_status("Parsed %i mosaics." % total)

    if not mosaics:
        error_exit("Couldn't find any (valid) mosaics in the project file!")
    log.info(mosaics.summarize())

    return mosaics


def gen_macro(mosaics, indir, outfile=None, opts=None):
    """Generate stitcher macro code and optionally save it in a file.

    Parameters
    ----------
    mosaics : micrometa.experiment.MosaicExperiment
        The mosaic object of the stitching experiment.
    indir : str
        The path to use as input directory *INSIDE* the macro.
    outfile : str (optional)
        The path to a file for saving the generated macro code.
    opts : dict (optional)
        A dict to be passed on to micrometa.imagej.gen_stitching_macro().

    Returns
    -------
    list(str)
        The generated macro code as a list of strings (one str per line).
    """
    templates = join(getProperty("fiji.dir"), "jars", "python-micrometa.jar")
    log.info("Using macro templates from [%s].", templates)
    log.info("Using [%s] as base directory.", indir)

    # set the default stitcher options
    stitcher_options = {
        "export_format": '".ids"',
        "split_z_slices": "false",
        "rotation_angle": 0,
        "stitch_regression": 0.3,
        "stitch_maxavg_ratio": 2.5,
        "stitch_abs_displace": 3.5,
        "compute": "false",
    }
    # merge explicit options, overriding the defaults from above if applicable:
    if opts:
        stitcher_options.update(opts)

    code = micrometa.imagej.gen_stitching_macro(
        name=mosaics.infile["dname"],
        path=indir,
        tplpfx="templates/imagej-macro/stitching",
        tplpath=templates,
        opts=stitcher_options,
    )

    log.debug("============= begin of generated macro code =============")
    log.debug(flatten(code))
    log.debug("============= end of generated  macro code =============")

    if outfile is not None:
        log.info("Writing stitching macro.")
        micrometa.imagej.write_stitching_macro(code, outfile)

    return code
