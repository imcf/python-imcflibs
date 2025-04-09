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

from ch.epfl.biop.scijava.command.spimdata import (
    FuseBigStitcherDatasetIntoOMETiffCommand,
)
from ij import IJ

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
        self._use_timepoint = "timepoints=[Average Timepoints]"

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
        self._use_timepoint = "timepoints=[use Timepoint %s]" % value
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
    ... multiple_illuminations_directions=[NO (one illumination direction)]
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
        `multiple_illuminations_directions`, `multiple_tiles` and
        `multiple_timepoints` options that can be used in a BDV-related `IJ.run`
        call.

        Returns
        -------
        str
        """
        parameters = [
            "multiple_angles=" + self._angle_definition,
            "multiple_channels=" + self._channel_definition,
            "multiple_illuminations_directions=" + self._illumination_definition,
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

    if selection == "single":
        processing_option = SINGLE % dimension
        dimension_select = "processing_" + dimension + "=[" + dimension + " %s]" % value

    if selection == "multiple":
        processing_option = MULTIPLE % dimension
        dimension_list = ""
        for dimension_name in value:
            dimension_list += dimension + "_%s " % dimension_name
        dimension_select = dimension_list.rstrip()

    if selection == "range":
        processing_option = RANGE % dimension
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
    timepoints_per_partition=1,
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
        in a single HDF5 file containing all timepoints. By default `1`,
        resulting in a HDF5 per timepoints.
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
        + "split_hdf5 "
        + "timepoints_per_partition="
        + str(timepoints_per_partition)
        + " "
        + "setups_per_partition=0 "
        + "use_deflate_compression "
    )

    log.debug(options)

    IJ.run("Define Multi-View Dataset", str(options))


def define_dataset_manual(
    project_filename,
    source_directory,
    image_file_pattern,
    dataset_organisation,
    definition_opts=None,
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
        Organisation of the dataset and the dimensions to process.
        Allows for defining the range of interest of the different dimensions.
        Looks like "timepoints_=%s-%s channels_=0-%s tiles_=%s-%s"
    definition_opts : dict
        Dictionary containing the details about the file repartitions.
    """

    xml_filename = project_filename + ".xml"

    if definition_opts is None:
        definition_opts = DefinitionOptions()

    temp = os.path.join(source_directory, project_filename + "_temp")
    os.path.join(temp, project_filename)

    options = (
        "define_dataset=[Manual Loader (Bioformats based)] "
        + "project_filename=["
        + xml_filename
        + "] "
        + "_____"
        + definition_opts.fmt_acitt_options()
        + " "
        + "image_file_directory="
        + source_directory
        + " "
        + "image_file_pattern="
        + image_file_pattern
        + dataset_organisation
        + " "
        + "calibration_type=[Same voxel-size for all views] "
        + "calibration_definition=[Load voxel-size(s) from file(s)] "
        # + "imglib2_data_container=[ArrayImg (faster)]"
    )

    log.debug("Manual dataset definition options: <%s>", options)
    IJ.run("Define Multi-View Dataset", str(options))


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
    IJ.run("As HDF5", str(options))


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
):
    """Calculate pairwise shifts using Phase Correlation.

    Parameters
    ----------
    project_path : str
        Full path to the `.xml` file.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptinos` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    downsampling_xyz : list of int, optional
        Downsampling factors in X, Y and Z, for example `[4,4,4]`. By default
        empty which will result in BigStitcher choosing the factors.
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
    IJ.run("Calculate pairwise shifts ...", str(options))

    backup_xml_files(file_info["path"], "phase_correlation_shift_calculation")


def filter_pairwise_shifts(
    project_path,
    min_r=0.7,
    max_r=1,
    max_shift_xyz="",
    max_displacement="",
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
    IJ.run("Filter pairwise shifts ...", str(options))

    backup_xml_files(file_info["path"], "filter_pairwise_shifts")


def optimize_and_apply_shifts(
    project_path,
    processing_opts=None,
    relative_error=2.5,
    absolute_error=3.5,
):
    """Optimize the shifts and apply them to the dataset.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` on which to optimize and apply the shifts.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptinos` object defining parameters for the run. Will
        fall back to the defaults defined in the corresponding class if the
        parameter is `None` or skipped.
    relative_error : float, optional
        Relative alignment error (in px) to accept, by default `2.5`.
    absolute_error : float, optional
        Absolute alignment error (in px) to accept, by default `3.5`.
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)

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
        + "global_optimization_strategy=[Two-Round using Metadata to align unconnected "
        + "Tiles and iterative dropping of bad links] "
        + "show_expert_grouping_options "
        + processing_opts.fmt_use_acitt()
        + processing_opts.fmt_how_to_treat()
    )

    log.debug("Optimization and shifts application options: <%s>", options)
    IJ.run("Optimize globally and apply shifts ...", str(options))

    backup_xml_files(file_info["path"], "optimize_and_apply_shifts")


