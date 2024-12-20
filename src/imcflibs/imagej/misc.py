"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

import sys
import time
import smtplib

from ij import IJ  # pylint: disable-msg=import-error
from ij.plugin.frame import RoiManager  # pylint: disable-msg=import-error
from ij.measure import ResultsTable  # pylint: disable-msg=import-error
from ij import Prefs as prefs
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


def calculate_mean_and_stdv(float_values):
    """Calculate mean and standard deviation from a list of floats.

    Parameters
    ----------
    float_values : list(float)
        List containing float numbers.

    Returns
    -------
    [float, float]
        Mean and standard deviation of the list.
    """
    mean = sum(float_values) / len(float_values)
    tot = 0.0
    for x in float_values:
        tot = tot + (x - mean) ** 2
    return [mean, (tot / (len(float_values))) ** 0.5]


def find_focus(imp):
    """Function to get the focused stack. Works on single-channel images only.

    Parameters
    ----------
    imp : ImagePlus
        A single-channel ImagePlus.

    Returns
    -------
    int
        Slice number which seems to be the best focused one.
    """

    imp_dimensions = imp.getDimensions()

    # Check if more than 1 channel
    # FUTURE Could be improved for multi channel
    if imp_dimensions[2] != 1:
        sys.exit("Image has more than one channel, please reduce dimensionality")

    # Loop through each time points
    for plane in range(1, imp_dimensions[4] + 1):
        focused_slice = 0
        norm_var = 0
        imp.setT(plane)
        # Loop through each z plane
        for current_z in range(1, imp_dimensions[3] + 1):
            imp.setZ(current_z)
            pix_array = imp.getProcessor().getPixels()
            mean = (sum(pix_array)) / len(pix_array)
            pix_array = [(x - mean) * (x - mean) for x in pix_array]
            # pix_array = pix_array*pix_array

            sumpix_array = sum(pix_array)
            var = sumpix_array / (imp_dimensions[0] * imp_dimensions[1] * mean)

            if var > norm_var:
                norm_var = var
                focused_slice = current_z

    return focused_slice


def send_mail(job_name, recipient, filename, total_execution_time):
    """Send an email using the SMTP server and sender email configured in ImageJ's Preferences.

    Parameters
    ----------
    job_name : string
        Job name to display in the email.
    recipient : string
        Recipient's email address.
    filename : string
        The name of the file to be passed in the email.
    total_execution_time : str
        The time it took to process the file in the format [HH:MM:SS:ss].
    """
    # Retrieve sender email and SMTP server from preferences
    sender = prefs.get("imcf.sender_email", "").strip()
    server = prefs.get("imcf.smtpserver", "").strip()

    # Ensure the sender and server are configured from Prefs
    if not sender:
        print("Sender email is not configured. Please check IJ_Prefs.txt.")
        return
    if not server:
        print("SMTP server is not configured. Please check IJ_Prefs.txt.")
        return

    # Ensure the recipient is provided
    if not recipient.strip():
        print("Recipient email is required.")
        return

    # Form the email subject and body
    subject = "Your {0} job finished successfully".format(job_name)
    body = (
        "Dear recipient,\n\n"
        "This is an automated message.\n"
        "Your dataset '{0}' has been successfully processed "
        "({1} [HH:MM:SS:ss]).\n\n"
        "Kind regards,\n"
        "The IMCF-team"
    ).format(filename, total_execution_time)

    # Form the complete message
    message = ("From: {0}\nTo: {1}\nSubject: {2}\n\n{3}").format(
        sender, recipient, subject, body
    )

    # Try sending the email, print error message if it wasn't possible
    try:
        smtpObj = smtplib.SMTP(server)
        smtpObj.sendmail(sender, recipient, message)
        print("Successfully sent email")
    except smtplib.SMTPException as err:
        print("Error: Unable to send email:", err)
    return


def progressbar(progress, total, line_number, prefix=""):
    """Progress bar for the IJ log window.

    FIXME: how is this different from show_progressbar() above? Please explain
    in the function description here.

    Parameters
    ----------
    progress : int
        Current step of the loop.
    total : int
        Total number of steps for the loop.
    line_number : int
        Number of the line to be updated.
    prefix : str, optional
        Text to use before the progress bar, by default ''.
    """

    size = 30
    x = int(size * progress / total)
    IJ.log(
        "\\Update%i:%s[%s%s] %i/%i\r"
        % (line_number, prefix, "#" * x, "." * (size - x), progress, total)
    )


def get_free_memory():
    """Get the free memory thats available to ImageJ.

    Returns
    -------
    free_memory : int
        The free memory in bytes.
    """
    max_memory = int(IJ.maxMemory())
    used_memory = int(IJ.currentMemory())
    free_memory = max_memory - used_memory

    return free_memory


def setup_clean_ij_environment(rm=None, rt=None):
    """Set up a clean and defined ImageJ environment.

    Parameters
    ----------
    rm : RoiManager, optional
        A reference to an IJ-RoiManager instance.
    rt : ResultsTable, optional
        A reference to an IJ-ResultsTable instance.
    """
    # FIXME: use function(s) from the "roimanager" module!
    if not rm:
        rm = RoiManager.getInstance()
        if not rm:
            rm = RoiManager()

    if not rt:
        rt = ResultsTable.getInstance()
        if not rt:
            rt = ResultsTable()

    rm.runCommand("reset")
    rt.reset()
    IJ.log(r"\\Clear")

    # FIXME: integrate commands from method below
    # fix_ij_options()
