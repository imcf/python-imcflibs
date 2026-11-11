"""BigDataViewer related functions.

Mostly convenience wrappers with simplified calls and default values.
"""

# Some function names just need to be longer than 30 chars:
# pylint: disable-msg=invalid-name

# The attribute count is not really our choice:
# pylint: disable-msg=too-many-instance-attributes

import os
import shutil
import sys

from ij import IJ
from java.io import File, FileInputStream, InputStreamReader
from javax.xml.parsers import DocumentBuilderFactory
from org.xml.sax import InputSource

from .. import pathtools
from ..log import LOG as log

# internal template strings used in string formatting (note: the `"""@private"""`
# pseudo-decorator is there to instruct [pdoc] to omit those variables when generating
# API documentation):
SINGLE = "[Single %s (Select from List)]"
"""@private"""
MULTIPLE = "[Multiple %ss (Select from List)]"
"""@private"""
RANGE = "[Range of %ss (Specify by Name)]"
"""@private"""
SINGLE_FILE = "[NO (one %s)]"
"""@private"""
MULTI_SINGLE_FILE = "[YES (all %ss in one file)]"
"""@private"""
MULTI_MULTI_FILE = "[YES (one file per %s)]"
"""@private"""

PLUGIN_CLASSES = {
    "Apply Transformations": "net.preibisch.mvrecon.fiji.plugin.Apply_Transformation",
    "Define Multi-View Dataset": "net.preibisch.mvrecon.fiji.plugin.Define_Multi_View_Dataset",
    "Detect Interest Points for Registration": (
        "net.preibisch.mvrecon.fiji.plugin.Interest_Point_Detection"
    ),
    "Duplicate Transformations": "net.preibisch.mvrecon.fiji.plugin.Duplicate_Transformation",
    "Image Fusion": "net.preibisch.mvrecon.fiji.plugin.Image_Fusion",
    "Register Dataset based on Interest Points": (
        "net.preibisch.mvrecon.fiji.plugin.Interest_Point_Registration"
    ),
    "Calculate pairwise shifts ...": "net.preibisch.stitcher.plugin.Calculate_Pairwise_Shifts",
    "Filter pairwise shifts ...": "net.preibisch.stitcher.plugin.Filter_Pairwise_Shifts",
    "Optimize globally and apply shifts ...": (
        "net.preibisch.stitcher.plugin.Global_Optimization_Stitching"
    ),
}
"""@private
Plugin classes of the MVR / BigStitcher commands (multiview-reconstruction
9.x, BigStitcher 3.x)."""


def run_command(command, options):
    """Run an MVR / BigStitcher command by its plugin class.

    `IJ.run()` looks a command up by its menu name. The legacy
    `SPIM_Registration` plugin, which some Fiji installations still ship,
    registers several of the same names (e.g. "Register Dataset based on
    Interest Points", "Detect Interest Points for Registration", "Apply
    Transformations"), so `IJ.run()` may start the old plugin instead. This
    function starts the class from `PLUGIN_CLASSES` and hands over the macro
    options the same way `IJ.run()` does. Commands without a known class (and
    environments without `IJ.runPlugIn`, e.g. the test mocks) use `IJ.run()`.
    See https://github.com/imcf/python-imcflibs/issues/158 for the details.

    Parameters
    ----------
    command : str
        The menu command, e.g. `Image Fusion`.
    options : str
        The macro options string.
    """
    class_name = PLUGIN_CLASSES.get(command)
    if class_name is None or not hasattr(IJ, "runPlugIn"):
        IJ.run(command, str(options))
        return

    from ij import Macro
    from java.lang import Thread

    thread = Thread.currentThread()
    # ImageJ only hands macro options to threads named "Run$_..."
    if not thread.getName().startswith("Run$_"):
        thread.setName("Run$_" + thread.getName())
    Macro.setOptions(thread, str(options))
    try:
        IJ.runPlugIn(command, class_name, "")
    finally:
        Macro.setOptions(thread, None)


