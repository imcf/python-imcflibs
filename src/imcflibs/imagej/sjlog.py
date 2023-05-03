"""Helper functions to set up the scijava logger from Python."""

import sjlogging  # pylint: disable-msg=import-error
from .prefs import debug_mode


def scijava_logger(log_service):
    """Prepare logger and set the level according to stored ImageJ preferences.

    Parameters
    ----------
    log_service : org.scijava.log.LogService
        The LogService instance, usually retrieved in a SciJava script by using
        the script parameters annotation `#@ LogService logs` or equivalent.

    Returns
    -------
    logger : logging.Logger
        The Python logger object connected to SciJava's LogService.
    """
    logger = sjlogging.setup_logger(log_service)
    log_level = "INFO"
    if debug_mode():
        # issue a message with level "warn" to bring up the console window:
        logger.warn("Enabling debug logging.")
        log_level = "DEBUG"
    sjlogging.set_loglevel(log_level)
    return logger
