"""Functions to work on shading correction / model generation."""

import os

import ij  # pylint: disable-msg=import-error

from ..imagej import bioformats
from ..imagej import projections
from ..pathtools import listdir_matching, gen_name_from_orig
from ..log import LOG as log


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
    model : ImagePlus
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
    calc = ij.plugin.ImageCalculator()
    for stack in imps:
        # log.debug("Processing channel...")
        calc.run("Divide stack", stack, model)

    if not merge:
        return imps

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
    model : ij.ImagePlus
        A 32-bit floating point image to be used as the shading model.
    proj : str
        A string describing the projections to be created. Use 'None' for not
        creating any projections, 'ALL' to do all supported ones.
    fmt : str
        The file format suffix to be used for the results and projections, e.g.
        '.ics' for ICS2 etc. See the Bio-Formats specification for details.
    """
    target = gen_name_from_orig(path, filename, "", fmt)
    if os.path.exists(target):
        log.info("Found shading corrected file, not re-creating: %s", target)
        return

    log.debug("Applying shading correction on [%s]...", filename)
    if not os.path.exists(path):
        os.makedirs(path)

    orig = bioformats.import_image(filename, split_c=True)
    corrected = apply_model(orig, model)
    bioformats.export_using_orig_name(corrected, path, filename, "", fmt, True)

    if proj == 'None':
        projs = []
    elif proj == 'ALL':
        projs = ['Average', 'Maximum']
    else:
        projs = [proj]
    projections.create_and_save(corrected, projs, path, filename, fmt)

    # corrected.show()
    corrected.close()
    log.debug("Done processing [%s].", os.path.basename(filename))


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
        The full path to a normalized 32-bit shading model image.
    fmt : str
        The file format suffix for storing the results.
    """
    imp = ij.IJ.openImage(model_file)
    matching_files = listdir_matching(path, suffix)

    imp.show()  # required, otherwise the IJ.run() call will ignore the imp
    for orig_file in matching_files:
        in_file = os.path.join(path, orig_file)
        correct_and_project(in_file, outpath, imp, 'ALL', fmt)
    imp.close()