class ProcessingOptions(object):
    """Helper to store processing options and generate parameter strings.

    Example
    -------
    NOTE: for readability reasons the output has been split into multiple lines
    even though the formatters are returning a single-line string.

    >>> opts = ProcessingOptions()
    >>> opts.process_channel(2)
    >>> opts.reference_tile(1)
    >>> opts.treat_timepoints("compare")

    >>> opts.fmt_acitt_options()
    ... process_angle=[All angles]
    ... process_channel=[Single channel (Select from List)]
    ... process_illumination=[All illuminations]
    ... process_tile=[All tiles]
    ... process_timepoint=[All Timepoints]

    >>> opts.fmt_acitt_selectors()
    ... processing_channel=[channel 1]

    >>> opts.fmt_use_acitt()
    ... channels=[Average Channels]
    ... illuminations=[Average Illuminations]
    ... tiles=[use Tile 1]

    >>> opts.fmt_how_to_treat()
    ... how_to_treat_angles=[treat individually]
    ... how_to_treat_channels=group
    ... how_to_treat_illuminations=group
    ... how_to_treat_tiles=group
    ... how_to_treat_timepoints=compare
    """

    def __init__(self):
        self._angle_processing_option = "[All angles]"
        self._angle_select = ""

        self._channel_processing_option = "[All channels]"
        self._channel_select = ""

        self._illumination_processing_option = "[All illuminations]"
        self._illumination_select = ""

        self._tile_processing_option = "[All tiles]"
        self._tile_select = ""

        self._timepoint_processing_option = "[All Timepoints]"
        self._timepoint_select = ""

        # by default `angles` is empty as the "sane" default value for
        # "treat_angles" is "[treat individually]"
        self._use_angle = ""
        # all other "use" options are set to averaging by default:
        self._use_channel = "channels=[Average Channels]"
        self._use_illumination = "illuminations=[Average Illuminations]"
        self._use_tile = "tiles=[Average Tiles]"
        # BigStitcher writes "TimePoint" (from the class name `TimePoint`)
        self._use_timepoint = "timepoints=[Average TimePoints]"

        # 'treat_*' values are: "group", "compare" or "[treat individually]"
        self._treat_angles = "[treat individually]"
        self._treat_channels = "group"
        self._treat_illuminations = "group"
        self._treat_tiles = "compare"
        self._treat_timepoints = "[treat individually]"

    ### reference-X methods

    def reference_angle(self, value):
        """Set the reference angle when using *Expert Grouping Options*.

        Select the angle(s) to use for the operation, by default empty (`""`).

        NOTE: this value will be used to render `angles=[use Angle VALUE]` when
        calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : str
            The tile to use for the grouping.
        """
        self._use_angle = "angles=[use Angle %s]" % str(value)
        log.debug("New reference angle setting: %s", self._use_angle)

    def reference_channel(self, value):
        """Set the reference channel when using *Expert Grouping Options*.

        Select the channel(s) to use for the operation, by default the averaging
        mode will be used (`channels=[Average Channels]`).

        NOTE: this value will be used to render `channels=[use Channel VALUE]`
        when calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
            The channel number to use for the grouping.
        """
        # channel = int(value) - 1  # will raise a ValueError if cast fails
        self._use_channel = "channels=[use Channel %s]" % int(value)
        log.debug("New reference channel setting: %s", self._use_channel)

    def reference_illumination(self, value):
        """Set the reference illumination when using *Expert Grouping Options*.

        Select the illumination(s) to use for the operation, by default the
        averaging mode will be used (`illuminations=[Average Illuminations]`).

        NOTE: this value will be used to render `illuminations=[use Illumination
        VALUE]` when calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
            The illumination number to use for the grouping.
        """
        self._use_illumination = "illuminations=[use Illumination %s]" % value
        log.debug(
            "New reference illumination setting: %s",
            self._use_illumination,
        )

    def reference_tile(self, value):
        """Set the reference tile when using *Expert Grouping Options*.

        Select the tile(s) to use for the operation, by default the averaging
        mode will be used (`tiles=[Average Tiles]`).

        NOTE: this value will be used to render `tiles=[use Tile VALUE]` when
        calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int
            The tile number to use for the grouping.
        """
        self._use_tile = "tiles=[use Tile %s]" % str(value)
        log.debug("New reference tile setting: %s", self._use_tile)

    def reference_timepoint(self, value):
        """Set the reference timepoint when using *Expert Grouping Options*.

        Select the timepoint(s) to use for the operation, by default the
        averaging mode will be used (`timepoints=[Average Timepoints]`).

        NOTE: this value will be used to render `timepoints=[use Timepoint
        VALUE]` when calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
            The timepoint number to use for the grouping.
        """
        self._use_timepoint = "timepoints=[use TimePoint %s]" % value
        log.debug("New reference timepoint setting: %s", self._use_timepoint)

    ### process-X methods

    def process_angle(self, value, range_end=None):
        """Set the processing option for angles.

        Update the angle processing option and selection depending on input.
        If the range_end is not None, it is considered as a range.

        Parameters
        ----------
        value : str, int, list of int or list of str
            The angle(s) to use for processing, either a single value or a list.
        range_end : int, optional
            Contains the end of the range, by default None.

        Notes
        -----
        Previous function name : angle_select().
        """

        selection = check_processing_input(value, range_end)
        processing_option, dimension_select = get_processing_settings(
            "angle", selection, value, range_end
        )

        self._angle_processing_option = processing_option
        self._angle_select = dimension_select

    def process_channel(self, value, range_end=None):
        """Set the processing option for channels.

        Update the channel processing option and selection depending on input.
        If the range_end is not None, it is considered as a range.

        Parameters
        ----------
        value : str, int, list of int or list of str
            The channel(s) to use for processing, a single value or a list.
        range_end : int, optional
            Contains the end of the range, by default None.

        Notes
        -----
        Previous function name : channel_select().
        """

        selection = check_processing_input(value, range_end)
        processing_option, dimension_select = get_processing_settings(
            "channel", selection, value, range_end
        )

        self._channel_processing_option = processing_option
        self._channel_select = dimension_select

    def process_illumination(self, value, range_end=None):
        """Set the processing option for illuminations.

        Update the illumination processing option and selection depending on
        input. If the range_end is not None, it is considered as a range.

        Parameters
        ----------
        value : str, int, list of int or list of str
            The illumination(s) to use for processing, a single value or a list.
        range_end : int, optional
            Contains the end of the range, by default None.

        Notes
        -----
        Previous function name : illumination_select().
        """

        selection = check_processing_input(value, range_end)
        processing_option, dimension_select = get_processing_settings(
            "illumination", selection, value, range_end
        )

        self._illumination_processing_option = processing_option
        self._illumination_select = dimension_select

    def process_tile(self, value, range_end=None):
        """Set the processing option for tiles.

        Update the tile processing option and selection depending on input.
        If the range_end is not None, it is considered as a range.

        Parameters
        ----------
        value : str, int, list of int or list of str
            The tile(s) to use for processing, a single value or a list.
        range_end : int, optional
            Contains the end of the range, by default None.

        Notes
        -----
        Previous function name : tile_select().
        """

        selection = check_processing_input(value, range_end)
        processing_option, dimension_select = get_processing_settings(
            "tile", selection, value, range_end
        )

        self._tile_processing_option = processing_option
        self._tile_select = dimension_select

    def process_timepoint(self, value, range_end=None):
        """Set the processing option for timepoints.

        Update the timepoint processing option and selection depending on input.
        If the range_end is not None, it is considered as a range.

        Parameters
        ----------
        value : str, int, list of int or list of str
            The timepoint(s) to use for processing, a single value or a list.
        range_end : int, optional
            Contains the end of the range, by default None.

        Notes
        -----
        Previous function name : timepoint_select().
        """

        selection = check_processing_input(value, range_end)
        processing_option, dimension_select = get_processing_settings(
            "timepoint", selection, value, range_end
        )

        self._timepoint_processing_option = processing_option
        self._timepoint_select = dimension_select

    ### treat-X methods

    def treat_angles(self, value):
        """Set the value for the `how_to_treat_angles` option.

        If the value is set to `group` also the `reference_angle` setting will
        be adjusted to `angles=[Average Angles]`.

        The default setting is `[treat individually]`.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_angles = value
        log.debug("New 'treat_angles' setting: %s", value)
        if value == "group":
            self._use_angle = "angles=[Average Angles]"
            log.debug("New 'use_angle' setting: %s", self._use_angle)

    def treat_channels(self, value):
        """Set the value for the `how_to_treat_channels` option.

        The default setting is `group`.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_channels = value
        log.debug("New 'treat_channels' setting: %s", value)

    def treat_illuminations(self, value):
        """Set the value for the `how_to_treat_illuminations` option.

        The default setting is `group`.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_illuminations = value
        log.debug("New 'treat_illuminations' setting: %s", value)

    def treat_tiles(self, value):
        """Set the value for the `how_to_treat_tiles` option.

        The default setting is `compare`.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_tiles = value
        log.debug("New 'treat_tiles' setting: %s", value)

    def treat_timepoints(self, value):
        """Set the value for the `how_to_treat_timepoints` option.

        The default setting is `[treat individually]`.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_timepoints = value
        log.debug("New 'treat_timepoints' setting: %s", value)

    ### formatter methods

    def fmt_acitt_options(self, input="process"):
        """Format Angle / Channel / Illumination / Tile / Timepoint options.

        Build a string providing the `process_angle`, `process_channel`,
        `process_illumination`, `process_tile` and `process_timepoint` options
        that can be used in a BDV-related `IJ.run` call.

        Returns
        -------
        str
        """
        input_type = ["process", "resave"]
        if input not in input_type:
            raise ValueError("Invalid input type, expected one of: %s" % input_type)
        parameters = [
            input + "_angle=" + self._angle_processing_option,
            input + "_channel=" + self._channel_processing_option,
            input + "_illumination=" + self._illumination_processing_option,
            input + "_tile=" + self._tile_processing_option,
            input + "_timepoint=" + self._timepoint_processing_option,
        ]
        parameter_string = " ".join(parameters).strip()
        log.debug("Formatted 'process_X' options: <%s>", parameter_string)
        return parameter_string + " "

    def fmt_acitt_selectors(self):
        """Format Angle / Channel / Illumination / Tile / Timepoint selectors.

        Build a string providing the `angle_select`, `channel_select`,
        `illumination_select`, `tile_select` and `timepoint_select` options that
        can be used in a BDV-related `IJ.run` call. In case no selectors have
        been chosen, nothing but a single space will be returned.

        Returns
        -------
        str
            The formatted selector string. Will be a single white-space in case
            no selectors have been configured for the object.
        """
        parameters = [
            self._angle_select if self._angle_select else "",
            self._channel_select if self._channel_select else "",
            self._illumination_select if self._illumination_select else "",
            self._tile_select if self._tile_select else "",
            self._timepoint_select if self._timepoint_select else "",
        ]
        parameter_string = " ".join(parameters).strip()
        log.debug("Formatted 'processing_X' selectors: <%s>", parameter_string)
        return parameter_string + " "

    def fmt_how_to_treat(self):
        """Format a parameter string with all `how_to_treat_` options.

        Returns
        -------
        str
        """
        parameters = [
            "how_to_treat_angles=" + self._treat_angles,
            "how_to_treat_channels=" + self._treat_channels,
            "how_to_treat_illuminations=" + self._treat_illuminations,
            "how_to_treat_tiles=" + self._treat_tiles,
            "how_to_treat_timepoints=" + self._treat_timepoints,
        ]
        parameter_string = " ".join(parameters).strip()
        log.debug("Formatted 'how_to_treat_X' options: <%s>", parameter_string)
        return parameter_string + " "

    def fmt_use_acitt(self):
        """Format expert grouping options, e.g. `channels=[use Channel 2]`.

        Generate a parameter string using the configured expert grouping options
        for ACITT. Please note that this may be an empty string (`""`).

        Returns
        -------
        str
        """
        parameters = [
            self._use_angle if self._treat_angles == "group" else "",
            self._use_channel if self._treat_channels == "group" else "",
            self._use_illumination if self._treat_illuminations == "group" else "",
            self._use_tile if self._treat_tiles == "group" else "",
            self._use_timepoint if self._treat_timepoints == "group" else "",
        ]
        parameter_string = " ".join(parameters).strip()
        log.debug(
            "Formatted expert grouping 'use' options: <%s>",
            parameter_string,
        )
        return parameter_string + " "


class DefinitionOptions(object):
    """Helper to store definition options and generate parameters strings.

    Example
    -------
    NOTE: for readability reasons the output has been split into multiple lines
    even though the formatters are returning a single-line string.

    >>> opts = DefinitionOptions()
    >>> opts.set_angle_definition("single")
    >>> opts.set_channel_definition("multi_single")

    >>> opts.fmt_acitt_options()
    ... multiple_angles=[NO (one angle)]
    ... multiple_channels=[YES (all channels in one file)]
    ... _____multiple_illumination_directions=[NO (one illumination direction)]
    ... multiple_tiles=[YES (all tiles in one file)]
    ... multiple_timepoints=[NO (one time-point)]
    """

    def __init__(self):
        self._angle_definition = SINGLE_FILE % "angle"
        self._channel_definition = MULTI_SINGLE_FILE % "channel"
        self._illumination_definition = SINGLE_FILE % "illumination direction"
        self._tile_definition = MULTI_MULTI_FILE % "tile"
        self._timepoint_definition = SINGLE_FILE % "time-point"

    def check_definition_option(self, value):
        """Check if the value is a valid definition option.

        Parameters
        ----------
        value : str
            Entered value by the user.

        Returns
        -------
        dict(str, str): dictionary containing the correct string definition.
        """
        valid = ["single", "multi_single", "multi_multi"]
        if value not in valid:
            raise ValueError("Value must be one of: %s" % valid)

        return {
            "single": SINGLE_FILE,
            "multi_single": MULTI_SINGLE_FILE,
            "multi_multi": MULTI_MULTI_FILE,
        }

    def check_definition_option_ang_ill(self, value):
        """Check if the value is a valid definition option.

        This is needed for angles and illuminations because support is not
        available for multiple angles and illuminations in a single file.

        Parameters
        ----------
        value : str
            Entered value by the user.

        Returns
        -------
        dict(str, str): dictionary containing the correct string definition.
        """
        valid = ["single", "multi_multi"]
        if value not in valid:
            raise ValueError(
                (
                    "Value must be one of: %s. Support for 'multi_single' is "
                    "not available for angles and illuminations."
                )
                % valid
            )

        return {
            "single": SINGLE_FILE,
            "multi_multi": MULTI_MULTI_FILE,
        }

    def set_angle_definition(self, value):
        """Set the value for the angle definition.

        Parameters
        ----------
        value : str
            One of `single` or `multi_multi`.
        """
        choices = self.check_definition_option_ang_ill(value)
        self._angle_definition = choices[value] % "angle"
        log.debug("New 'angle_definition' setting: %s", self._angle_definition)

    def set_channel_definition(self, value):
        """Set the value for the channel definition.

        Parameters
        ----------
        value : str
            One of `single`, `multi_single` or `multi_multi`.
        """
        choices = self.check_definition_option(value)
        self._channel_definition = choices[value] % "channel"
        log.debug(
            "New 'channel_definition' setting: %s",
            self._channel_definition,
        )

    def set_illumination_definition(self, value):
        """Set the value for the illumination definition.

        Parameters
        ----------
        value : str
            One of `single`, `multi_single` or `multi_multi`.
        """
        choices = self.check_definition_option_ang_ill(value)
        self._illumination_definition = choices[value] % "illumination direction"
        log.debug(
            "New 'illumination_definition' setting: %s",
            self._illumination_definition,
        )

    def set_tile_definition(self, value):
        """Set the value for the tile_definition.

        Parameters
        ----------
        value : str
            One of `single`, `multi_single` or `multi_multi`.
        """
        choices = self.check_definition_option(value)
        self._tile_definition = choices[value] % "tile"
        log.debug("New 'tile_definition' setting: %s", self._tile_definition)

    def set_timepoint_definition(self, value):
        """Set the value for the time_point_definition.

        Parameters
        ----------
        value : str
            One of `single`, `multi_single` or `multi_multi`.
        """
        choices = self.check_definition_option(value)
        self._timepoint_definition = choices[value] % "time-point"
        log.debug(
            "New 'timepoint_definition' setting: %s",
            self._timepoint_definition,
        )

    def fmt_acitt_options(self):
        """Format Angle / Channel / Illumination / Tile / Timepoint options.

        Build a string providing the `multiple_angles`, `multiple_channels`,
        `_____multiple_illumination_directions`, `multiple_tiles` and
        `multiple_timepoints` options that can be used in a BDV-related `IJ.run`
        call.

        Returns
        -------
        str
        """
        parameters = [
            "multiple_angles=" + self._angle_definition,
            "multiple_channels=" + self._channel_definition,
            # dialog label "_____Multiple_illumination_directions"
            "_____multiple_illumination_directions=" + self._illumination_definition,
            "multiple_tiles=" + self._tile_definition,
            "multiple_timepoints=" + self._timepoint_definition,
        ]
        parameter_string = " ".join(parameters).strip()
        log.debug("Formatted 'multiple_X' options: <%s>", parameter_string)
        return parameter_string + " "


def check_processing_input(value, range_end):
    """Sanitize and clarifies the acitt input selection.

    Validate the input by checking the type and returning the expected output.

    Parameters
    ----------
    value : str, int, list of int or list of str
        Contains the list of input dimensions, the first input dimension of a
        range or a single channel.
    range_end : int or None
        Contains the end of the range if need be.

    Returns
    -------
    str
        Returns the type of selection: single, multiple or range
    """
    if type(value) is not list:
        value = [value]
    # Check if all the elements of the value list are of the same type
    if not all(isinstance(x, type(value[0])) for x in value):
        raise TypeError("Invalid input, all values must be of the same type.")
    if type(range_end) is int:
        if type(value[0]) is not int:
            raise TypeError("Range start needs to be an int.")
        elif len(value) != 1:
            raise ValueError("Range start needs to be single number.")
        else:
            return "range"
    elif len(value) == 1:
        return "single"
    else:
        return "multiple"


def get_processing_settings(dimension, selection, value, range_end):
    """Generate processing strings for selected dimension and processing mode.

    Generate the processing option and dimension selection strings that
    correspond to the selected processing mode and the given dimension
    selection.

    Parameters
    ----------
    dimension : {`angle`, `channel`, `illumination`, `tile`, `timepoint`}
        The dimension selection to use.
    selection : {`single`, `multiple`, `range`}
        The *selector* name ("processing mode"), used to derive how the
        generated string needs to be assembled according to the given dimension
        and value / range settings.
    value : str, int, list of int or list of str
        The list of input dimensions, the first input dimension of a range or a
        single dimension value in case `selection == "single"` (e.g. for
        selecting a single channel).
    range_end : int or None
        Contains the end of the range if need be.

    Returns
    -------
    tuple of str
        processing_option, dimension_select
    """
    processing_option = dimension_select = ""

    # Validate inputs according to the function docstring
    valid_dimensions = ("angle", "channel", "illumination", "tile", "timepoint")
    if dimension not in valid_dimensions:
        raise ValueError(
            "Invalid dimension '%s', expected one of: %s"
            % (dimension, ", ".join(valid_dimensions))
        )

    valid_selections = ("single", "multiple", "range")
    if selection not in valid_selections:
        raise ValueError(
            "Invalid selection '%s', expected one of: %s"
            % (selection, ", ".join(valid_selections))
        )

    # the dialogs name timepoints "Timepoint" (capitalised), all other
    # dimensions by their lower-case attribute name
    label = "Timepoint" if dimension == "timepoint" else dimension

    if selection == "single":
        processing_option = SINGLE % label
        dimension_select = "processing_" + dimension + "=[" + label + " %s]" % value

    if selection == "multiple":
        processing_option = MULTIPLE % label
        dimension_list = ""
        for dimension_name in value:
            dimension_list += dimension + "_%s " % dimension_name
        dimension_select = dimension_list.rstrip()

    if selection == "range":
        processing_option = RANGE % label
        dimension_select = (
            "process_following_"
            + dimension
            + "s=%s-%s"
            % (
                value,
                range_end,
            )
        )

    return processing_option, dimension_select


def backup_xml_files(source_directory, subfolder_name):
    """Create a backup of BDV-XML files inside a subfolder of `xml-backup`.

    Copies all `.xml` and `.xml~` files to a subfolder with the given name
    inside a folder called `xml-backup` in the source directory. Uses the
    `shutil.copy2()` command, which will overwrite existing files.

    Parameters
    ----------
    source_directory : str
        Full path to the directory containing the xml files.
    subfolder_name : str
        The name of the subfolder that will be used inside `xml-backup`. Will be
        created if necessary.
    """
    xml_backup_directory = os.path.join(source_directory, "xml-backup")
    pathtools.create_directory(xml_backup_directory)
    backup_subfolder = xml_backup_directory + "/%s" % (subfolder_name)
    pathtools.create_directory(backup_subfolder)
    all_xml_files = pathtools.listdir_matching(source_directory, ".*\\.xml", regex=True)
    os.chdir(source_directory)
    for xml_file in all_xml_files:
        shutil.copy2(xml_file, backup_subfolder)


def define_dataset_auto(
    project_filename,
    file_path,
    bf_series_type,
    dataset_save_path=None,
    timepoints_per_partition=0,
    resave="Re-save as multiresolution HDF5",
    subsampling_factors=None,
    hdf5_chunk_sizes=None,
):
    """Define a dataset using the Autoloader or Multi-View loader.

    If the series is tiles, will run "Define Dataset...", otherwise will run
    "Define Multi-View Dataset...".

    Parameters
    ----------
    project_filename : str
        Name of the project (without an `.xml` extension).
    file_path : str
        Path to the file, can be the first `.czi` or a regex to match all files
        with an extension.
    dataset_save_path : str
        Output path for the `.xml`.
    bf_series_type : {`Angles`,`Tiles`}
        Defines how Bio-Formats interprets the series.
    timepoints_per_partition : int, optional
        Split the output dataset by timepoints. Use `0` for no split, resulting
        in a single HDF5 file containing all timepoints. Otherwise, choose the
        number of timepoints per file. By default `0`.
    
    resave : str, optional
        Allow the function to either re-save the images or simply create a
        merged xml. Use `Load raw data` to avoid re-saving, by default `Re-save
        as multiresolution HDF5` which will resave the input data.
    subsampling_factors : str, optional
        Specify subsampling factors explicitly, for example:
        `[{ {1,1,1}, {2,2,1}, {4,4,2}, {8,8,4} }]`.
    hdf5_chunk_sizes : str, optional
        Specify hdf5_chunk_sizes factors explicitly, for example
        `[{ {32,16,8}, {16,16,16}, {16,16,16}, {16,16,16} }]`.
    """

    file_info = pathtools.parse_path(file_path)

    project_filename = project_filename.replace(" ", "_")
    result_folder = pathtools.join2(file_info["path"], project_filename)

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    if not dataset_save_path:
        dataset_save_path = result_folder
    if subsampling_factors:
        subsampling_factors = (
            "manual_mipmap_setup subsampling_factors=" + subsampling_factors + " "
        )
    else:
        subsampling_factors = ""
    if hdf5_chunk_sizes:
        hdf5_chunk_sizes = "hdf5_chunk_sizes=" + hdf5_chunk_sizes + " "
    else:
        hdf5_chunk_sizes = ""
    if timepoints_per_partition > 0:
        split_timepoints = "split_hdf5 timepoints_per_partition=" + str(
            timepoints_per_partition
        ) + " "
    else:
        split_timepoints = ""

    if bf_series_type == "Angles":
        angle_rotation = "apply_angle_rotation "
    else:
        angle_rotation = ""

    options = (
        "define_dataset=[Automatic Loader (Bioformats based)]"
        + " "
        + "project_filename=["
        + project_filename
        + ".xml"
        + "] "
        + "path=["
        + file_info["full"]
        + "] "
        + "exclude=10 "
        + "bioformats_series_are?="
        + bf_series_type
        + " "
        + "move_tiles_to_grid_(per_angle)?=["
        + "Do not move Tiles to Grid (use Metadata if available)] "
        + "how_to_store_input_images=["
        + resave
        + "] "
        + "load_raw_data_virtually"
        + " "
        + "metadata_save_path=["
        + dataset_save_path
        + "] "
        + "image_data_save_path=["
        + dataset_save_path
        + "] "
        + "check_stack_sizes "
        + angle_rotation
        + subsampling_factors
        + hdf5_chunk_sizes
        + split_timepoints
        + "setups_per_partition=0 "
        + "use_deflate_compression "
    )

    log.debug(options)

    run_command("Define Multi-View Dataset", options)


def define_dataset_manual(
    project_filename,
    source_directory,
    image_file_pattern,
    dataset_organisation,
    definition_opts=None,
    list_files=None,
):
    """Run "Define Multi-View Dataset" using the "Manual Loader" option.

    Parameters
    ----------
    project_filename : str
        Name of the project (without an `.xml` extension).
    source_directory : str
        Path to the folder containing the file(s).
    image_file_pattern : str
        Regular expression corresponding to the names of your files and how to
        read the different dimensions.
    dataset_organisation : str
        Organisation of the dataset and the dimensions to process. Allows for
        defining the range(s) of interest for the different dimensions, for
        example: `timepoints_=%s-%s channels_=0-%s tiles_=%s-%s`.
    definition_opts : dict
        Dictionary containing the details about the file repartitions.
    list_files : list of str, optional
        An optional list of file names to pass directly to the manual loader in
        "show_list" mode. When provided, the function will include the filenames
        in the options string instead of relying on a file pattern; items should
        be either full paths or relative to the selected `source_directory`.
    """
    # xml_filename = project_filename + ".xml"

    if definition_opts is None:
        definition_opts = DefinitionOptions()

    show_list_options = "" if not list_files else "show_list " + " ".join(list_files)

    options = (
        "define_dataset=[Manual Loader (Bioformats based)] "
        + "project_filename=["
        + project_filename
        + "] "
        + "_____"
        + definition_opts.fmt_acitt_options()
        + " "
        + "image_file_directory="
        + source_directory
        + " "
        + "image_file_pattern="
        + image_file_pattern
        + " "
        + dataset_organisation
        + " "
        + "calibration_type=[Same voxel-size for all views] "
        + "calibration_definition=[Load voxel-size(s) from file(s)] "
        + show_list_options
    )

    log.debug("Manual dataset definition options: <%s>", options)
    run_command("Define Multi-View Dataset", options)


def resave_as_h5(
    source_xml_file,
    output_h5_file_path,
    processing_opts=None,
    timepoints_per_partition=1,
    use_deflate_compression=True,
    subsampling_factors=None,
    hdf5_chunk_sizes=None,
):
    """Resave the xml dataset in a new format (either all or single timepoints).

    Useful if it hasn't been done during dataset definition (see
    `define_dataset_auto()`). Allows e.g. parallelization of HDF-5 re-saving.

    Parameters
    ----------
    source_xml_file : File or str
        XML input file.
    output_h5_file_path : str
        Export path for the output file including the `.xml `extension.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    timepoints_per_partition : int, optional
        How many timepoints to export per partition, by default `1`.
    use_deflate_compression : bool, optional
        Run deflate compression, by default `True`.
    subsampling_factors : str, optional
        Specify subsampling factors explicitly, for example:
        `[{ {1,1,1}, {2,2,1}, {4,4,2}, {8,8,4} }]`.
    hdf5_chunk_sizes : str, optional
        Specify hdf5_chunk_sizes factors explicitly, for example
        `[{ {32,16,8}, {16,16,16}, {16,16,16}, {16,16,16} }]`.
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    if use_deflate_compression:
        use_deflate_compression_arg = "use_deflate_compression "
    else:
        use_deflate_compression_arg = ""

    # If split_hdf5 option
    if timepoints_per_partition != 0:
        split_hdf5 = "split_hdf5 "
    else:
        split_hdf5 = ""

    if subsampling_factors:
        subsampling_factors = "subsampling_factors=" + subsampling_factors + " "
    else:
        subsampling_factors = " "
    if hdf5_chunk_sizes:
        hdf5_chunk_sizes = "hdf5_chunk_sizes=" + hdf5_chunk_sizes + " "
    else:
        hdf5_chunk_sizes = " "

    options = (
        "select="
        + str(source_xml_file)
        + " "
        + processing_opts.fmt_acitt_options("resave")
        + processing_opts.fmt_acitt_selectors()
        + subsampling_factors
        + hdf5_chunk_sizes
        + "timepoints_per_partition="
        + str(timepoints_per_partition)
        + " "
        + "setups_per_partition=0 "
        + use_deflate_compression_arg
        + split_hdf5
        + "export_path="
        + output_h5_file_path
    )

    log.debug("Resave as HDF5 options: <%s>", options)
    IJ.run("Resave as HDF5 (local)", str(options))


