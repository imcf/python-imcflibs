"""BigDataViewer related functions.

Mostly convenience wrappers with simplified calls and default values.
"""

# Some function names just need to be longer than 30 chars:
# pylint: disable-msg=invalid-name

import os
import sys
import shutil

from ij import IJ  # pylint: disable-msg=import-error

from .. import pathtools

from ..log import LOG as log

# template strings:
SINGLE = "[Single %s (Select from List)]"


class ProcessingOptions(object):

    """Helper to store processing options and generate parameter strings.

    Attributes
    ----------
    use_channel : str
    use_tiles : str
    channel_processing_option : str
    channel_select : str
    illumination_processing_option : str
    illumination_select : str
    tile_processing_option : str
    tile_select : str
    timepoint_processing_option : str
    timepoint_select : str
    angle_processing_option : str
    angle_select : str
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
        self._treat_tiles = "group"
        self._treat_timepoints = "group"

    def reference_angle(self, value):
        # FIXME: is the "expert grouping" statement correct?
        """Set the reference angle when using *Expert Grouping Options*.

        Select the angle(s) to use for the operation, by default empty (`""`).

        NOTE: this value will be used to render `angles=[use Angle VALUE]` when calling
        the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : str
            The tile to use for the grouping.
        """
        self._use_angle = "angles=[use Angle %s]" % str(value)
        log.debug("New reference angle setting: %s", self._use_angle)

    def reference_channel(self, value):
        # FIXME: is the "expert grouping" statement correct?
        # FIXME: explain the "-1", why is it done?
        """Set the reference channel when using *Expert Grouping Options*.

        Select the channel(s) to use for the operation, by default the averaging mode
        will be used (`channels=[Average Channels]`).

        NOTE: this value will be used to render `channels=[use Channel VALUE]` when
        calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
            The channel number + 1 to use for the grouping (in other words: the
            effectively used value will be the given one minus 1).
        """
        channel = int(value) - 1  # will raise a ValueError if cast fails
        self._use_channel = "channels=[use Channel %s]" % channel
        log.debug("New reference channel setting: %s", self._use_channel)

    def reference_illumination(self, value):
        # FIXME: is the "expert grouping" statement correct?
        """Set the reference illumination when using *Expert Grouping Options*.

        Select the illumination(s) to use for the operation, by default the averaging
        mode will be used (`illuminations=[Average Illuminations]`).

        NOTE: this value will be used to render `illuminations=[use Illumination VALUE]`
        when calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
        """
        self._use_illumination = "illuminations=[use Illumination %s]" % value
        log.debug("New reference illumination setting: %s", self._use_illumination)

    def reference_tile(self, value):
        # FIXME: is the "expert grouping" statement correct?
        # FIXME: what are possible types for the parameter, is it int?
        """Set the reference tile when using *Expert Grouping Options*.

        Select the tile(s) to use for the operation, by default the averaging mode will
        be used (`tiles=[Average Tiles]`).

        NOTE: this value will be used to render `tiles=[use Tile VALUE]` when calling
        the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : str
            The tile to use for the grouping.
        """
        self._use_tile = "tiles=[use Tile %s]" % str(value)
        log.debug("New reference tile setting: %s", self._use_tile)

    def reference_timepoint(self, value):
        # FIXME: is the "expert grouping" statement correct?
        """Set the reference timepoint when using *Expert Grouping Options*.

        Select the timepoint(s) to use for the operation, by default the averaging mode
        will be used (`timepoints=[Average Timepoints]`).

        NOTE: this value will be used to render `timepoints=[use Timepoint VALUE]` when
        calling the `fmt_use_acitt()` method.

        Parameters
        ----------
        value : int or int-like
        """
        self._use_timepoint = "timepoints=[use Timepoint %s]" % value
        log.debug("New reference timepoint setting: %s", self._use_timepoint)

    def process_angle(self, value):  # def angle_select(self, value):
        """Select a single angle to use for processing.

        Parameters
        ----------
        value : int or int-like
        """
        self._angle_processing_option = SINGLE % "angle"
        self._angle_select = "processing_angle=[angle %s]" % value

    def process_channel(self, value):  # def channel_select(self, value):
        """Select a single channel to use for processing.

        Parameters
        ----------
        value : int or int-like
        """
        self._channel_processing_option = SINGLE % "channel"
        channel = int(value) - 1
        self._channel_select = "processing_channel=[channel %s]" % channel

    def process_illumination(self, value):  # def illumination_select(self, value):
        """Select a single illumination to use for processing.

        Parameters
        ----------
        value : int or int-like
        """
        self._illumination_processing_option = SINGLE % "illumination"
        self._illumination_select = "processing_illumination=[illumination %s]" % value

    def process_tile(self, value):  # def tile_select(self, value):
        """Select a single tile to use for processing.

        Parameters
        ----------
        value : int or int-like
        """
        self._tile_processing_option = SINGLE % "tile"
        self._tile_select = "processing_tile=[tile %s]" % value

    def process_timepoint(self, value):  # def timepoint_select(self, value):
        """Select a single timepoint to use for processing.

        Parameters
        ----------
        value : int or int-like
        """
        self._timepoint_processing_option = SINGLE % "timepoint"
        self._timepoint_select = "processing_timepoint=[timepoint %s]" % value

    def treat_angles(self, value):
        """Set the value for the `how_to_treat_angles` option.

        If the value is set to `group` also the `reference_angle` setting will
        be adjusted to `angles=[Average Angles]`.

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

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_channels = value
        log.debug("New 'treat_channels' setting: %s", value)

    def treat_illuminations(self, value):
        """Set the value for the `how_to_treat_illuminations` option.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_illuminations = value
        log.debug("New 'treat_illuminations' setting: %s", value)

    def treat_tiles(self, value):
        """Set the value for the `how_to_treat_tiles` option.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_tiles = value
        log.debug("New 'treat_tiles' setting: %s", value)

    def treat_timepoints(self, value):
        """Set the value for the `how_to_treat_timepoints` option.

        Parameters
        ----------
        value : str
            One of `group`, `compare` or `[treat individually]`.
        """
        self._treat_timepoints = value
        log.debug("New 'treat_timepoints' setting: %s", value)

    def fmt_acitt_options(self):
        """Format Angle / Channel / Illumination / Tile / Timepoint options.

        Build a string providing the `process_angle`, `process_channel`,
        `process_illumination`, `process_tile` and `process_timepoint` options
        that can be used in a BDV-related `IJ.run` call.

        Returns
        -------
        str
        """
        parameters = [
            "process_angle=" + self._angle_processing_option,
            "process_channel=" + self._channel_processing_option,
            "process_illumination=" + self._illumination_processing_option,
            "process_tile=" + self._tile_processing_option,
            "process_timepoint=" + self._timepoint_processing_option,
        ]
        parameter_string = " ".join(parameters) + " "
        log.debug("Formatted ACITT options: <%s>", parameter_string)
        return parameter_string

    def fmt_acitt_selectors(self):
        """Format Angle / Channel / Illumination / Tile / Timepoint selectors.

        Build a string providing the `angle_select`, `channel_select`,
        `illumination_select`, `tile_select` and `timepoint_select` options
        that can be used in a BDV-related `IJ.run` call.

        Returns
        -------
        str
        """
        parameters = [
            "angle_select=" + self._angle_select if self._angle_select else "",
            "channel_select=" + self._channel_select if self._channel_select else "",
            "illumination_select=" + self._illumination_select
            if self._illumination_select
            else "",
            "tile_select=" + self._tile_select if self._tile_select else "",
            "timepoint_select=" + self._timepoint_select
            if self._timepoint_select
            else "",
        ]
        parameter_string = " ".join(parameters) + " "
        log.debug("Formatted ACITT selectors: <%s>", parameter_string)
        return parameter_string

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
        parameter_string = " ".join(parameters) + " "
        log.debug("Formatted 'how_to_treat_' options: <%s>", parameter_string)
        return parameter_string

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
        parameter_string = " ".join(parameters) + " "
        log.debug("Formatted expert grouping 'use' options: <%s>", parameter_string)
        return parameter_string


