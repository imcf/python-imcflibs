"""Functions to work with ImageJ preferences."""

from ij import Prefs, IJ  # pylint: disable-msg=E0401


def debug_mode():
    """Check if the 'imcf.debugging' setting is enabled.

    This is a workaround for a Jython issue in ImageJ with values that are
    stored in the "IJ_Prefs.txt" file being cast to the wrong types and / or
    values in Python. Calling Prefs.get() using a (Python) boolean as the
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

    Will set the following options to ensure consistent behavior independent of
    how ImageJ is configured on a specific machine.

    - Ensure ImageJ appearance settings are the default values.
    - Set foreground color to white and background to black.
    - Set default file saving format to .txt files.
    - Ensure intensities are being scaled when converting between bit depths.
    - Options on binary images:
        - Set background to black.
        - Enable padding to prevent eroding from image edges.
        - Enforce defaults on iterations and count for *erosion*, *dilation*,
          *opening* and *closing* operations.

    References
    ----------
    The ImageJ User Guide is providing detailed explanations of the options
    configured by this function:

    - [Edit > Options > Appearance][ijo_app]
    - [Edit > Options > Colors][ijo_col]
    - [Edit > Options > Conversions][ijo_cnv]
    - [Edit > Options > Input/Output][ijo_i_o]
    - [Process > Binary > Options][ijo_bin]

    [ijo_app]: https://imagej.net/ij/docs/guide/146-27.html#sub:Appearance...
    [ijo_cnv]: https://imagej.net/ij/docs/guide/146-27.html#sub:Conversions...
    [ijo_col]: https://imagej.net/ij/docs/guide/146-27.html#sub:Colors...
    [ijo_i_o]: https://imagej.net/ij/docs/guide/146-27.html#sub:Input/Output...
    [ijo_bin]: https://imagej.net/ij/docs/guide/146-29.html#sub:BinaryOptions...
    """

    # Set all appearance settings to default values (untick all options)
    IJ.run("Appearance...", " ")

    # Set foreground color to be white and background black
    IJ.run("Colors...", "foreground=white background=black selection=red")

    # Options regarding binary images:
    # - `black`: set background for binary images to be black.
    # - `pad`: enable padding of edges to prevent eroding from image edge.
    # - `iterations=1`: number of times erosion (dilation, opening, closing) is
    #   performed
    # - `count=1`: number of adjacent background pixels necessary before a pixel
    #   is removed from the edge of an object during erosion and the number of
    #   adjacent foreground pixels necessary before a pixel is added to the edge
    #   of an object during dilation.
    # https://imagej.net/ij/docs/menus/process.html#options
    # https://imagej.net/ij/docs/guide/146-29.html#sub:BinaryOptions...
    IJ.run("Options...", "iterations=1 count=1 black pad")

    # Set default saving format to .txt files
    IJ.run("Input/Output...", "file=.txt save_column save_row")

    # Enable "scale when converting".
    # https://imagej.net/ij/docs/menus/edit.html#options
    IJ.run("Conversions...", "scale")
