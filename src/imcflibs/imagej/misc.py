"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

import sys, time
from ij import IJ  # pylint: disable-msg=E0401

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

def elapsed_time_since(start,end=None):
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

    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

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
    return 100 * float(part)/float(whole)

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
    mean = sum(list)/len(list)
    tot = 0.0
    for x in list:
        tot = tot + (x - mean)**2
    return [mean, (tot/(len(list)))**0.5]