def backup_xml_files(source_directory, subfolder_name):
    """Create a backup of BDV-XML files inside a subfolder of `xml-backup`.

    Copies all `.xml` and `.xml~` files to a subfolder with the given name inside a
    folder called `xml-backup` in the source directory. Uses the `shutil.copy2()`
    command, which will overwrite existing files.

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
    all_xml_files = pathtools.listdir_matching(source_directory, ".*\.xml", regex=True)
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
    """Run "Define Multi-View Dataset" using the "Auto-Loader" option.

    Parameters
    ----------
    project_filename : str
        Name of the project (without an `.xml` extension).
    file_path : str
        Path to the file, can be the first `.czi` or a regex to match all files
        with an extension.
    dataset_save_path : str
        Output path for the `.xml`.
    bf_series_type : str
        One of "Angles" or "Tiles", specifying how Bio-Formats interprets the series.
    timepoints_per_partition : int, optional
        Split the output by timepoints. Use `0` for no split, by default `1`.
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
    # FIXME: the docstring is actually not corrct, in the sense that the function will
    # switch to `Define dataset ...` in case the `bf_series_type` is `Tiles`

    # FIXME: improve the timepoints_per_partition parameter description!

    file_info = pathtools.parse_path(file_path)

    project_filename = project_filename.replace(" ", "_")
    result_folder = pathtools.join2(file_info["path"], project_filename)

    if not os.path.exists(result_folder):
        os.makedirs(result_folder)

    if not dataset_save_path:
        dataset_save_path = pathtools.join2(result_folder, project_filename)
    if subsampling_factors:
        subsampling_factors = "subsampling_factors=" + subsampling_factors + " "
    else:
        subsampling_factors = (
            "manual_mipmap_setup "
            "subsampling_factors=[{ "
            "{1,1,1}, "
            "{2,2,1}, "
            "{4,4,1}, "
            "{8,8,2}, "
            "{16,16,4} "
            "}] "
        )
    if hdf5_chunk_sizes:
        hdf5_chunk_sizes = "hdf5_chunk_sizes=" + hdf5_chunk_sizes + " "
    else:
        hdf5_chunk_sizes = (
            "hdf5_chunk_sizes=[{ "
            "{32,32,4}, "
            "{32,16,8}, "
            "{16,16,16}, "
            "{32,16,8}, "
            "{32,32,4} "
            "}] "
        )

    if bf_series_type == "Angles":
        angle_rotation = "apply_angle_rotation "
    else:
        angle_rotation = ""

    options = (
        "define_dataset=[Automatic Loader (Bioformats based)] "
        + "project_filename=["
        + project_filename
        + ".xml"
        + "] "
        + "path=["
        + file_info["path"]
        + "] "
        + "exclude=10 "
        # + "bioformats_series_are?="
        # + bf_series_type
        # + " "
        + "move_tiles_to_grid_(per_angle)?=[Do not move Tiles to Grid (use Metadata if available)] "
        + "how_to_load_images=["
        + resave
        + "] "
        + "dataset_save_path=["
        + result_folder
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
        # + "export_path=["
        # + dataset_save_path
        # + "]",
    )

    log.debug(options)

    if bf_series_type == "Tiles":
        log.debug("Doing tiled dataset definition")
        IJ.run("Define dataset ...", str(options))
    elif bf_series_type == "Angles":
        log.debug("Doing multi-view dataset definition")
        IJ.run("Define Multi-View Dataset", str(options))
    else:
        raise ValueError("Wrong answer for series type")
    return


