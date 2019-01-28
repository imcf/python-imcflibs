"""Functions to work with ImageJ preferences."""

from ij import Prefs

def debug_mode():
    """Wrapper to check if 'imcf.debugging' is enabled.

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
