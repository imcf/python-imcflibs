"""Common logging singleton for the package.

Example
-------
>>> from log import LOG as log

From there on a logger is available for usage with e.g. log.warn(), even if the
import statement from above happens in multiple places across modules, it will
always use the same logger instance (that "singleton" functionality is built
into the logging module, we just do the setup here). This can easily be checked
by looking at the log handlers in the different modules.

The logging levels, in increasing order of importance, are:

10 DEBUG
20 INFO
30 WARN
40 ERROR
50 CRITICAL
"""


import logging


LOG = logging.getLogger(__name__)


def enable_console_logging():
    """Add a stream handler logging to the console.

    Returns
    -------
    logging.StreamHandler
    """
    stream_handler = logging.StreamHandler()
    LOG.addHandler(stream_handler)
    return stream_handler


def enable_file_logging(fname, mode="a"):
    """Add a logging handler writing to a file.

    Returns
    -------
    logging.FileHandler
    """
    file_handler = logging.FileHandler(fname, mode=mode)
    LOG.addHandler(file_handler)
    return file_handler


def set_loglevel(verbosity):
    """Calculate the default loglevel and set it accordingly.

    This is a convenience function that wraps the calculation and setting of
    the logging level. The way our "log" module is currently built (as a
    singleton), there is no obvious better way to have this somewhere else.

    Example
    -------
    This will set the loglevel to DEBUG:
    >>> set_loglevel(2)

    This will set the loglevel to INFO:
    >>> set_loglevel(1)

    To set the verbosity level when you're e.g. using argparse to count the
    number of occurences of '-v' switches on the commandline into a variable
    'verbosity', this code can be used:
    >>> log.set_loglevel(args.verbosity)
    """
    # default loglevel is 30 while 20 and 10 show more details
    loglevel = (3 - verbosity) * 10
    LOG.setLevel(loglevel)
