"""ImageJ processing utilities for filtering and thresholding images.

This module provides functions to apply various image processing operations
using ImageJ, including filters, background subtraction, and thresholding.
"""

from ij import IJ

from ..log import LOG as log


def apply_filter(imp, filter_method, filter_radius, do_3d=False):
    """Make a specific filter followed by a threshold method of choice.

    Parameters
    ----------
    imp : ImagePlus
        Input ImagePlus to filter and threshold
    filter_method : str
        Name of the filter method to use. Must be one of:
            - Median
            - Mean
            - Gaussian Blur
            - Minimum
            - Maximum
    filter_radius : int
        Radius of the filter filter to use
    do_3d : bool, optional
        If set to True, will do a 3D filtering, by default False


    Returns
    -------
    ij.ImagePlus
        Filtered ImagePlus
    """
    log.info("Applying filter %s with radius %d" % (filter_method, filter_radius))

    if filter_method not in [
        "Median",
        "Mean",
        "Gaussian Blur",
        "Minimum",
        "Maximum",
    ]:
        raise ValueError(
            "filter_method must be one of: Median, Mean, Gaussian Blur, Minimum, Maximum"
        )

    if do_3d:
        filter = filter_method + " 3D..."
    else:
        filter = filter_method + "..."

    options = (
        "sigma="
        if filter_method == "Gaussian Blur"
        else "radius=" + str(filter_radius) + " stack"
    )

    log.debug("Filter: <%s> with options <%s>" % (filter, options))

    imageplus = imp.duplicate()
    IJ.run(imageplus, filter, options)

    return imageplus


def apply_rollingball_bg_subtraction(imp, rolling_ball_radius, do_3d=False):
    """Perform background subtraction using a rolling ball method.

    Parameters
    ----------
    imp : ij.ImagePlus
        Input ImagePlus to filter and threshold
    rolling_ball_radius : int
        Radius of the rolling ball filter to use
    do_3d : bool, optional
        If set to True, will do a 3D filtering, by default False

    Returns
    -------
    ij.ImagePlus
        Filtered ImagePlus
    """
    log.info("Applying rolling ball with radius %d" % rolling_ball_radius)

    options = "rolling=" + str(rolling_ball_radius) + " stack" if do_3d else ""

    log.debug("Background subtraction options: %s" % options)

    imageplus = imp.duplicate()
    IJ.run(imageplus, "Substract Background...", options)

    return imageplus


def apply_threshold(imp, threshold_method, do_3d=True):
    """Apply a threshold method to the input ImagePlus.

    Parameters
    ----------
    imp : ij.ImagePlus
        Input ImagePlus to filter and threshold
    threshold_method : str
        Name of the threshold method to use
    do_3d : bool, optional
        If set to True, the automatic threshold will be done on a 3D stack, by default True

    Returns
    -------
    ij.ImagePlus
        Thresholded ImagePlus
    """

    log.info("Applying threshold method %s" % threshold_method)

    imageplus = imp.duplicate()

    auto_threshold_options = (
        threshold_method + " " + "dark" + " " + "stack" if do_3d else ""
    )

    log.debug("Auto threshold options: %s" % auto_threshold_options)

    IJ.setAutoThreshold(imageplus, auto_threshold_options)

    convert_to_binary_options = (
        "method=" + threshold_method + " " + "background=Dark" + " " + "black"
    )

    log.debug("Convert to binary options: %s" % convert_to_binary_options)

    IJ.run(imageplus, "Convert to Mask", convert_to_binary_options)

    return imageplus