def flip_axes(source_xml_file, x=False, y=True, z=False):
    """Call BigStitcher's "Flip Axes" command.

    Wrapper for `BigStitcher > Batch Processing > Tools > Flip Axes`. This is
    required for some formats, for example Nikon `.nd2` files need a flip along
    the Y-axis.

    Parameters
    ----------
    source_xml_file : str
        Full path to the `.xml` file.
    x : bool, optional
        Flip images along the X-axis, by default `False`.
    y : bool, optional
        Flip mages along the Y-axis, by default `True`.
    z : bool, optional
        Flip images along the Z-axis, by default `False`.
    """

    file_info = pathtools.parse_path(source_xml_file)

    axes_to_flip = ""
    if x is True:
        axes_to_flip += " flip_x"
    if y is True:
        axes_to_flip += " flip_y"
    if z is True:
        axes_to_flip += " flip_z"

    IJ.run("Flip Axes", "select=" + source_xml_file + axes_to_flip)

    backup_xml_files(file_info["path"], "flip_axes")


def phase_correlation_pairwise_shifts_calculation(
    project_path,
    processing_opts=None,
    downsampling_xyz="",
    backup_xml=True,
):
    """Calculate pairwise shifts using Phase Correlation.

    Parameters
    ----------
    project_path : str
        Full path to the `.xml` file.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    downsampling_xyz : list of int, optional
        Downsampling factors in X, Y and Z, for example `[4,4,4]`. By default
        empty which will result in BigStitcher choosing the factors.
    backup_xml : bool, optional
        Copy the XML files to `xml-backup/` afterwards (default `True`).
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)

    if downsampling_xyz != "":
        downsampling = "downsample_in_x=%s downsample_in_y=%s downsample_in_z=%s " % (
            downsampling_xyz[0],
            downsampling_xyz[1],
            downsampling_xyz[2],
        )
    else:
        downsampling = ""

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + " "
        + "method=[Phase Correlation] "
        + "show_expert_grouping_options "
        + "show_expert_algorithm_parameters "
        + processing_opts.fmt_use_acitt()
        + processing_opts.fmt_how_to_treat()
        + downsampling
        + "subpixel_accuracy"
    )

    log.debug("Calculate pairwise shifts options: <%s>", options)
    run_command("Calculate pairwise shifts ...", options)

    if backup_xml:
        backup_xml_files(file_info["path"], "phase_correlation_shift_calculation")


def filter_pairwise_shifts(
    project_path,
    min_r=0.7,
    max_r=1,
    max_shift_xyz="",
    max_displacement="",
    backup_xml=True,
):
    """Filter the pairwise shifts based on different thresholds.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` on which to apply the filters.
    min_r : float, optional
        Minimal quality of the link to keep, by default `0.7`.
    max_r : float, optional
        Maximal quality of the link to keep, by default `1`.
    max_shift_xyz : list(int), optional
        Maximal shift in X, Y and Z (in pixels) to keep, e.g. `[10,10,10]`. By
        default empty, meaning no filtering based on the shifts will be applied.
    max_displacement : int, optional
        Maximal displacement to keep. By default empty, meaning no filtering
        based on the displacement will be applied.
    backup_xml : bool, optional
        Copy the XML files to `xml-backup/` afterwards (default `True`).
    """

    file_info = pathtools.parse_path(project_path)

    if max_shift_xyz != "":
        filter_by_max_shift = (
            " filter_by_shift_in_each_dimension"
            " max_shift_in_x=%s max_shift_in_y=%s max_shift_in_z=%s"
        ) % (max_shift_xyz[0], max_shift_xyz[1], max_shift_xyz[2])
    else:
        filter_by_max_shift = ""

    if max_displacement != "":
        filter_by_max_displacement = (
            " filter_by_total_shift_magnitude max_displacement=%s"
        ) % (max_displacement)
    else:
        filter_by_max_displacement = ""

    options = (
        "select=["
        + project_path
        + "] "
        + "filter_by_link_quality "
        + "min_r="
        + str(min_r)
        + " "
        + "max_r="
        + str(max_r)
        + filter_by_max_shift
        + filter_by_max_displacement
    )

    log.debug("Filter pairwise options: <%s>", options)
    run_command("Filter pairwise shifts ...", options)

    if backup_xml:
        backup_xml_files(file_info["path"], "filter_pairwise_shifts")


def optimize_and_apply_shifts(
    project_path,
    processing_opts=None,
    relative_error=2.5,
    absolute_error=3.5,
    strategy="Two-Round using Metadata to align unconnected Tiles and "
    + "iterative dropping of bad links",
    fix_groups=None,
    pre_align=True,
    backup_xml=True,
):
    """Optimize the shifts and apply them to the dataset.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` on which to optimize and apply the shifts.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    relative_error : float, optional
        Relative alignment error (in px) to accept, by default `2.5`.
    absolute_error : float, optional
        Absolute alignment error (in px) to accept, by default `3.5`.
    strategy : str, optional
        The global optimization strategy (without brackets), by default
        `Two-Round using Metadata to align unconnected Tiles and iterative
        dropping of bad links`. Note: the plain variant is spelled `Two-Round
        using metadata to align unconnected Tiles` (lower-case "m").
    fix_groups : list of str, optional
        Groups to fix, as in the checkbox labels `Fix_Group_<views>` cut at the
        first space, e.g. `["0-0"]` if every view is its own group or
        `["0-0,"]` if view 0 shares a group (`0-0, 0-24`). Keys that do not
        exist are ignored, so both variants can be given. By default `None`
        (BigStitcher fixes nothing and does not fall back to a default view).
    pre_align : bool, optional
        Pre-align the tiles before the optimization, by default `True` (MVR
        <= 7 always did; MVR 9 only if the `pre-align` key is given).
    backup_xml : bool, optional
        Copy the XML files to `xml-backup/` afterwards (default `True`).
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)

    fix = "".join("fix_group_%s " % group for group in (fix_groups or []))

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + " "
        + "relative="
        + str(relative_error)
        + " "
        + "absolute="
        + str(absolute_error)
        + " "
        + "global_optimization_strategy=["
        + strategy
        + "] "
        + "show_expert_grouping_options "
        + processing_opts.fmt_use_acitt()
        + processing_opts.fmt_how_to_treat()
        + fix
        + ("pre-align " if pre_align else "")
    )

    log.debug("Optimization and shifts application options: <%s>", options)
    run_command("Optimize globally and apply shifts ...", options)

    if backup_xml:
        backup_xml_files(file_info["path"], "optimize_and_apply_shifts")