def detect_interest_points(
    project_path,
    processing_opts=None,
    sigma=1.8,
    threshold=0.008,
    maximum_number=3000,
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
    maximum_number : int, optional
        Maximum number of interest points to use, by default `3000`.
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + "type_of_interest_point_detection=Difference-of-Gaussian "
        + "label_interest_points=beads "
        + "limit_amount_of_detections "
        + "group_tiles "
        + "subpixel_localization=[3-dimensional quadratic fit] "
        + "interest_point_specification=[Advanced ...] "
        + "downsample_xy=8x "
        + "downsample_z=2x "
        + "sigma="
        + str(sigma)
        + " "
        + "threshold="
        + str(threshold)
        + " "
        + "find_maxima "
        + "maximum_number="
        + str(maximum_number)
        + " "
        + "type_of_detections_to_use=Brightest "
        + "compute_on=[CPU (Java)]"
    )

    log.debug("Interest points detection options: <%s>", options)
    IJ.run("Detect Interest Points for Registration", str(options))


def interest_points_registration(
    project_path,
    processing_opts=None,
    rigid_timepoints=False,
):
    """Run the "Register Dataset based on Interest Points" command.

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
    """

    if not processing_opts:
        processing_opts = ProcessingOptions()

    if rigid_timepoints:
        rigid_timepoints_arg = "consider_each_timepoint_as_rigid_unit "
    else:
        rigid_timepoints_arg = " "

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
        + "Only compare overlapping views (according to current transformations)] "
        + "interest_point_inclusion=[Compare all interest point of overlapping views] "
        + "interest_points=beads "
        + "group_tiles "
        + "group_illuminations "
        + "group_channels "
        + "reference=1 "
        + rigid_timepoints_arg
        + "transformation=Affine "
        + "regularize_model "
        + "model_to_regularize_with=Affine "
        + "lamba=0.10 "
        + "number_of_neighbors=3 "
        + "redundancy=1 "
        + "significance=3 "
        + "allowed_error_for_ransac=5 "
        + "ransac_iterations=Normal "
        + "global_optimization_strategy=["
        + "Two-Round: Handle unconnected tiles, "
        + "remove wrong links RELAXED (5.0x / 7.0px)] "
        + "interestpoint_grouping=["
        + "Group interest points (simply combine all in one virtual view)] "
        + "interest=5"
    )

    log.debug("Interest points registration options: <%s>", options)
    # register using interest points
    IJ.run("Register Dataset based on Interest Points", options)


