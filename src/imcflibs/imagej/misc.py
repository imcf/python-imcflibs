"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

import sys
import time
import smtplib
import os
import csv

from ij import IJ  # pylint: disable-msg=import-error
from ij.plugin import ImageCalculator

from . import prefs
from ..log import LOG as log


def show_status(msg):
    """Update the ImageJ status bar and issue a log message.

    Parameters
    ----------
    msg : str
        The message to display in the ImageJ status bar and log.
    """
    log.info(msg)
    IJ.showStatus(msg)


def show_progress(cur, final):
    """Update ImageJ's progress bar and print the current progress to the log.

    Parameters
    ----------
    cur : int
        Current progress value.
    final : int
        Total value representing 100% completion.

    Notes
    -----
    `ij.IJ.showProgress` internally increments the given `cur` value by 1.
    """
    log.info("Progress: %s / %s (%s)", cur + 1, final, (1.0 + cur) / final)
    IJ.showProgress(cur, final)


def error_exit(msg):
    """Log an error message and exit.

    Parameters
    ----------
    msg : str
        The error message to log.
    """
    log.error(msg)
    sys.exit(msg)


def elapsed_time_since(start, end=None):
    """Generate a string with the time elapsed between two timepoints.

    Parameters
    ----------
    start : float
        The start time, typically obtained via `time.time()`.
    end : float, optional
        The end time. If not given, the current time is used.

    Returns
    -------
    str
        The elapsed time formatted as `HH:MM:SS.ss`.

    """
    if not end:
        end = time.time()

    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)


def percentage(part, whole):
    """Calculate the percentage of a value based on total.

    Parameters
    ----------
    part : float
        The portion value of a total.
    whole : float
        The total value.

    Returns
    -------
    float
        The percentage value.
    """
    return 100 * float(part) / float(whole)


def calculate_mean_and_stdv(values_list, round_decimals=0):
    """Calculate mean and standard deviation from a list of floats.

    Parameters
    ----------
    values_list : list of int,float
        List containing numbers.
    round_decimals : int, optional
        Rounding decimal to use for the result, by default 0

    Returns
    -------
    tuple of (float, float)
        Mean and standard deviation of the input list.
    """
    filtered_list = filter(None, values_list)

    try:
        mean = round(sum(filtered_list) / len(filtered_list), round_decimals)
    except ZeroDivisionError:
        mean = 0
    tot = 0.0
    for x in filtered_list:
        tot = tot + (x - mean) ** 2
    return [mean, (tot / (len(filtered_list))) ** 0.5]


def find_focus(imp):
    """Find the slice of a stack that is the best focused one.

    First, calculate the variance of the pixel values in each slice. The slice
    with the highest variance is considered the best focused as this typically
    indicates more contrast and sharpness.

    Parameters
    ----------
    imp : ij.ImagePlus
        A single-channel ImagePlus stack.

    Returns
    -------
    int
        The slice number of the best focused slice.

    Raises
    ------
    SystemExit
        If the image has more than one channel.

    Notes
    -----
    Currently only single-channel stacks are supported.
    """

    imp_dimensions = imp.getDimensions()

    # Check if more than 1 channel
    # FUTURE Could be improved for multi channel
    if imp_dimensions[2] != 1:
        sys.exit("Image has more than one channel, please reduce dimensionality")

    # Loop through each time point
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
    sender = prefs.Prefs.get("imcf.sender_email", "").strip()
    server = prefs.Prefs.get("imcf.smtpserver", "").strip()

    # Ensure the sender and server are configured from Prefs
    if not sender:
        log.info("Sender email is not configured. Please check IJ_Prefs.txt.")
        return
    if not server:
        log.info("SMTP server is not configured. Please check IJ_Prefs.txt.")
        return

    # Ensure the recipient is provided
    if not recipient.strip():
        log.info("Recipient email is required.")
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
        log.debug("Successfully sent email")
    except smtplib.SMTPException as err:
        log.warning("Error: Unable to send email: %s", err)
    return


