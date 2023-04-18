"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

import sys
import time

from ij import IJ, ImageStack  # pylint: disable-msg=E0401

from ..log import LOG as log


def show_status(msg):
    """Wrapper to update the ImageJ status bar and the log simultaneously."""
    log.info(msg)
    IJ.showStatus(msg)


def show_progress(cur, final):
    """Wrapper to update the progress bar and issue a log message."""
    # ij.IJ.showProgress is adding 1 to the value given as first parameter...
    log.info("Progress: %s / %s (%s)", cur + 1, final, (1.0 + cur) / final)
    IJ.showProgress(cur, final)


def error_exit(msg):
    """Convenience wrapper to log an error and exit then."""
    log.error(msg)
    sys.exit(msg)


def elapsed_time_since(start, end=None):
    """Prints the elapsed time for execution

    Parameters
    ----------
    start : time
        Start time
    end : time, optional
        End time

    Returns
    -------
    str
        Formatted time elapsed
    """

    if not end:
        end = time.time()

    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


def percentage(part, whole):
    """Returns the percentage of a value based on total

    Parameters
    ----------
    part : float
        Part
    whole : float
        Complete size

    Returns
    -------
    float
        Percentage
    """
    return 100 * float(part) / float(whole)


def calculate_mean_and_stdv(list):
    """Gets statistics from a list

    Parameters
    ----------
    list : float
        List containing values

    Returns
    -------
    [float, float]
        Mean and Std of the list
    """
    mean = sum(list) / len(list)
    tot = 0.0
    for x in list:
        tot = tot + (x - mean) ** 2
    return [mean, (tot / (len(list))) ** 0.5]


def find_focus(imp):
    """Function to get the focused stack. Only works on 1 channel

    Parameters
    ----------
    imp : ImagePlus
        1-channel ImagePlus
    Returns
    -------
    int
        Slice number which seems to be in focus
    """

    bitDepth = imp.getBitDepth()
    imDim = imp.getDimensions()
    focusedStack = ImageStack(imDim[0], imDim[1])

    # Check if more than 1 channel
    # FUTURE Could be improved for multi channel
    if imDim[2] != 1:
        sys.exit("Image has more than one channel, please reduce dimensionality")

    # Loop through each time points
    for plane in range(1, imDim[4] + 1):
        m = 0
        normVar = 0
        imp.setT(plane)
        # Loop through each z plane
        for tp in range(1, imDim[3] + 1):
            imp.setZ(tp)
            pixArray = imp.getProcessor().getPixels()
            mean = (sum(pixArray)) / len(pixArray)
            pixArray = [(x - mean) * (x - mean) for x in pixArray]
            # pixArray = pixArray*pixArray

            sumPixArray = sum(pixArray)
            var = sumPixArray / (imDim[0] * imDim[1] * mean)

            if var > normVar:
                normVar = var
                m = tp

    return m


def progressbar(progress, total, line_number, prefix=""):
    """Progress bar for the IJ log window

    Parameters
    ----------
    progress : int
        Current step of the loop
    total : int
        Total number of steps for the loop
    line_number : int
        Number of the line to be updated
    prefix : str, optional
        Text to use before the progress bar, by default ''
    """

    size = 20
    x = int(size * progress / total)
    IJ.log(
        "\\Update%i:%s[%s%s] %i/%i\r"
        % (
            line_number,
            timed_log(prefix, True),
            "#" * x,
            "." * (size - x),
            progress,
            total,
        )
    )


def timed_log(message, as_string=False):
    """Print a log message with a timestamp added

    Parameters
    ----------
    message : str
        Message to print
    """
    if as_string:
        return time.strftime("%H:%M:%S", time.localtime()) + ": " + message + " "
    IJ.log(time.strftime("%H:%M:%S", time.localtime()) + ": " + message + " ")
