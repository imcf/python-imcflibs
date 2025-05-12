"""Miscellaneous ImageJ related functions, mostly convenience wrappers."""

import csv
import glob
import os
import smtplib
import subprocess
import sys
import time

from ij import IJ  # pylint: disable-msg=import-error
from ij.plugin import Duplicator, ImageCalculator, StackWriter

from .. import pathtools
from ..log import LOG as log
from . import bioformats as bf
from . import prefs


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

    Notes
    -----
    Returns (0, 0) when:
        - The input list is empty.
        - After filtering out None values, no elements remain.
    """

    filtered_list = [x for x in values_list if x is not None]

    if not filtered_list:
        return 0, 0

    mean = round(sum(filtered_list) / len(filtered_list), round_decimals)
    variance = sum((x - mean) ** 2 for x in filtered_list) / len(filtered_list)
    std_dev = round(variance**0.5, round_decimals)

    return mean, std_dev


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


def send_notification_email(
    job_name, recipient, filename, total_execution_time, subject="", message=""
):
    """Send an email notification with optional details of the processed job.

    Retrieve the sender email and SMTP server settings from ImageJ's preferences
    and use them to send an email notification with job details.

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
    subject : string, optional
        Subject of the email, by default says job finished.
    message : string, optional
        Message to be included in the email, by default says job processed.

    Notes
    -----
    - The function requires two preferences to be set in `~/.imagej/IJ_Prefs.txt`:
      - `.imcf.sender_email`: the sender's email address
      - `.imcf.smtpserver`: the SMTP server address
    - If these preferences are not set or if required parameters are missing,
      the function logs a message and exits without sending an email.
    - In case of an SMTP error, the function logs a warning.
    """

    # Retrieve sender email and SMTP server from preferences
    # NOTE: the leading dot "." has to be omitted in the `Prefs.get()` call,
    # despite being present in the `IJ_Prefs.txt` file!
    sender = prefs.Prefs.get("imcf.sender_email", "").strip()
    server = prefs.Prefs.get("imcf.smtpserver", "").strip()

    # Ensure the sender and server are configured from Prefs
    if not sender:
        log.info("[.imcf.sender_email] is not configured in '~/.imagej/IJ_Prefs.txt'.")
        return
    if not server:
        log.info("[.imcf.smtpserver] is not configured in '~/.imagej/IJ_Prefs.txt'.")
        return

    log.debug("Using SMTP server [%s].", server)

    # Ensure the recipient is provided
    if not recipient.strip():
        log.info("Recipient email is required, not sending email notification.")
        return

    # Form the email subject and body
    if subject == "":
        subject = "Your {0} job has finished".format(job_name)
    else:
        subject = subject

    if message == "":
        body = (
            "Dear recipient,\n\n"
            "This is an automated message.\n"
            "Your workflow '{0}' has been processed "
            "({1} [HH:MM:SS:ss]).\n\n"
            "Kind regards.\n"
        ).format(filename, total_execution_time)
    else:
        body = message

    # Form the complete message
    message = ("From: {0}\nTo: {1}\nSubject: {2}\n\n{3}").format(
        sender, recipient, subject, body
    )

    # Try sending the email, print error message if it wasn't possible
    try:
        smtpObj = smtplib.SMTP(server)
        smtpObj.sendmail(sender, recipient, message)
        log.debug("Successfully sent email to <%s>.", recipient)
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
    """Print a message to the ImageJ log window, prefixed with a timestamp.

    If `as_string` is set to True, nothgin will be printed to the log window,
    instead the formatted log message will be returned as a string.

    Parameters
    ----------
    message : str
        Message to print
    as_string : bool, optional
        Flag to request the formatted string to be returned instead of printing
        it to the log. By default False.
    """
    formatted = time.strftime("%H:%M:%S", time.localtime()) + ": " + message + " "
    if as_string:
        return formatted
    IJ.log(formatted)


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
        The ImagePlus that is to be subtracted from.
    imp2: ij.ImagePlus
        The ImagePlus that is to be subtracted.

    Returns
    -------
    ij.ImagePlus
        The ImagePlus resulting from the subtraction.
    """
    ic = ImageCalculator()
    subtracted = ic.run("Subtract create", imp1, imp2)

    return subtracted