def progressbar(progress, total, line_number, prefix=""):
    """Progress bar for the IJ log window.

    Show a progress bar in the log window of Fiji at a specific line independent
    of the main Fiji progress bar.

    Parameters
    ----------
    progress : int
        Current step of the loop.
    total : int
        Total number of steps for the loop.
    line_number : int
        Number of the line to be updated.
    prefix : str, optional
        Text to use before the progress bar, by default an empty string.
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
    """Print a message to the ImageJ log window with a timestamp added.

    Parameters
    ----------
    message : str
        Message to print
    """
    if as_string:
        return time.strftime("%H:%M:%S", time.localtime()) + ": " + message + " "
    IJ.log(time.strftime("%H:%M:%S", time.localtime()) + ": " + message + " ")


def get_free_memory():
    """Get the free memory that is available to ImageJ.

    Returns
    -------
    free_memory : int
        The free memory in bytes.
    """
    max_memory = int(IJ.maxMemory())
    used_memory = int(IJ.currentMemory())
    free_memory = max_memory - used_memory

    return free_memory


def setup_clean_ij_environment(rm=None, rt=None):  # pylint: disable-msg=unused-argument
    """Set up a clean and defined ImageJ environment.

    This funtion clears the active results table, the ROI manager, and the log.
    Additionally, it closes all open images and resets the ImageJ options,
    performing a [*Fresh Start*][fresh_start].

    Parameters
    ----------
    rm : RoiManager, optional
        Will be ignored (kept for keeping API compatibility).
    rt : ResultsTable, optional
        Will be ignored (kept for keeping API compatibility).

    Notes
    -----
    "Fresh Start" is described in the [ImageJ release notes][ij_relnotes],
    following a [suggestion by Robert Haase][fresh_start].

    [ij_relnotes]: https://imagej.nih.gov/ij/notes.html
    [fresh_start]: https://forum.image.sc/t/43102
    """

    IJ.run("Fresh Start", "")
    IJ.log("\\Clear")

    prefs.fix_ij_options()


def sanitize_image_title(imp):
    """Remove special chars and various suffixes from the title of an ImagePlus.

    Parameters
    ----------
    imp : ImagePlus
        The ImagePlus to be renamed.

    Notes
    -----
    The function removes the full path of the image file (if present), retaining
    only the base filename using `os.path.basename()`.
    """
    # sometimes (unclear when) the title contains the full path, therefore we
    # simply call `os.path.basename()` on it to remove all up to the last "/":
    image_title = os.path.basename(imp.getTitle())
    image_title = image_title.replace(".czi", "")
    image_title = image_title.replace(" ", "_")
    image_title = image_title.replace("_-_", "")
    image_title = image_title.replace("__", "_")
    image_title = image_title.replace("#", "Series")

    imp.setTitle(image_title)


def subtract_images(imp1, imp2):
    """Subtract one image from the other (imp1 - imp2).

    Parameters
    ----------
    imp1: ij.ImagePlus
        The ImagePlus that is to be subtracted from
    imp2: ij.ImagePlus
        The ImagePlus that is to be subtracted

    Returns
    ---------
    ij.ImagePlus
        The ImagePlus resulting from the subtraction
    """
    ic = ImageCalculator()
    subtracted = ic.run("Subtract create", imp1, imp2)

    return subtracted


def close_images(list_of_imps):
    """Close all open ImagePlus objects given in a list.

    Parameters
    ----------
    list(ij.ImagePlus)
        A list of open ImagePlus objects
    """
    for imp in list_of_imps:
        imp.changes = False
        imp.close()


def get_threshold_value_from_method(imp, method, ops):
    """Get the value of a selected AutoThreshold method for the given ImagePlus.

    This is useful to figure out which threshold value will be calculated by the
    selected method for the given stack *without* actually having to apply it.

    Parameters
    ----------
    imp : ij.ImagePlus
        The image from which to get the threshold value.
    method : {'huang', 'ij1', 'intermodes', 'isoData', 'li', 'maxEntropy',
        'maxLikelihood', 'mean', 'minError', 'minimum', 'moments', 'otsu',
        'percentile', 'renyiEntropy', 'rosin', 'shanbhag', 'triangle', 'yen'}
        The AutoThreshold method to use.
    ops: ops.OpService
        The ImageJ Ops service instance, usually retrieved through a _Script
        Parameter_ at the top of the script, as follows:
        ```
        #@ OpService ops
        ```

    Returns
    -------
    int
        The threshold value chosen by the selected method.
    """
    histogram = ops.run("image.histogram", imp)
    threshold_value = ops.run("threshold.%s" % method, histogram)
    threshold_value = int(round(threshold_value.get()))

    return threshold_value


def write_results(out_file, content):
    """
    Write the results to a csv file.

    Parameters
    ----------
    out_file : str
        Path to the output file.
    content : list of OrderedDict
        List of dictionaries representing the results.

    """

    # Check if the output file exists
    if not os.path.exists(out_file):
        # If the file does not exist, create it and write the header
        with open(out_file, "wb") as f:
            dict_writer = csv.DictWriter(f, content[0].keys(), delimiter=";")
            dict_writer.writeheader()
            dict_writer.writerows(content)
    else:
        # If the file exists, append the results
        with open(out_file, "ab") as f:
            dict_writer = csv.DictWriter(f, content[0].keys(), delimiter=";")
            dict_writer.writerows(content)
def save_as(imageplus, extension, out_dir, series, pad_number, split_channels):
    """Function to save an image

    Parameters
    ----------
    imageplus : ImagePlus
        ImagePlus to save
    extension : str
        Extension to use for the output
    out_dir : str
        Path for the output
    series : int
        Series to open
    pad_number : int
        Number of 0 to use for padding
    split_channels : bool
        Bool to split or not the channels
    """

    out_ext = {}
    out_ext["ImageJ-TIF"] = ".tif"
    out_ext["ICS-1"] = ".ids"
    out_ext["ICS-2"] = ".ics"
    out_ext["OME-TIFF"] = ".ome.tif"
    out_ext["CellH5"] = ".ch5"
    out_ext["BMP"] = ".bmp"

    imp_to_use = []
    dir_to_save = []

    if split_channels:
        for channel in range(1, imageplus.getNChannels() + 1):
            imp_to_use.append(
                Duplicator().run(
                    imageplus,
                    channel,
                    channel,
                    1,
                    imageplus.getNSlices(),
                    1,
                    imageplus.getNFrames(),
                )
            )
            dir_to_save.append(os.path.join(out_dir, "C" + str(channel)))
    else:
        imp_to_use.append(imageplus)
        dir_to_save.append(out_dir)

    for index, current_imp in enumerate(imp_to_use):
        basename = imageplus.getShortTitle()

        out_path = os.path.join(
            dir_to_save[index], basename + "_series_" + str(series).zfill(pad_number)
        )

        if extension == "ImageJ-TIF":
            check_folder(dir_to_save[index])
            IJ.saveAs(current_imp, "Tiff", out_path + ".tif")

        elif extension == "BMP":
            out_folder = os.path.join(out_dir, basename + os.path.sep)
            check_folder(out_folder)
            StackWriter.save(current_imp, out_folder, "format=bmp")

        else:
            bf.export(current_imp, out_path + out_ext[extension])

        current_imp.close()
def pad_number(index, pad_length=2):
    """Pad a number with leading zeros to a specified length.

    Parameters
    ----------
    index : int or str
        The number to be padded
    pad_length : int, optional
        The total length of the resulting string after padding, by default 2

    Returns
    -------
    str
        The padded number as a string

    Examples
    --------
    >>> pad_number(7)
    '07'
    >>> pad_number(42, 4)
    '0042'
    """
    return str(index).zfill(pad_length)