def duplicate_transformations(
    project_path,
    transformation_type="channel",
    channel_source=None,
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
        Reference channel nummber (starting at 1), by default None.
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

    chnl_apply = ""
    chnl_process = ""

    if transformation_type == "channel":
        apply = "[One channel to other channels]"
        target = "[All Channels]"
        source = str(channel_source - 1)
        if tile_source:
            tile_apply = "apply_to_tile=[Single tile (Select from List)] "
            tile_process = "processing_tile=[tile " + str(tile_source) + "] "
        else:
            tile_apply = "apply_to_tile=[All tiles] "
    elif transformation_type == "tile":
        apply = "[One tile to other tiles]"
        target = "[All Tiles]"
        source = str(tile_source)
        if channel_source:
            chnl_apply = "apply_to_channel=[Single channel (Select from List)] "
            chnl_process = (
                "processing_channel=[channel " + str(channel_source - 1) + "] "
            )
        else:
            chnl_apply = "apply_to_channel=[All channels] "
    else:
        sys.exit("Issue with transformation duplication")

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
        + chnl_apply
        + chnl_process
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
    IJ.run("Duplicate Transformations", str(options))

    backup_xml_files(
        file_info["path"],
        "duplicate_transformation_" + transformation_type,
    )


def fuse_dataset(
    project_path,
    processing_opts=None,
    result_path=None,
    downsampling=1,
    interpolation="[Linear Interpolation]",
    pixel_type="[16-bit unsigned integer]",
    fusion_type="Avg, Blending",
    export="HDF5",
    compression="Zstandard",
):
    """Call BigStitcher's "Fuse Dataset" command.

    Wrapper to `BigStitcher > Batch Processing > Fuse Dataset`.

    Depending on the export type, inputs are different and therefore will
    distribute inputs differently.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` on which to run the fusion.
    processing_opts : imcflibs.imagej.bdv.ProcessingOptions, optional
        The `ProcessingOptinos` object defining parameters for the run. Will
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
    export : str, optional
        Format of the output fused image, by default `HDF5`.
    fusion_type : str, optional
        Type of fusion algorithm to use, by default `Avg, Blending`.
    compression : str, optional
        Compression method to use when exporting as HDF5, by default `Zstandard`.
    """

    if processing_opts is None:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)
    if not result_path:
        result_path = file_info["path"]
        # if not os.path.exists(result_path):
        #     os.makedirs(result_path)

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + "bounding_box=[All Views] "
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
        + "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] "
        + "preserve_original "
        + "produce=[Each timepoint & channel] "
    )

    if export == "TIFF":
        options = (
            options
            + "fused_image=[Save as (compressed) TIFF stacks] "
            + "define_input=[Auto-load from input data (values shown below)] "
            + "output_file_directory=["
            + result_path
            + "/.] "
            + "filename_addition=["
            + file_info["basename"]
            + "]"
        )
    elif export == "HDF5":
        h5_fused_path = pathtools.join2(
            result_path, file_info["basename"] + "_fused.h5"
        )
        xml_fused_path = pathtools.join2(
            result_path, file_info["basename"] + "_fused.xml"
        )

        options = (
            options
            + "fused_image=[OME-ZARR/N5/HDF5 export using N5-API] "
            + "define_input=[Auto-load from input data (values shown below)] "
            + "export=HDF5 "
            + "compression="
            + compression
            + " "
            + "create "
            + "create_0 "
            + "hdf5_file=["
            + h5_fused_path
            + "] "
            + "xml_output_file=["
            + xml_fused_path
            + "] "
            + "show_advanced_block_size_options "
            + "block_size_x=128 "
            + "block_size_y=128 "
            + "block_size_z=64 "
            + "block_size_factor_x=1 "
            + "block_size_factor_y=1 "
            + "block_size_factor_z=1"
        )

    log.debug("Dataset fusion options: <%s>", options)
    IJ.run("Image Fusion", str(options))


def fuse_dataset_bdvp(
    project_path,
    command,
    processing_opts=None,
    result_path=None,
    compression="LZW",
):
    """Export a BigDataViewer project using the BIOP Kheops exporter.

    Use the BIOP Kheops exporter to convert a BigDataViewer project into
    OME-TIFF files, with optional compression.

    Parameters
    ----------
    project_path : str
        Full path to the BigDataViewer XML project file.
    command : CommandService
        The Scijava CommandService instance to execute the export command.
    processing_opts : ProcessingOptions, optional
        Options defining which parts of the dataset to process. If None, default
        processing options will be used (process all angles, channels, etc.).
    result_path : str, optional
        Path where to store the exported files. If None, files will be saved in
        the same directory as the input project.
    compression : str, optional
        Compression method to use for the TIFF files. Default is "LZW".

    Notes
    -----
    This function requires the PTBIOP update site to be enabled in Fiji/ImageJ.
    """
    if processing_opts is None:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)
    if not result_path:
        result_path = file_info["path"]
        # if not os.path.exists(result_path):
        #     os.makedirs(result_path)

    command.run(
        FuseBigStitcherDatasetIntoOMETiffCommand,
        True,
        "image",
        project_path,
        "output_dir",
        result_path,
        "compression",
        compression,
        "subset_channels",
        "",
        "subset_slices",
        "",
        "subset_frames",
        "",
        "compress_temp_files",
        False,
    )