def close_images(list_of_imps):
    """Close all open ImagePlus objects given in a list.

    Parameters
    ----------
    list_of_imps: list(ij.ImagePlus)
        A list of open ImagePlus objects.
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


def write_ordereddict_to_csv(out_file, content):
    """Write data from a list of OrderedDicts to a CSV file.

    When performing measurements in an analysis that is e.g. looping over
    multiple files, it's useful to keep the results in `OrderedDict` objects,
    e.g. one per analyzed file / dataset. This function can be used to create a
    CSV file (or append to an existing one) from a list of `OrderedDict`s. The
    structure inside the dicts is entirely up to the calling code (i.e. it's not
    related to ImageJ's *Results* window or such), the only requirement is
    type-consistency among all the `OrderedDict`s provided to the function.

    Parameters
    ----------
    out_file : str
        Path to the output CSV file.
    content : list of OrderedDict
        List of OrderedDict objects representing the data rows to be written.
        All dictionaries must have the same keys.

    Notes
    -----
    - The CSV file will use the semicolon charachter (`;`) as delimiter.
    - When appending to an existing file, the column structure has to match. No
      sanity checking is being done on this by the function!
    - The output file is opened in binary mode for compatibility.

    Examples
    --------
    >>> from collections import OrderedDict
    >>> results = [
    ...     OrderedDict([('id', 1), ('name', 'Sample A'), ('value', 42.5)]),
    ...     OrderedDict([('id', 2), ('name', 'Sample B'), ('value', 37.2)])
    ... ]
    >>> write_ordereddict_to_csv('results.csv', results)

    The resulting CSV file will have the following content:

        id;name;value
        1;Sample A;42.5
        2;Sample B;37.2
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


def save_image_in_format(imp, format, out_dir, series, pad_number, split_channels):
    """Save an ImagePlus object in the specified format.

    This function provides flexible options for saving ImageJ images in various
    formats with customizable naming conventions. It supports different
    Bio-Formats compatible formats as well as ImageJ-native formats, and can
    handle multi-channel images by either saving them as a single file or
    splitting channels into separate files.

    The function automatically creates necessary directories and uses consistent
    naming patterns with series numbers. For split channels, separate
    subdirectories are created for each channel (C1, C2, etc.).

    Parameters
    ----------
    imp : ij.ImagePlus
        ImagePlus object to save.
    format : {'ImageJ-TIF', 'ICS-1', 'ICS-2', 'OME-TIFF', 'CellH5', 'BMP'}
        Output format to use, see Notes section below for details.
    out_dir : str
        Directory path where the image(s) will be saved.
    series : int
        Series number to append to the filename.
    pad_number : int
        Number of digits to use when zero-padding the series number.
    split_channels : bool
        If True, split channels and save them individually in separate folders
        named "C1", "C2", etc. inside out_dir. If False, save all channels in a
        single file.

    Notes
    -----
    Depending on the value of the `format` parameter, one of the following
    output formats and saving strategies will be used:
    - Bio-Formats based formats will be produced by calling `bf.export()`, note
      that these formats will preserve metadata (which is **not** the case for
      the other formats using different saving strategies):
        - `ICS-1`: Save as ICS version 1 format (a pair of `.ics` and `.ids`).
        - `ICS-2`: Save as ICS version 2 format (single `.ics` file).
        - `OME-TIFF`: Save in OME-TIFF format (`.ome.tif`).
        - `CellH5`: Save as CellH5 format (`.ch5`).
    - `ImageJ-TIF`: Save in ImageJ TIFF format (`.tif`) using `IJ.saveAs()`.
    - `BMP`: Save in BMP format using `StackWriter.save()`, producing one `.bmp`
      per slice in a subfolder named after the original image.

    Examples
    --------
    Save a multichannel image as OME-TIFF without splitting channels:

    >>> save_image_with_extension(imp, "OME-TIFF", "/output/path", 1, 3, False)
    ... # resulting file: /output/path/image_title_series_001.ome.tif

    Save with channel splitting:

    >>> save_image_with_extension(imp, "OME-TIFF", "/output/path", 1, 3, True)
    ... # resulting files: /output/path/C1/image_title_series_001.ome.tif
    ... #                  /output/path/C2/image_title_series_001.ome.tif
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
        for channel in range(1, imp.getNChannels() + 1):
            imp_to_use.append(
                Duplicator().run(
                    imp,
                    channel,
                    channel,
                    1,
                    imp.getNSlices(),
                    1,
                    imp.getNFrames(),
                )
            )
            dir_to_save.append(os.path.join(out_dir, "C" + str(channel)))
    else:
        imp_to_use.append(imp)
        dir_to_save.append(out_dir)

    for index, current_imp in enumerate(imp_to_use):
        basename = imp.getShortTitle()

        out_path = pathtools.join2(
            dir_to_save[index],
            basename + "_series_" + str(series).zfill(pad_number),
        )

        if format == "ImageJ-TIF":
            pathtools.create_directory(dir_to_save[index])
            IJ.saveAs(current_imp, "Tiff", out_path + ".tif")

        elif format == "BMP":
            out_folder = os.path.join(out_dir, basename + os.path.sep)
            pathtools.create_directory(out_folder)
            StackWriter.save(current_imp, out_folder, "format=bmp")

        else:
            bf.export(current_imp, out_path + out_ext[format])

        current_imp.close()


def locate_latest_imaris(paths_to_check=None):
    """Find paths to latest installed Imaris or ImarisFileConverter version.

    Identify the full path to the most recent (as in "version number")
    ImarisFileConverter or Imaris installation folder with the latter one having
    priority. In case nothing is found, an empty string is returned.

    Parameters
    ----------
    paths_to_check: list of str, optional
        A list of paths that should be used to look for the installations, by default
        `None` which will fall back to the standard installation locations of Bitplane.

    Returns
    -------
    str
    """
    if not paths_to_check:
        paths_to_check = [
            r"C:\Program Files\Bitplane\ImarisFileConverter ",
            r"C:\Program Files\Bitplane\Imaris ",
        ]

    imaris_paths = [""]

    for check in paths_to_check:
        hits = glob.glob(check + "*")
        imaris_paths += sorted(
            hits,
            key=lambda x: float(x.replace(check, "").replace(".", "")),
        )

    return imaris_paths[-1]


def run_imarisconvert(file_path, pixel_calibration=None):
    """Convert a given file to Imaris format using ImarisConvert.

    Convert the input image file to Imaris format (Imaris5) using the
    ImarisConvert utility. The function uses the latest installed Imaris
    application to perform the conversion via `subprocess.call()`.

    Parameters
    ----------
    file_path : str
        Absolute path to the input image file.
    pixel_calibration : tuple or list, optional
        Sequence of 3 values (x, y, z) representing voxel dimensions to be set during
        conversion, by default None.
    """
    # in case the given file has the suffix `.ids` (meaning it is part of an
    # ICS-1 `.ics`+`.ids` pair), point ImarisConvert to the `.ics` file instead:
    path_root, file_extension = os.path.splitext(file_path)
    if file_extension == ".ids":
        file_extension = ".ics"
        file_path = path_root + file_extension

    imaris_path = locate_latest_imaris()

    command = 'ImarisConvert.exe  -i "%s" -of Imaris5 -o "%s"' % (
        file_path,
        file_path.replace(file_extension, ".ims"),
    )
    if pixel_calibration:
        command = command + " --voxelsizex %s --voxelsizey %s --voxelsizez %s" % (
            pixel_calibration[0],
            pixel_calibration[1],
            pixel_calibration[2],
        )

    log.debug("\n%s" % command)
    IJ.log("Converting to Imaris5 .ims...")
    result = subprocess.call(command, shell=True, cwd=imaris_path)
    if result == 0:
        IJ.log("Conversion to .ims is finished.")
    else:
        IJ.log("Conversion failed with error code: %d" % result)