def define_dataset_manual(
    project_filename,
    source_directory,
    image_file_pattern,
    dataset_organisation,
    file_definition,
):
    """Run "Define Multi-View Dataset" using the "Manual Loader" option.

    Parameters
    ----------
    project_filename : str
        Name of the project (without an `.xml` extension).
    source_directory : str
        Path to the folder containing the file(s).
    image_file_pattern : str
        Pattern corresponding to the names of your files separating the
        different dimensions.
    dataset_organisation : str
        Organisation of the dataset and the dimensions to process.
    file_definition : dict
        Dictionary containing the details about the file repartitions.
    """

    # FIXME: explain image_file_pattern, dataset_organisation and
    # file_definition with more details / examples

    xml_filename = project_filename + ".xml"

    temp = os.path.join(source_directory, project_filename + "_temp")
    os.path.join(temp, project_filename)

    options = (
        "define_dataset=[Manual Loader (Bioformats based)] "
        + "project_filename=["
        + xml_filename
        + "] "
        + "multiple_timepoints="
        + file_definition["multiple_timepoints"]
        + " "
        + "multiple_channels="
        + file_definition["multiple_channels"]
        + " "
        + "multiple_illumination_directions="
        + file_definition["multiple_illuminations"]
        + " "
        + "multiple_angles="
        + file_definition["multiple_angles"]
        + " "
        + "multiple_tiles="
        + file_definition["multiple_tiles"]
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
        + "imglib2_data_container=[ArrayImg (faster)]"
    )

    log.debug(options)
    IJ.run("Define dataset ...", str(options))


