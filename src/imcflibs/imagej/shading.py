"""Functions to work on shading correction / model generation."""

import os

import ij  # pylint: disable-msg=import-error
from ij import IJ
from ij.plugin import ImageCalculator, Concatenator
from ij.process import StackStatistics, ImageProcessor
from ..imagej import bioformats  # pylint: disable-msg=no-name-in-module
from ..imagej import misc, projections
from ..log import LOG as log
from ..pathtools import gen_name_from_orig, listdir_matching


def apply_model(imps, model, merge=True):
    """Apply a given shading model to a list of images / stacks.

    The model is supposed to be a normalized 32-bit floating point 2D image that
    will be used as a divisor to the slices of all ImagePlus objects given.

    WARNING: the operation happens in-place, i.e. the original "imps" images
    will be modified!

    Parameters
    ----------
    imps : list(ij.ImagePlus)
        A list of ImagePlus objects (e.g. separate channels of a multi-channel
        stack image) that should be corrected for shading artefacts.
    model : ij.ImagePlus
        A 2D image with 32-bit float values normalized to 1.0 (i.e. no pixels
        with higher values) to be used for dividing the input images to correct
        for shading.
    merge : bool, optional
        Whether or not to combine the resulting ImagePlus objects into a single
        multi-channel stack (default=True).

    Returns
    -------
    ij.ImagePlus or list(ij.ImagePlus)
        The merged ImagePlus with all channels, or the original list of stacks
        with the shading-corrected image planes.
    """
    log.debug("Applying shading correction...")
    calc = ij.plugin.ImageCalculator()
    for i, stack in enumerate(imps):
        log.debug("Processing channel %i...", i)
        calc.run("Divide stack", stack, model)

    if not merge:
        return imps

    log.debug("Merging shading-corrected channels...")
    merger = ij.plugin.RGBStackMerge()
    merged_imp = merger.mergeChannels(imps, False)
    return merged_imp


def correct_and_project(filename, path, model, proj, fmt):
    """Apply a shading correction to an image and create a projection.

    In case the target file for the shading corrected image already exists,
    nothing is done - neither the shading correction is re-created nor any
    projections will be done (independent on whether the latter one already
    exist or not).

    Parameters
    ----------
    filename : str
        The full path to a multi-channel image stack.
    path : str
        The full path to a directory for storing the results. Will be created in
        case it doesn't exist yet. Existing files will be overwritten.
    model : ij.ImagePlus or None
        A 32-bit floating point image to be used as the shading model. If model
        is None, no shading correction will be applied.
    proj : str
        A string describing the projections to be created. Use 'None' for not
        creating any projections, 'ALL' to do all supported ones.
    fmt : str
        The file format suffix to be used for the results and projections, e.g.
        '.ics' for ICS2 etc. See the Bio-Formats specification for details.

    Returns
    -------
    (bool, bool)
        A tuple of booleans indicating whether a shading correction has been
        applied and whether projections were created. The latter depends on
        both, the requested projections as well as the image type (e.g. it can
        be False even if projections were requested, but the image)
    """
    target = gen_name_from_orig(path, filename, "", fmt)
    if os.path.exists(target):
        log.info("Found shading corrected file, not re-creating: %s", target)
        return False, False

    if not os.path.exists(path):
        os.makedirs(path)

    imps = bioformats.import_image(filename, split_c=True)
    ret_corr = False
    if model is not None:
        log.debug("Applying shading correction on [%s]...", filename)
        imp = apply_model(imps, model)
        bioformats.export_using_orig_name(imp, path, filename, "", fmt, True)
        # imps needs to be updated with the new (=merged) stack:
        imps = [imp]
        ret_corr = True

    if proj == "None":
        projs = []
    elif proj == "ALL":
        projs = ["Average", "Maximum"]
    else:
        projs = [proj]
    for imp in imps:
        ret_proj = projections.create_and_save(imp, projs, path, filename, fmt)
        imp.close()

    log.debug("Done processing [%s].", os.path.basename(filename))
    return ret_corr, ret_proj


def process_folder(path, suffix, outpath, model_file, fmt):
    """Run shading correction and projections on an entire folder.

    Parameters
    ----------
    path : str
        The input folder to be scanned for images to be processed.
    suffix : str
        The file name suffix of the files to be processed.
    outpath : str
        The output folder where results will be stored. Existing files will be
        overwritten.
    model_file : str
        The full path to a normalized 32-bit shading model image. If set to '-'
        or 'NONE', no shading correction will be applied, i.e. only the
        projection step will have an effect.
    fmt : str
        The file format suffix for storing the results.
    """
    matching_files = listdir_matching(path, suffix, fullpath=True)
    process_files(matching_files, outpath, model_file, fmt)


def process_files(files, outpath, model_file, fmt):
    """Run shading correction and projections on a list of files.

    Parameters
    ----------
    files : list(str)
        The files to be processed, as a list of strings with the full path.
    outpath : str
        The output folder where results will be stored. Existing files will be
        overwritten.
    model_file : str
        The full path to a normalized 32-bit shading model image. If set to '-'
        or 'NONE', no shading correction will be applied, i.e. only the
        projection step will have an effect.
    fmt : str
        The file format suffix for storing the results.
    """
    log.info("Running shading correction and projections on %s files...", len(files))

    if model_file.upper() in ["-", "NONE"]:
        model = None
    else:
        model = ij.IJ.openImage(model_file)
        # the model needs to be shown, otherwise the IJ.run() call ignores it
        try:
            model.show()
            canvas = model.getCanvas()
            for _ in range(5):
                # we have to show it, but we can make it smaller:
                canvas.zoomOut(100, 100)
        except AttributeError:
            misc.error_exit("Opening shading model [%s] failed!" % model_file)

    for in_file in files:
        correct_and_project(in_file, outpath, model, "ALL", fmt)

    if model:
        model.close()

def simple_flatfield_correction(imp, sigma=20.0):
    """Performs a simple flatfield correction to a given ImagePlus stack.

    The function returns a 32-bit corrected flatfield image.

    Parameters
    ----------
    imp : ij.ImagePlus
        The input stack to be projected.
    sigma: float, optional
        The sigma value for the Gaussian blur, default=20.0

    Returns
    -------
    ij.ImagePlus
        The 32-bit image result of flatfield correction

    """
    flatfield = imp.duplicate()
    sigma_str = "sigma=" + str(sigma)

    IJ.run(flatfield, "Gaussian Blur...", sigma_str)
    stats = StackStatistics(flatfield)

    # Normalize image to the highest value of original (requires 32-bit image)
    IJ.run(flatfield, "32-bit", "")
    IJ.run(
        flatfield,
        "Divide...",
        "value=" + str(stats.max))
    ic = ImageCalculator()
    flatfield_corrected = ic.run("Divide create", imp, flatfield)

    return flatfield_corrected
