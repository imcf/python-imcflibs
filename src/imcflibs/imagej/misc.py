"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

from ij import IJ  # pylint: disable-msg=E0401

from ..log import LOG as log

def show_status(msg):
    """Wrapper to update the ImageJ status bar and the log simultaneously."""
    log.info(msg)
    IJ.showStatus(msg)


def show_progress(cur, final):
    """Wrapper to update the progress bar and issue a log message."""
    # ij.IJ.showProgress is adding 1 to the value given as first parameter...
    log.info("Progress: %s / %s (%s)", cur+1, final, (1.0+cur)/final)
    IJ.showProgress(cur, final)