def detect_interest_points(
    project_path,
    processing_opts=None,
    sigma=1.8,
    threshold=0.008,
    maximum_number=3000,
    label="beads",
    downsample_xy=8,
    downsample_z=2,
    min_intensity=None,
    max_intensity=None,
    group_tiles=True,
    group_illuminations=False,
):
    """Run the "Detect Interest Points" command for registration.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` project.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    sigma : float, optional
        Minimum sigma for interest points detection, by default `1.8`.
    threshold : float, optional
        Threshold value for the interest point detection, by default `0.008`.
        Relative to the intensity range (`min_intensity` .. `max_intensity`,
        by default the min .. max of each view).
    maximum_number : int, optional
        Maximum number of interest points to use, by default `3000`.
    label : str, optional
        Label of the interest points, by default `beads`.
    downsample_xy : int, optional
        Downsampling in X and Y before the detection (1, 2, 4 or 8), by
        default `8`.
    downsample_z : int, optional
        Downsampling in Z before the detection (1, 2, 4 or 8), by default `2`.
    min_intensity, max_intensity : float, optional
        Fixed intensity range for all views (`set_minimal_and_maximal_intensity`).
        By default `None`: each view is normalised to its own min .. max, which
        makes the threshold mean different things in bright and dim views.
    group_tiles : bool, optional
        Combine the tiles of a view into one detection, by default `True`.
    group_illuminations : bool, optional
        Combine the illuminations of a view, by default `False`.
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    if min_intensity is not None and max_intensity is not None:
        intensity = (
            "set_minimal_and_maximal_intensity "
            + "minimal_intensity="
            + str(min_intensity)
            + " "
            + "maximal_intensity="
            + str(max_intensity)
            + " "
        )
    else:
        intensity = ""

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + "type_of_interest_point_detection=Difference-of-Gaussian "
        + "label_interest_points="
        + label
        + " "
        + "limit_amount_of_detections "
        + ("group_tiles " if group_tiles else "")
        + ("group_illuminations " if group_illuminations else "")
        + "subpixel_localization=[3-dimensional quadratic fit] "
        + "interest_point_specification=[Advanced ...] "
        + "downsample_xy="
        + str(downsample_xy)
        + "x "
        + "downsample_z="
        + str(downsample_z)
        + "x "
        + "sigma="
        + str(sigma)
        + " "
        + "threshold="
        + str(threshold)
        + " "
        + "find_maxima "
        + intensity
        + "maximum_number="
        + str(maximum_number)
        + " "
        + "type_of_detections_to_use=Brightest "
        + "compute_on=[CPU (Java)]"
    )

    log.debug("Interest points detection options: <%s>", options)
    run_command("Detect Interest Points for Registration", options)


def fmt_ransac_options(
    max_error=5,
    min_inliers=None,
    iterations="Normal (10,000)",
    min_inlier_ratio=None,
    max_trust=None,
):
    """Format the RANSAC options of the interest point registration.

    Valid for multiview-reconstruction 9.x. MVR 7 used an `inlier_factor`
    instead of an absolute number of inliers and the iteration choices "Fast",
    "Normal", ... without the counts.

    Parameters
    ----------
    max_error : float, optional
        Allowed error for RANSAC in px, by default `5`.
    min_inliers : int, optional
        Minimal number of inliers per link (`minmal_number_of_inliers`, typo
        as in MVR). By default `None`, i.e. MVR's default (12).
    iterations : str, optional
        One of `Fast (1,000)`, `Normal (10,000)` (default), `Thorough (10^5)`,
        `Very thorough (10^6)`, `Ridiculous (10^7)`.
    min_inlier_ratio : float, optional
        Minimal inlier ratio (advanced RANSAC dialog). By default `None`, i.e.
        MVR's default (0.05; MVR 7 used 0.1).
    max_trust : float, optional
        Maximal trust, a factor of the median residual (advanced RANSAC
        dialog). By default `None`, i.e. MVR's default (3; MVR 7 used 4).

    Returns
    -------
    str
    """
    options = (
        "allowed_error_for_ransac="
        + str(max_error)
        + " "
        + "ransac_iterations=["
        + iterations
        + "] "
    )
    if min_inliers is not None:
        options += "minmal_number_of_inliers=" + str(min_inliers) + " "
    if min_inlier_ratio is not None or max_trust is not None:
        options += "advanced_ransac_options filter_ransac "
        if min_inlier_ratio is not None:
            options += "minimal_inlier_ratio=" + str(min_inlier_ratio) + " "
        if max_trust is not None:
            options += "maximal_trust=" + str(max_trust) + " "
    return options


def interest_points_registration(
    project_path,
    processing_opts=None,
    rigid_timepoints=False,
    label="beads",
    transformation="Affine",
    regularize_with="Affine",
    regularization_lambda=0.1,
    group_tiles=True,
    group_illuminations=True,
    group_channels=True,
    merge_distance=5,
    view_selection="Only compare overlapping views (according to current "
    + "transformations)",
    point_selection="Compare all interest point of overlapping views",
    number_of_neighbors=3,
    redundancy=1,
    significance=3,
    search_radius=None,
    ransac_options=None,
    strategy="Two-Round: Handle unconnected tiles, remove wrong links RELAXED "
    + "(5.0x / 7.0px)",
    fix_views=None,
    pre_align=True,
):
    """Run the "Register Dataset based on Interest Points" command.

    Uses the "Precise descriptor-based (translation invariant)" algorithm. The
    defaults reproduce the earlier behaviour of this function (Affine,
    regularised with Affine, all groups, RELAXED).

    Parameters
    ----------
    project_path : str
        Path to the `.xml` project.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped. This controls which angles, channels,
        illuminations, tiles and timepoints are processed.
    rigid_timepoints : bool, optional
        If set to `True` each timepoint will be considered as a rigid unit
        (useful e.g. if spatial registration has already been performed before).
        By default `False`.
    label : str, optional
        Label of the interest points, by default `beads`.
    transformation : str, optional
        `Translation`, `Rigid` or `Affine` (default).
    regularize_with : str or None, optional
        Model to regularize with (`Translation`, `Rigid`, `Affine`), by default
        `Affine`; `None` for no regularization.
    regularization_lambda : float, optional
        Weight of the regularization model, by default `0.1`.
    group_tiles, group_illuminations, group_channels : bool, optional
        Combine the interest points of the tiles / illuminations / channels of
        a view into one virtual view, by default `True`.
    merge_distance : float, optional
        Distance (px) below which grouped points are merged, by default `5`.
    view_selection : str, optional
        Which views to compare (choice without brackets), by default only
        overlapping views.
    point_selection : str, optional
        Which points to compare (choice without brackets), by default all
        points of overlapping views; `Only compare interest points that overlap
        between views (according to current transformations)` restricts them
        to the overlaps.
    number_of_neighbors, redundancy, significance : int, optional
        Descriptor parameters, by default `3`, `1` and `3`.
    search_radius : float, optional
        Only pair descriptors whose points are within this distance (px) under
        the current transformations (`limit_search_radius`). By default `None`
        (no limit).
    ransac_options : str, optional
        RANSAC options from `fmt_ransac_options()`, by default
        `fmt_ransac_options()` (MVR defaults, 10,000 iterations).
    strategy : str, optional
        The global optimization strategy (without brackets), by default
        `Two-Round: Handle unconnected tiles, remove wrong links RELAXED (5.0x
        / 7.0px)`.
    fix_views : str, optional
        The `fix_views` choice, e.g. `Fix first view`, together with `Do not
        map back (use this if views are fixed)`. By default `None` (dialog
        default; with a single timepoint that is `Fix first view`).
    pre_align : bool, optional
        Pre-align the views before the global optimization, by default `True`
        (MVR <= 7 always did; MVR 9 only if the `pre-align` key is given).
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    if rigid_timepoints:
        rigid_timepoints_arg = "consider_each_timepoint_as_rigid_unit "
    else:
        rigid_timepoints_arg = " "

    if ransac_options is None:
        ransac_options = fmt_ransac_options()

    if regularize_with:
        regularize = (
            "regularize_model "
            + "model_to_regularize_with="
            + regularize_with
            + " "
            + "lambda="
            + str(regularization_lambda)
            + " "
        )
    else:
        regularize = ""

    grouping = (
        ("group_tiles " if group_tiles else "")
        + ("group_illuminations " if group_illuminations else "")
        + ("group_channels " if group_channels else "")
    )
    if grouping:
        grouping += (
            "interestpoint_grouping=["
            + "Group interest points (simply combine all in one virtual view)] "
            + "interest="
            + str(merge_distance)
            + " "
        )

    if search_radius is not None:
        radius = "limit_search_radius search_radius=" + str(search_radius) + " "
    else:
        radius = ""

    if fix_views:
        fix = (
            "fix_views=["
            + fix_views
            + "] "
            + "map_back_views=[Do not map back (use this if views are fixed)] "
        )
    else:
        fix = ""

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + "registration_algorithm=[Precise descriptor-based (translation invariant)] "
        + "registration_over_time=["
        + "Match against one reference timepoint (no global optimization)] "
        + "registration_in_between_views=["
        + view_selection
        + "] "
        + "interest_point_inclusion=["
        + point_selection
        + "] "
        + "interest_points="
        + label
        + " "
        + grouping
        + "reference=1 "
        + rigid_timepoints_arg
        + fix
        + "transformation="
        + transformation
        + " "
        + regularize
        + "number_of_neighbors="
        + str(number_of_neighbors)
        + " "
        + "redundancy="
        + str(redundancy)
        + " "
        + "significance="
        + str(significance)
        + " "
        + radius
        + ransac_options
        + "global_optimization_strategy=["
        + strategy
        + "] "
        + ("pre-align" if pre_align else "")
    )

    log.debug("Interest points registration options: <%s>", options)
    # register using interest points
    run_command("Register Dataset based on Interest Points", options)


