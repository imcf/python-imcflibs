"""ImageJ processing utilities for filtering and thresholding images.

This module provides functions to apply various image processing operations
using ImageJ, including filters, background subtraction, and thresholding.
"""

from ij import IJ

from ..log import LOG as log


def filter_options(filter_method, filter_radius, do_3d=False):
    """Build the ImageJ filter command and options strings.

    Parameters
    ----------
    filter_method : str
        Name of the filter method to use. Must be one of:
            - Median
            - Mean
            - Gaussian Blur
            - Minimum
            - Maximum
    filter_radius : int
        Radius of the filter to use
    do_3d : bool, optional
        If set to True, will do a 3D filtering, by default False

    Returns
    -------
    tuple[str, str]
        The filter name and options strings
    """

    if do_3d:
        filter_name = filter_method + " 3D..."
    else:
        filter_name = filter_method + "..."

    if filter_method == "Gaussian Blur":
        options = "sigma=" + str(filter_radius) + " stack"
    else:
        options = "radius=" + str(filter_radius) + " stack"

    return filter_name, options


def threshold_options(threshold_method, do_3d=True):
    """Build the ImageJ threshold option strings.

    Parameters
    ----------
    threshold_method : str
        Name of the threshold method to use
    do_3d : bool, optional
        If set to True, the automatic threshold will be done on a 3D stack,
        by default True

    Returns
    -------
    tuple[str, str]
        The auto threshold options and the convert to binary options strings

    """

    auto_threshold_options = (
        threshold_method + " " + "dark" + " " + "stack" if do_3d else ""
    )

    convert_to_binary_options = (
        "method=" + threshold_method + " " + "background=Dark" + " " + "black"
    )

    return auto_threshold_options, convert_to_binary_options


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

    filter, options = filter_options(filter_method, filter_radius, do_3d=do_3d)

    log.debug("Filter: <%s> with options <%s>" % (filter, options))

    imageplus = imp.duplicate()
    IJ.run(imageplus, filter, options)

    return imageplus


def apply_rollingball_bg_subtraction(
    imp,
    rolling_ball_radius,
    light_background=False,
    sliding=False,
    disable_smoothing=False,
    do_3d=False,
):
    """Perform background subtraction using a rolling ball method.

    Parameters
    ----------
    imp : ij.ImagePlus
        Input ImagePlus to filter and threshold
    rolling_ball_radius : int
        Radius of the rolling ball filter to use
    light_background : bool, optional
        If set to True, will treat the background as light, by default False
    sliding : bool, optional
        If set to True, will do a sliding window approach, by default False
    disable_smoothing : bool, optional
        If set to True, will disable the smoothing, by default False
    do_3d : bool, optional
        If set to True, will do a 3D filtering, by default False

    Returns
    -------
    ij.ImagePlus
        Filtered ImagePlus
    """
    log.info("Applying rolling ball with radius %d" % rolling_ball_radius)

    options = rolling_ball_options(
        rolling_ball_radius,
        light_background=light_background,
        sliding=sliding,
        disable_smoothing=disable_smoothing,
        do_3d=do_3d,
    )

    log.debug("Background subtraction options: %s" % options)

    imageplus = imp.duplicate()
    IJ.run(imageplus, "Subtract Background...", options)

    return imageplus


def rolling_ball_options(
    rolling_ball_radius,
    light_background=False,
    sliding=False,
    disable_smoothing=False,
    do_3d=False,
):
    """Generate the options for the "Subtract Background..." macro command.

    Parameters
    ----------
    rolling_ball_radius : int
        Radius of the rolling ball filter to use
    light_background : bool, optional
        If set to True, will treat the background as light, by default False
    sliding : bool, optional
        If set to True, will do a sliding window approach, by default False
    disable_smoothing : bool, optional
        If set to True, will disable the smoothing, by default False
    do_3d : bool, optional
        If set to True, will do a 3D filtering, by default False

    Returns
    -------
    str
        The options string for the "Subtract Background..." macro command

    """
    parts = ["rolling=" + str(rolling_ball_radius)]
    if light_background:
        parts.append("light")
    if sliding:
        parts.append("sliding")
    if disable_smoothing:
        parts.append("disable")
    if do_3d:
        parts.append("stack")
    return " ".join(parts)


def apply_threshold(imp, threshold_method, do_3d=True):
    """Apply a threshold method to the input ImagePlus.

    Parameters
    ----------
    imp : ij.ImagePlus
        Input ImagePlus to filter and threshold
    threshold_method : str
        Name of the threshold method to use
    do_3d : bool, optional
        If set to True, the automatic threshold will be done on a 3D stack,
        by default True

    Returns
    -------
    ij.ImagePlus
        Thresholded ImagePlus
    """

    log.info("Applying threshold method %s" % threshold_method)

    imageplus = imp.duplicate()

    auto_threshold_options, convert_to_binary_options = threshold_options(
        threshold_method, do_3d=do_3d
    )

    log.debug("Auto threshold options: %s" % auto_threshold_options)

    IJ.setAutoThreshold(imageplus, auto_threshold_options)

    log.debug("Convert to binary options: %s" % convert_to_binary_options)

    IJ.run(imageplus, "Convert to Mask", convert_to_binary_options)

    return imageplus
