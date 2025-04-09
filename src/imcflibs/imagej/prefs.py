"""Functions to work with ImageJ preferences."""

from ij import Prefs, IJ  # pylint: disable-msg=E0401


def debug_mode():
    """Check if the 'imcf.debugging' setting is enabled.

    This is a workaround for a Jython issue in ImageJ with values that are
    stored in the "IJ_Prefs.txt" file being cast to the wrong types and / or
    values in Python. Callling Prefs.get() using a (Python) boolean as the
    second parameter always leads to the return value '0.0' (Python type float),
    no matter what is actually stored in the preferences. Doing the same in e.g.
    Groovy behaves correctly.

    Calling Prefs.get() as below with the second parameter being a string and
    subsequently checking the string value leads to the expected result.
    """
    debug = Prefs.get("imcf.debugging", "false")
    return debug == "true"


def set_default_ij_options():
    """Configure ImageJ default options for consistency.

    Set the following options:
    - Ensure ImageJ appearance settings are default values.
    - Set foreground color to white and background to black.
    - Set black background for binary images.
    - Set default file saving format to .txt files.
    - Ensure images are scaled appropriately when converting between different bit depths.
    """

    # Set all appearance settings to default values (untick all options)
    IJ.run("Appearance...", " ")

    # Set foreground color to be white and background black
    IJ.run("Colors...", "foreground=white background=black selection=red")

    # Set black background for binary images and set pad edges to true to prevent eroding from image edge
    IJ.run("Options...", "iterations=1 count=1 black pad")

    # Set default saving format to .txt files
    IJ.run("Input/Output...", "file=.txt save_column save_row")

    # Scale when converting = checked
    IJ.run("Conversions...", "scale")