def duplicate_transformations(
    project_path,
    transformation_type="channel",
    channel_source=0,
    tile_source=None,
    transformation_to_use="[Replace all transformations]",
):
    """Duplicate / propagate transformation parameters to other channels.

    Propagate the transformation parameters generated by a previously performed
    registration of a single channel to the other channels.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` project.
    transformation_type : str, optional
        Transformation mode, one of `channel` (to propagate from one channel to
        all others) and `tiles` (to propagate from one tile to all others).
    channel_source : int, optional
        Reference channel number (starting at 1), by default None.
    tile_source : int, optional
        Reference tile, by default None.
    transformation_to_use : str, optional
        One of `[Replace all transformations]` (default) and `[Add last
        transformation only]` to specify which transformations to propagate.
    """

    file_info = pathtools.parse_path(project_path)

    apply = ""
    source = ""
    target = ""
    tile_apply = ""
    tile_process = ""

    ch_apply = ""
    ch_process = ""

    if transformation_type == "channel":
        apply = "[One channel to other channels]"
        target = "[All Channels]"
        if channel_source > 0:
            source = str(channel_source - 1)
        else:
            source = "0"
        if tile_source:
            tile_apply = "apply_to_tile=[Single tile (Select from List)] "
            tile_process = "processing_tile=[tile " + str(tile_source) + "] "
        else:
            tile_apply = "apply_to_tile=[All tiles] "
    elif transformation_type == "tile":
        apply = "[One tile to other tiles]"
        target = "[All Tiles]"
        source = str(tile_source)
        if channel_source > 0:
            ch_apply = "apply_to_channel=[Single channel (Select from List)] "
            ch_process = "processing_channel=[channel " + str(channel_source - 1) + "] "
        else:
            ch_apply = "apply_to_channel=[All channels] "
    else:
        raise ValueError("Invalid transformation type: %s" % transformation_type)

    options = (
        "apply="
        + apply
        + " "
        + "select=["
        + project_path
        + "] "
        + "apply_to_angle=[All angles] "
        + "apply_to_illumination=[All illuminations] "
        + tile_apply
        + tile_process
        + ch_apply
        + ch_process
        + "apply_to_timepoint=[All Timepoints] "
        + "source="
        + source
        + " "
        + "target="
        + target
        + " "
        + "duplicate_which_transformations="
        + transformation_to_use
        + " "
    )

    log.debug("Transformation duplication options: <%s>", options)
    run_command("Duplicate Transformations", options)

    backup_xml_files(
        file_info["path"],
        "duplicate_transformation_" + transformation_type,
    )