def resave_as_h5(
    source_xml_file,
    output_h5_file_path,
    timepoints="All Timepoints",
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
    timepoints : str, optional
        The timepoints that should be exported, by default `All Timepoints`.
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
    # save all timepoints or a single one:
    if timepoints == "All Timepoints":
        timepoints = "resave_timepoint=[All Timepoints] "
    else:
        timepoints = (
            "resave_timepoint=[Single Timepoint (Select from List)] "
            + "processing_timepoint=[Timepoint "
            + str(timepoints)
            + "] "
        )

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
        + "resave_angle=[All angles] "
        + "resave_channel=[All channels] "
        + "resave_illumination=[All illuminations] "
        + "resave_tile=[All tiles] "
        + timepoints
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

    log.debug(options)
    IJ.run("As HDF5", str(options))

    return


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
    treat_timepoints="group",
    treat_channels="group",
    treat_illuminations="group",
    treat_angles="[treat individually]",
    treat_tiles="group",
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
    treat_timepoints : str, optional
        How to deal with the timepoints, by default `group`.
    treat_channels : str, optional
        How to deal with the channels, by default `group`.
    treat_illuminations : str, optional
        How to deal with the illuminations, by default `group`.
    treat_angles : str, optional
        How to deal with the angles, by default `[treat individually]`.
    treat_tiles : str, optional
        How to deal with the tiles, by default `group`.
    downsampling_xyz : list of int, optional
        Downsampling factors in X, Y and Z, for example `[4,4,4]`. By default
        empty which will result in BigStitcher choosing the factors.
    """

    if processing_opts is None:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)

    use_angle = "angles=[Average Angles]" if treat_angles == "group" else ""
    use_channel = processing_opts.use_channel if treat_channels == "group" else ""
    use_illumination = ""
    if treat_illuminations == "group":
        use_illumination = "illuminations=[Average Illuminations]"
    use_timepoint = ""
    if treat_timepoints == "group":
        use_timepoint = "timepoints=[Average Timepoints]"
    use_tile = processing_opts.use_tiles if treat_tiles == "group" else ""

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
        # + options_dict["timepoint_select"]  # FIXME: is this duplication intended??
        + " "
        + "method=[Phase Correlation] "
        + "show_expert_grouping_options "
        + "show_expert_algorithm_parameters "
        + use_angle
        + " "
        + use_channel
        + " "
        + use_illumination
        + " "
        + use_timepoint
        + " "
        + use_tile
        + " "
        + "how_to_treat_angles="
        + treat_angles
        + " "
        + "how_to_treat_channels="
        + treat_channels
        + " "
        + "how_to_treat_illuminations="
        + treat_illuminations
        + " "
        + "how_to_treat_tiles="
        + treat_tiles
        + " "
        + "how_to_treat_timepoints="
        + treat_timepoints
        + " "
        + downsampling
        + "subpixel_accuracy"
    )

    log.debug(options)
    IJ.run("Calculate pairwise shifts ...", str(options))

    backup_xml_files(file_info["path"], "phase_correlation_shift_calculation")
    return


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

    log.debug(options)
    IJ.run("Filter pairwise shifts ...", str(options))

    backup_xml_files(file_info["path"], "filter_pairwise_shifts")
    return


def optimize_and_apply_shifts(
    project_path,
    processing_opts=None,
    treat_timepoints="group",
    treat_channels="group",
    treat_illuminations="group",
    treat_angles="[treat individually]",
    treat_tiles="group",
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
    treat_timepoints : str, optional
        How to treat the timepoints, by default `group`.
    treat_channels : str, optional
        How to treat the channels, by default `group`.
    treat_illuminations : str, optional
        How to treat the illuminations, by default `group`.
    treat_angles : str, optional
        How to treat the angles, by default `[treat individually]`.
    treat_tiles : str, optional
        How to treat the tiles, by default `group`.
    relative_error : float, optional
        Relative alignment error (in px) to accept, by default `2.5`.
    absolute_error : float, optional
        Absolute alignment error (in px) to accept, by default `3.5`.
    """

    if processing_opts is None:
        processing_opts = ProcessingOptions()

    file_info = pathtools.parse_path(project_path)

    use_angle = "angles=[Average Angles]" if treat_angles == "group" else ""
    use_channel = processing_opts.use_channel if treat_channels == "group" else ""
    use_illumination = ""
    if treat_illuminations == "group":
        use_illumination = "illuminations=[Average Illuminations]"
    use_timepoint = ""
    if treat_timepoints == "group":
        use_timepoint = "timepoints=[Average Timepoints]"
    use_tile = processing_opts.use_tiles if treat_tiles == "group" else ""

    options = (
        "select=["
        + project_path
        + "] "
        + processing_opts.fmt_acitt_options()
        + processing_opts.fmt_acitt_selectors()
        + " "  # WARNING: original code had another "timepoint_select" option here!
        + "relative="
        + str(relative_error)
        + " "
        + "absolute="
        + str(absolute_error)
        + " "
        + "global_optimization_strategy=[Two-Round using Metadata to align unconnected "
        + "Tiles and iterative dropping of bad links] "
        + "show_expert_grouping_options "
        + use_angle
        + " "
        + use_channel
        + " "
        + use_illumination
        + " "
        + use_timepoint
        + " "
        + use_tile
        + " "
        + "how_to_treat_angles="
        + treat_angles
        + " "
        + "how_to_treat_channels="
        + treat_channels
        + " "
        + "how_to_treat_illuminations="
        + treat_illuminations
        + " "
        + "how_to_treat_tiles="
        + treat_tiles
        + " "
        + "how_to_treat_timepoints="
        + treat_timepoints
    )

    log.debug(options)
    IJ.run("Optimize globally and apply shifts ...", str(options))

    backup_xml_files(file_info["path"], "optimize_and_apply_shifts")


def detect_interest_points(
    project_path,
    process_timepoint="All Timepoints",
    process_channel="All channels",
    sigma=1.8,
    threshold=0.008,
    maximum_number=3000,
):
    """Run the "Detect Interest Points" command for registration.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` project.
    process_timepoint : str, optional
        Timepoint to be processed, by default `All Timepoints`.
    process_channel : str, optional
        Channel to be processed, by default `All channels`.
    sigma : float, optional
        Minimum sigma for interest points detection, by default `1.8`.
    threshold : float, optional
        Threshold value for the interest point detection, by default `0.008`.
    maximum_number : int, optional
        Maximum number of interest points to use, by default `3000`.
    """

    # If not process all channels at once, then adapt the option
    if process_channel == "All channels":
        process_channel_arg = "[" + process_channel + "] "
    else:
        process_channel_arg = (
            "[Single channel (Select from List)] "
            + "processing_channel=[channel "
            + process_channel
            + "] "
        )
    # FIXME look into the actual call! @sebastien
    # save all timepoints or a single one:
    if process_timepoint == "All Timepoints":
        process_timepoint = "resave_timepoint=[All Timepoints] "
    else:
        process_timepoint = (
            "resave_timepoint=[Single Timepoint (Select from List)] "
            + "processing_timepoint=[Timepoint "
            + str(process_timepoint)
            + "] "
        )

    options = (
        "select=["
        + project_path
        + "] "
        + "process_angle=[All angles] "
        + "process_channel="
        + process_channel_arg
        + "process_illumination=[All illuminations] "
        + "process_tile=[All tiles] "
        + "process_timepoint=["
        + process_timepoint
        + "] "
        + "type_of_interest_point_detection=Difference-of-Gaussian "
        + "label_interest_points=beads "
        + "limit_amount_of_detections "
        + "group_tiles "
        + "group_illuminations "
        + "subpixel_localization=[3-dimensional quadratic fit] "
        + "interest_point_specification=[Advanced ...] "
        + "downsample_xy=[Match Z Resolution (less downsampling)] "
        + "downsample_z=1x "
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

    log.debug(options)
    IJ.run("Detect Interest Points for Registration", str(options))
    return


def interest_points_registration(
    project_path,
    process_timepoint="All Timepoints",
    process_channel="All channels",
    rigid_timepoints=False,
):
    """Run the "Register Dataset based on Interest Points" command.

    Parameters
    ----------
    project_path : str
        Path to the `.xml` project.
    process_timepoint : str, optional
        Timepoint to be processed, by default `All Timepoints`.
    process_channel : str, optional
        Channels to be used for performing the registration. By default, all
        channels are taken into account, however this behavior could be
        undesirable if only one channel is adequate (e.g. beads or other useful
        fiducials). To restrict registration to a specific channel, provide the
        channel name using this parameter. By default `All channels`.
    rigid_timepoints : bool, optional
        If set to `True` each timepoint will be considered as a rigid unit
        (useful e.g. if spatial registration has already been performed before).
        By default `False`.
    """

    # If not process all channels at once, then adapt the option
    if process_channel == "All channels":
        process_channel_arg = "[All channels] "
    else:
        process_channel_arg = (
            "[Single channel (Select from List)] processing_channel=[channel "
            + process_channel
            + "] "
        )

    if rigid_timepoints:
        rigid_timepoints_arg = "consider_each_timepoint_as_rigid_unit "
    else:
        rigid_timepoints_arg = " "

    options = (
        "select=["
        + project_path
        + "] "
        + "process_angle=[All angles] "
        + "process_channel="
        + process_channel_arg
        + "process_illumination=[All illuminations] "
        + "process_tile=[All tiles] "
        + "process_timepoint=["
        + process_timepoint
        + "] "
        + "registration_algorithm=[Precise descriptor-based (translation invariant)] "
        + "registration_in_between_views=[Compare all views against each other] "
        + "interest_points=beads "
        + "group_tiles "
        + "group_illuminations "
        + "group_channels "
        + rigid_timepoints_arg
        + "fix_views=[Fix first view] "
        + "map_back_views=[Do not map back (use this if views are fixed)] "
        + "transformation=Affine "
        + "regularize_model "
        + "model_to_regularize_with=Rigid "
        + "lamba=0.10 "
        + "number_of_neighbors=3 "
        + "redundancy=2 "
        + "significance=1 "
        + "allowed_error_for_ransac=5 "
        + "ransac_iterations=Normal "
        + "interestpoint_grouping=[Group interest points (simply combine all in one virtual view)] "
        + "interest=5"
    )

    log.debug(options)
    # register using interest points
    IJ.run("Register Dataset based on Interest Points", options)
    return


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
    # FIXME: transformation_to_use requires explanations of possible values!

    file_info = pathtools.parse_path(project_path)

    apply = ""
    source = ""
    target = ""
    tile_apply = ""
    tile_process = ""

    chnl_apply = ""
    chnl_process = ""

    # FIXME: invalid parameter combinations!
    # Calling the function with transformation_type="channel" and
    # channel_source=None (the default) will lead to an invalid combination!
    # Same for transformation_type="tile" / tile_source=None, in both cases the
    # resulting call will contain the sequence ` source= `.
    if transformation_type == "channel":
        apply = "[One channel to other channels]"
        target = "[All Channels]"
        if channel_source:
            source = str(channel_source - 1)
        if tile_source:
            tile_apply = "apply_to_tile=[Single tile (Select from List)] "
            tile_process = "processing_tile=[tile " + str(tile_source) + "] "
        else:
            tile_apply = "apply_to_tile=[All tiles] "
    elif transformation_type == "tile":
        apply = "[One tile to other tiles]"
        target = "[All Tiles]"
        if tile_source:
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

    log.debug(options)
    IJ.run("Duplicate Transformations", str(options))

    backup_xml_files(
        file_info["path"], "duplicate_transformation_" + transformation_type
    )
    return


def fuse_dataset(
    project_path,
    processing_opts=None,
    result_path=None,
    downsampling=1,
    interpolation="[Linear Interpolation]",
    pixel_type="[16-bit unsigned integer]",
    export="HDF5",
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
        + "pixel_type="
        + pixel_type
        + " "
        + "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] "
        + "blend "
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
            + "fused_image=[ZARR/N5/HDF5 export using N5-API] "
            + "define_input=[Auto-load from input data (values shown below)] "
            + "export=HDF5 "
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

    log.debug(options)
    IJ.run("Fuse dataset ...", str(options))