def export_choice(export):
    """Get the `export=` value of "OME-ZARR/N5/HDF5 export using N5-API".

    Choices of multiview-reconstruction 9.x: `N5`, `OME-ZARR v3`, `OME-ZARR v2
    (deprecated)` and `HDF5 (currently not supported)`.

    Parameters
    ----------
    export : {`N5`, `OME-ZARR`}
        The format; `OME-ZARR` is written as OME-ZARR v3.

    Returns
    -------
    str
        The choice in brackets, e.g. `[OME-ZARR v3]`.

    Raises
    ------
    ValueError
        For HDF5 (not available in MVR 9.x) and unknown formats.
    """
    choices = {"N5": "[N5]", "OME-ZARR": "[OME-ZARR v3]"}
    if export not in choices:
        raise ValueError(
            "No export option for %s in MVR 9.x (HDF5 is not available, use N5 "
            "or OME-ZARR)" % export
        )
    return choices[export]


def fuse_dataset(
    project_path,
    processing_opts=None,
    result_path=None,
    downsampling=1,
    interpolation="[Linear Interpolation]",
    pixel_type="[16-bit unsigned integer]",
    fusion_type="Avg, Blending",
    export="TIFF",
    compression="Zstandard",
    bounding_box="All Views",
    preserve_original=True,
    non_rigid_label=None,
    non_rigid_alpha=1.0,
    non_rigid_cpd=10,
    filename_addition=None,
    output_basename=None,
    block_size=(128, 128, 64),
    block_size_factor=(2, 2, 2),
    subsampling_factors="",
    sharding=True,
    single_container=True,
):
    """Call BigStitcher's "Fuse Dataset" command.

    Wrapper to `BigStitcher > Batch Processing > Fuse Dataset`.

    Depending on the export type, inputs are different and therefore will
    distribute inputs differently. TIFF stacks are written uncompressed (one
    file per timepoint and channel). N5 and OME-ZARR always get a
    multi-resolution pyramid and a BDV/BigStitcher XML.

    Note: MVR keeps the last values of its dialogs for the rest of the Fiji
    session, so an option missing from the macro string is not MVR's default
    but the value of the previous fusion. Compression and block sizes are
    therefore always passed (defaults = MVR's initial values); only the pyramid
    levels can be left to MVR, which proposes them for each fused image.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` on which to run the fusion.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptions` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    result_path : str, optional
        Path to store the resulting fused image, by default `None` which will
        store the result in the same folder as the input project.
    downsampling : int, optional
        Downsampling value to use during fusion, by default `1`.
    interpolation : str, optional
        Interpolation to use during fusion, by default `[Linear Interpolation]`.
    pixel_type : str, optional
        Pixel type to use during fusion, by default `[16-bit unsigned integer]`.
    export : {`TIFF`, `N5`, `OME-ZARR`}, optional
        Format of the output fused image, by default `TIFF` (uncompressed;
        MVR's "Save as (compressed) TIFF stacks" never compresses). `N5` and
        `OME-ZARR` (OME-ZARR v3) write chunked containers in parallel. `HDF5`
        is not available in MVR 9.x and raises a `ValueError`.
    fusion_type : str, optional
        Type of fusion algorithm to use, by default `Avg, Blending`.
    compression : str, optional
        N5 / OME-ZARR only: one of `Lz4`, `Gzip`, `Zstandard`, `Blosc`,
        `Bzip2`, `Xz`, `Raw (no compression)`. By default `Zstandard` (MVR's
        default).
    bounding_box : str, optional
        Name of the bounding box to fuse (without brackets), by default `All
        Views`.
    preserve_original : bool, optional
        Keep the anisotropy of the input (z in planes) at downsampling 1, by
        default `True`. Ignored by MVR for downsampling > 1.
    non_rigid_label : str, optional
        Interest point label for a non-rigid fusion (moving least squares on
        the stored correspondences). By default `None` (rigid). MVR fuses
        views with fewer than 12 correspondences with their affine model. Note
        (MVR 7.0.7 - 9.0.11): the non-rigid fusion ignores the minimum of the
        bounding box (fuses world 0 .. max), and the label is only found if
        every fused view has correspondences of it.
    non_rigid_alpha : float, optional
        Alpha of the moving least squares, by default `1.0`.
    non_rigid_cpd : int, optional
        Control point distance in output voxels, by default `10`.
    filename_addition : str, optional
        TIFF only: prefix of the file names (`<addition>_fused_tp_<t>_ch_<c>.tif`).
        By default `None`, i.e. the project's base name.
    output_basename : str, optional
        N5 / OME-ZARR only: base name of the container and its XML. By
        default `None`, i.e. `<project basename>_fused`.
    block_size : list of int, optional
        N5 / OME-ZARR only: block (chunk) size in X, Y and Z, by default
        `(128, 128, 64)` (MVR's default). N5 writes one file per block.
    block_size_factor : list of int, optional
        N5 / OME-ZARR only: compute block size as a factor of the block size in
        X, Y and Z; with OME-ZARR sharding also the shard size (one file per
        shard). By default `(2, 2, 2)` (MVR's default).
    subsampling_factors : str, optional
        N5 / OME-ZARR only: downsampling factors of the pyramid levels, e.g.
        `{ {1,1,1}, {2,2,1}, {4,4,2} }`. By default `""`, i.e. the levels
        BigStitcher proposes for the size of the fused image (data dependent).
    sharding : bool, optional
        OME-ZARR only: group blocks into shards (fewer files), by default
        `True` (BigStitcher's default).
    single_container : bool, optional
        OME-ZARR only: store channels and timepoints in a single OME-ZARR
        container, by default `True` (BigStitcher's default).

    Raises
    ------
    ValueError
        If `export` is `HDF5` or unknown.
    """

    if processing_opts is None:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)
    if not result_path:
        result_path = file_info["path"]
        # if not os.path.exists(result_path):
        #     os.makedirs(result_path)

    if non_rigid_label:
        non_rigid = (
            "interest_points_for_non_rigid=["
            + non_rigid_label
            + "] "
            + "non_rigid_advanced_parameters "
            + "alpha="
            + str(non_rigid_alpha)
            + " "
            + "control_point_distance="
            + str(non_rigid_cpd)
            + " "
        )
    else:
        non_rigid = "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] "

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + "bounding_box=["
        + bounding_box
        + "] "
        + "downsampling="
        + str(downsampling)
        + " "
        + "interpolation="
        + interpolation
        + " "
        + "fusion_type=["
        + fusion_type
        + "] "
        + "pixel_type="
        + pixel_type
        + " "
        + non_rigid
        + ("preserve_original " if preserve_original else "")
        + "produce=[Each timepoint & channel] "
    )

    if export == "TIFF":
        if filename_addition is None:
            filename_addition = file_info["basename"]
        options = (
            options
            + "fused_image=[Save as (compressed) TIFF stacks] "
            + "define_input=[Auto-load from input data (values shown below)] "
            + "output_file_directory=["
            + result_path
            + "/.] "
            + "filename_addition=["
            + filename_addition
            + "]"
        )
    elif export in ("N5", "OME-ZARR"):
        if output_basename is None:
            output_basename = file_info["basename"] + "_fused"
        extension = {"N5": ".n5", "OME-ZARR": ".zarr"}[export]
        path_key = {"N5": "n5_dataset_path", "OME-ZARR": "zarr_dataset_path"}[export]
        data_path = pathtools.join2(result_path, output_basename + extension)
        xml_fused_path = pathtools.join2(result_path, output_basename + ".xml")

        options = (
            options
            + "fused_image=[OME-ZARR/N5/HDF5 export using N5-API] "
            + "define_input=[Auto-load from input data (values shown below)] "
            + "export="
            + export_choice(export)
            + " "
            + "create_a_bdv/bigstitcher "
            + "create_multi-resolution "
            + path_key
            + "=["
            + data_path
            + "] "
            + "xml_output_file=["
            + xml_fused_path
            + "] "
        )
        options = options + "compression=[" + compression + "] "
        if export == "OME-ZARR":
            # checkboxes missing from a macro are off, so the defaults are
            # passed explicitly
            options = (
                options
                + ("store_channels " if single_container else "")
                + ("enable_sharding " if sharding else "")
            )
        options = options + (
            "show_advanced_block_size_options "
            + "block_size_x=%s block_size_y=%s block_size_z=%s " % tuple(block_size)
            + "block_size_factor_x=%s block_size_factor_y=%s block_size_factor_z=%s "
            % tuple(block_size_factor)
        )
        if subsampling_factors:
            options = options + "subsampling_factors=[" + subsampling_factors + "] "
    elif export == "HDF5":
        raise ValueError(
            "HDF5 export is not available in multiview-reconstruction 9.x, use "
            "TIFF, N5 or OME-ZARR"
        )
    else:
        raise ValueError("Unknown export format: %s" % export)

    log.debug("Dataset fusion options: <%s>", options)
    run_command("Image Fusion", options)


def fuse_dataset_bdvp(
    project_path,
    command,
    result_path=None,
    fusion_method="SMOOTH AVERAGE",
    range_channels="",
    range_slices="",
    range_frames="",
    n_resolution_levels=5,
    use_lzw_compression=True,
    split_slices=False,
    split_channels=False,
    split_frames=False,
    override_z_ratio=False,
    z_ratio=1.0,
    use_interpolation=True,
):
    """Export a project using the BigDataViewer playground (`bdvp`) exporter.

    Use the BigDataViewer playground / BIOP Kheops exporter to fuse a
    BigDataViewer project and save it as pyramidal OME-TIFF.

    Parameters
    ----------
    project_path : str
        Full path to the BigDataViewer XML project file.
    command : CommandService
        The Scijava CommandService instance to execute the export command.
    result_path : str, optional
        Path where to store the exported files. If `None`, files will be
        saved in the same directory as the input project.
    fusion_method : str, optional
        Fusion method to use for exporting (default `SMOOTH AVERAGE`).
    range_channels : str, optional
        Channels to include in the export. Default is all channels.
    range_slices : str, optional
        Slices to include in the export. Default is all slices.
    range_frames : str, optional
        Frames to include in the export. Default is all frames.
    n_resolution_levels : int, optional
        Number of pyramid resolution levels to use for the export. Default is 5.
    use_lzw_compression : bool, optional
        Compress the output file using LZW. Default is True.
    split_slices : bool, optional
        Split output into separate files for each slice. Default is False.
    split_channels : bool, optional
        Split output into separate files for each channel. Default is False.
    split_frames : bool, optional
        Split output into separate files for each frame. Default is False.
    override_z_ratio : bool, optional
        Override the default `z_ratio` value. Default is False.
    z_ratio : float, optional
        The z ratio to use for the export. Default is 1.0.
    use_interpolation : bool, optional
        Interpolate during fusion (takes ~4x longer). Default is True.

    Notes
    -----
    Requires the `PTBIOP` update site to be enabled in Fiji/ImageJ.

    Examples
    --------
    Example 1 - simple export using a CommandService instance available as
    `command`, using the default options and placing the output  next to the
    input xml:

    >>> #@ CommandService command
    >>> xml_input = "/path/to/project.xml"
    >>> fuse_dataset_bdvp(xml_input, command)

    Example 2 - explicit options using a custom output path, specific channels,
    disabling interpolation and overriding the z-ratio:

    >>> #@ CommandService command
    >>> xml_input = "/path/to/project.xml"
    >>> out_dir = "/path/to/output_dir"
    >>> fuse_dataset_bdvp(
    ...     xml_input,
    ...     command,
    ...     result_path=out_dir,
    ...     fusion_method="SMOOTH AVERAGE",
    ...     range_channels="0-1",
    ...     n_resolution_levels=4,
    ...     use_lzw_compression=False,
    ...     split_channels=True,
    ...     override_z_ratio=True,
    ...     z_ratio=2.0,
    ...     use_interpolation=False,
    ... )
    """
    # imported here: needs the PTBIOP update site, the other functions of this
    # module do not
    from ch.epfl.biop.scijava.command.spimdata import (
        FuseBigStitcherDatasetIntoOMETiffCommand,
    )

    file_info = pathtools.parse_path(project_path)

    if not result_path:
        result_path = file_info["path"]

    command.run(
        FuseBigStitcherDatasetIntoOMETiffCommand,
        True,  # seems to indicate whether to run the command headless or not
        "xml_bigstitcher_file",
        project_path,
        "output_path_directory",
        result_path,
        "range_channels",
        range_channels,
        "range_slices",
        range_slices,
        "range_frames",
        range_frames,
        "n_resolution_levels",
        n_resolution_levels,
        "fusion_method",
        fusion_method,
        "use_lzw_compression",
        use_lzw_compression,
        "split_slices",
        split_slices,
        "split_channels",
        split_channels,
        "split_frames",
        split_frames,
        "override_z_ratio",
        override_z_ratio,
        "z_ratio",
        z_ratio,
        "use_interpolation",
        use_interpolation,
    ).get()
