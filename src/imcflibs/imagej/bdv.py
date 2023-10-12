"""BigDataViewer related functions.

Mostly convenience wrappers with simplified calls and default values.
"""

# The pylint on Python 2.7 is too old to play nicely with black:
# pylint: disable-msg=bad-continuation
# Some function names just need to be longer than 30 chars:
# pylint: disable-msg=invalid-name
import os
import sys
import shutil

from ij import IJ  # pylint: disable-msg=import-error

from .. import pathtools

from ..log import LOG as log


def backup_xml_files(source_directory, subfolder_name):
    """Copy all .xml (and .xml~) files to a subfolder inside
    a folder called "xml-backup" in the source dir.
    Uses shutil.copy2 which will overwrite existing files.

    Parameters
    ----------
    source_directory : str
        full path to the directory containing the xml files
    subfolder_name : str
        name of the subfolder. Will be created if it does not exists.
    """

    xml_backup_directory = os.path.join(source_directory, "xml-backup")
    pathtools.create_directory(xml_backup_directory)
    backup_subfolder = xml_backup_directory + "/%s" % (subfolder_name)
    pathtools.create_directory(backup_subfolder)
    all_xml_files = pathtools.listdir_matching(source_directory, ".*\.xml", regex=True)
    os.chdir(source_directory)
    for xml_file in all_xml_files:
        shutil.copy2(xml_file, backup_subfolder)


def run_define_dataset_autoloader(
    project_filename,
    file_path,
    bf_series_type,
    dataset_save_path=None,
    timepoints_per_partition=1,
    resave="Re-save as multiresolution HDF5",
    subsampling_factors=None,
    hdf5_chunk_sizes=None,
):
    """Run the Define Multi-View Dataset command using the "Auto-Loader" option.

    Parameters
    ----------
    project_filename : str
        Name of the project without .xml extension
    file_path : str
        path to the file, can be the first czi or a regex to match all files
        with an extension
    dataset_save_path : str
        output path for the .xml
    bf_series_type : str
        One of "Angles" or "Tiles", specifying how Bio-Formats interprets the series.
    timepoints_per_partition : int, optional
        split the output by timepoints. Use 0 for no split, by default 1
    resave : str, optional
        Allows this function to either re-save the images or simply create a merged xml.
        Use "Load raw data" to avoid re-saving, by default "Re-save as multiresolution
        HDF5" will resave the input data.
    subsampling_factors: str, optional
        Allow specifying subsampling factors explicitly, for example:
        "[{ {1,1,1}, {2,2,1}, {4,4,2}, {8,8,4} }]"
    hdf5_chunk_sizes: str, optional
        Allow specifying hdf5_chunk_sizes factors explicitly, for example
        "[{ {32,16,8}, {16,16,16}, {16,16,16}, {16,16,16} }]"
    """

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
        subsampling_factors = "manual_mipmap_setup subsampling_factors=[{ {1,1,1}, {2,2,1}, {4,4,1}, {8,8,2}, {16,16,4} }] "
    if hdf5_chunk_sizes:
        hdf5_chunk_sizes = "hdf5_chunk_sizes=" + hdf5_chunk_sizes + " "
    else:
        hdf5_chunk_sizes = "hdf5_chunk_sizes=[{ {32,32,4}, {32,16,8}, {16,16,16}, {32,16,8}, {32,32,4} }] "

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


def run_define_dataset_manualoader(
    project_filename,
    source_directory,
    image_file_pattern,
    dataset_organisation,
    file_definition,
):
    """Run the Define Multi-View Dataset command using the "Manual Loader" option

    Parameters
    ----------
    project_filename : str
        Name of the project without .xml extension
    source_directory : str
        Path to the folder containing the file(s)
    image_file_pattern : str
        Pattern corresponding to the names of your files separating the
        different dimensions
    dataset_organisation : str
        Organisation of the dataset and the dimensions to process
    file_definition : dict
        Dictionary containing all the info about the file repartitions
    """

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

    return


def run_resave_as_h5(
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
    `run_define_dataset_autoloader()`). Allows e.g. parallelization of HDF-5
    re-saving.

    Parameters
    ----------
    source_xml_file : File or str
        XML input file.
    output_h5_file_path : str
        Export path for the output file including .xml extension
    timepoints : str, optional
        Which timepoints should be exported, by default "All Timepoints".
    timepoints_per_partition : int, optional
        How many timepoints per partition should be exported, by default 1.
    use_deflate_compression : bool, optional
        Run deflate compression, by default True.
    subsampling_factors: str, optional
        Allow specifying subsampling factors explicitly, for example:
        "[{ {1,1,1}, {2,2,1}, {4,4,2}, {8,8,4} }]"
    hdf5_chunk_sizes: str, optional
        Allow specifying hdf5_chunk_sizes factors explicitly, for example
        "[{ {32,16,8}, {16,16,16}, {16,16,16}, {16,16,16} }]"
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


def run_flip_axes(source_xml_file, x=False, y=True, z=False):
    """Wrapper for BigStitcher > Batch Processing > Tools > Flip axes.
    For example, nd2 files require a flip along the y axis.

    Parameters
    ----------
    h5_resave_xml_path : str
        full path to the .xml-file
    x : bool, optional
        flip images along the x axes, by default False
    y : bool, optional
        flip mages along the  axes, by default True
    z : bool, optional
        flip images along the z axes, by default False
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


def run_phase_correlation_pairwise_shifts_calculation(
    project_path,
    input_dict={},
    treat_timepoints="group",
    treat_channels="group",
    treat_illuminations="group",
    treat_angles="[treat individually]",
    treat_tiles="group",
    downsampling_xyz="",
):
    """Run the Pairwise shifts calculation using Phase Correlation

    Parameters
    ----------
    project_path : str
        Path to the XML
    input_dict : dict
        Dictionary containing all the required information for angle, channel,
        illuminations and timepoints
    treat_timepoints : str, optional
        How to deal with the timepoints, by default "group"
    treat_channels : str, optional
        How to deal with the channels, by default "group"
    treat_illuminations : str, optional
        How to deal with the illuminations, by default "group"
    treat_angles : str, optional
        How to deal with the angles, by default "[treat individually]"
    treat_tiles : str, optional
        How to deal with the tiles, by default "group"
    downsampling_xyz : list of int, optional
        specify downsampling in x,y and z, e.g. [4,4,4], by default empty,
        meaning BigStitcher chooses

    """

    file_info = pathtools.parse_path(project_path)

    options_dict = parse_options(input_dict)

    print(options_dict)

    use_angle = "angles=[Average Angles]" if treat_angles == "group" else ""
    use_channel = "channels=[Average Channels]" if treat_channels == "group" else ""
    use_illumination = (
        "illuminations=[Average Illuminations]"
        if treat_illuminations == "group"
        else ""
    )
    use_timepoint = (
        "timepoints=[Average Timepoints]" if treat_timepoints == "group" else ""
    )
    use_tile = "tiles=[Average Tiles]" if treat_tiles == "group" else ""

    if downsampling_xyz != "":
        downsampling = (
            "downsample_in_x=%s downsample_in_y=%s downsample_in_z=%s ") % (
            downsampling_xyz[0],
            downsampling_xyz[1],
            downsampling_xyz[2]
        )
    else:
        downsampling = ""

    options = (
        "select=["
        + project_path
        + "] "
        + "process_angle="
        + options_dict["angle_text"]
        + "process_channel="
        + options_dict["channel_text"]
        + "process_illumination="
        + options_dict["illumination_text"]
        + "process_tile="
        + options_dict["tile_text"]
        + "process_timepoint="
        + options_dict["timepoint_text"]
        + options_dict["timepoint_select"]
        + options_dict["angle_select"]
        + options_dict["channel_select"]
        + options_dict["illumination_select"]
        + options_dict["tile_select"]
        + options_dict["timepoint_select"]
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


def run_filter_pairwise_shifts(
    project_path,
    min_r=0.7,
    max_r=1,
    max_shift_xyz="",
    max_displacement="",
):
    """Filter the pairwise shifts based on different thresholds

    Parameters
    ----------
    project_path : str
        Path of the XML on which to apply the filters
    min_r : float, optional
        Minimal quality of the link to keep, by default 0.7
    max_r : float, optional
        Maximal quality of the link to keep, by default 1
    max_shift_xyz : list of int, optional
        Maximal shift in X, Y and Z in px to keep, e.g. [10,10,10], by default empty,
        meaning this option is skipped
    max_displacement : int, optional
        Maximal displacement to keep, by default empty,
        meaning this option is skipped
    """

    file_info = pathtools.parse_path(project_path)

    if max_shift_xyz != "":
        filter_by_max_shift = (
            " filter_by_shift_in_each_dimension"
            " max_shift_in_x=%s max_shift_in_y=%s max_shift_in_z=%s") % (
            max_shift_xyz[0],
            max_shift_xyz[1],
            max_shift_xyz[2]
        )
    else:
        filter_by_max_shift = ""

    if max_displacement != "":
        filter_by_max_displacement = (
            " filter_by_total_shift_magnitude max_displacement=%s") % (
            max_displacement
        )
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


def run_optimize_apply_shifts(
    project_path,
    input_dict={},
    treat_timepoints="group",
    treat_channels="group",
    treat_illuminations="group",
    treat_angles="[treat individually]",
    treat_tiles="group",
    relative_error=2.5,
    absolute_error=3.5,
):
    """Optimize the shifts and apply it to the dataset

    Parameters
    ----------
    project_path : str
        Path of the XML on which to optimize and apply the shifts
    input_dict : dict
        Dictionary containing all the required information for angles,
        channels, illuminations, tiles and timepoints
    treat_timepoints : str, optional
        How to treat the timepoints, by default "group"
    treat_channels : str, optional
        How to treat the channels, by default "group"
    treat_illuminations : str, optional
        How to treat the illuminations, by default "group"
    treat_angles : str, optional
        How to treat the angles, by default "[treat individually]"
    treat_tiles : str, optional
        How to treat the tiles, by default "group"
    relative_error: float, optional
        relative alignment error in px, by default 2.5
    absolute_error: float, optional
        absolute alignment error in px, by default 3.5
    """

    file_info = pathtools.parse_path(project_path)

    options_dict = parse_options(input_dict)

    use_angle = "angles=[Average Angles]" if treat_angles == "group" else ""
    use_channel = "channels=[Average Channels]" if treat_channels == "group" else ""
    use_illumination = (
        "illuminations=[Average Illuminations]"
        if treat_illuminations == "group"
        else ""
    )
    use_timepoint = (
        "timepoints=[Average Timepoints]" if treat_timepoints == "group" else ""
    )
    use_tile = "tiles=[Average Tiles]" if treat_tiles == "group" else ""

    options = (
        "select=["
        + project_path
        + "] "
        + "process_angle="
        + options_dict["angle_text"]
        + "process_channel="
        + options_dict["channel_text"]
        + "process_illumination="
        + options_dict["illumination_text"]
        + "process_tile="
        + options_dict["tile_text"]
        + "process_timepoint="
        + options_dict["timepoint_text"]
        + options_dict["timepoint_select"]
        + options_dict["angle_select"]
        + options_dict["channel_select"]
        + options_dict["illumination_select"]
        + options_dict["tile_select"]
        + options_dict["timepoint_select"]
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
    return


def run_detect_interest_points(
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
        Path to the .xml project
    process_timepoint : str, optional
        Specify which timepoint should be processed, by default "All Timepoints"
    process_channel : str, optional
        Specify which channel should be processed, by default "All channels"
    sigma : float, optional
        Minimum sigma for interest points detection, by default 1.8
    threshold : float, optional
        Threshold value for the interest point detection, by default 0.008
    maximum_number : int, optional
        Maximum number of interest points to use, by default 3000.
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


def run_interest_points_registration(
    project_path,
    process_timepoint="All Timepoints",
    process_channel="All channels",
    rigid_timepoints=False,
):
    """Run the registration command.

    Parameters
    ----------
    project_path : str
        Path to the .xml project
    process_timepoint : str, optional
        Specify which timepoint should be processed, by default "All Timepoints"
    process_channel : str, optional
        Specify which channels should be processed. By default, all channels are
        processed together, however this behavior could be undesirable if only
        one channel is adequate (beads or nuclei). In that case provide the
        channel name instead. by default "All channels"
    rigid_timepoints : bool, optional
        If spatial registration has already been run, set this boolean to True
        to consider each timepoint as rigid unit, by default False
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


def run_duplicate_transformations(
    project_path,
    transformation_type="channel",
    channel_source=None,
    tile_source=None,
    transformation_to_use="[Replace all transformations]",
):
    """Duplicate the transformation parameters to the other channels.

    If registration has been generated using a single channel,this can be used
    to propagate it to the others.

    Parameters
    ----------
    project_path : str
        Path to the .xml project
    transformation_type : str, optional
        select mode, e.g. "channel" or "tiles"
    channel_source : int, optional
        number of the reference channel, starts at 1, by default None
    tile source : int, optional
        the reference tile, by default None
    transformation_to_use : str, optional
        select which transformations to duplicate.
        Alternative option: "[Add last transformation only]"
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


# def run_fusion(
#     temp_path,
#     fused_xml_path,
#     process_timepoint="All Timepoints",
#     downsampling=1,
#     ram_handling="Virtual",
#     save_format="Save as new XML Project (HDF5)",
#     additional_option="",
# ):
#     """run the image fusion command

#     Parameters
#     ----------
#     temp_path : str
#         temporary folder output (scratch)
#     fused_xml_path : str
#         final xml output path
#     process_timepoint : str, optional
#         Specify which timepoint should be processed, by default "All Timepoints"
#     downsampling : int, optional
#         Downsampling factor to use during the fusion, by default 1 (no
#         downsampling)
#     ram_handling : str, optional
#         Which type of ram_handling do you require, by default "Virtual". This is
#         the conservative (not likely to fail even if only a low amount of RAM is
#         available) and slow approach
#     save_format : str, optional
#         file format of the new image, by default "Save as new XML Project
#         (HDF5)", this is matching the conservative and slow approach
#     additional_option : str, optional=""
#         Any additional options that should be added to the fusion command. Do
#         not forget to finish each additional option with a space
#     """
#     # Add preserve original data anisotropy tickbox:
#     # tiles=> true; angle=>False

#     options = (
#         "select=["
#         + temp_path
#         + "] "
#         + "process_angle=[All angles] "
#         + "process_channel=[All channels] "
#         + "process_illumination=["
#         + process_timepoint
#         + "] "
#         + "process_tile=[All tiles] "
#         + "process_timepoint=[All Timepoints] "
#         + "bounding_box=[Currently Selected Views] "
#         + "downsampling="
#         + str(downsampling)
#         + " "
#         + "pixel_type=[16-bit unsigned integer] "
#         + "interpolation=[Linear Interpolation] "
#         + "image=["
#         + ram_handling
#         + "] "
#         + "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] "
#         + "blend "
#         + additional_option
#         + "produce=[Each timepoint & channel] "
#         + "fused_image=["
#         + save_format
#         + "] "
#         + "export_path=["
#         + fused_xml_path
#         + "]",
#     )

#     IJ.run("Fuse dataset ...", options)
#     return


def run_fusion(
    project_path,
    input_dict={},
    result_path=None,
    downsampling=1,
    interpolation="[Linear Interpolation]",
    pixel_type="[16-bit unsigned integer]",
    export="HDF5",
):
    """Wrapper to BigStitcher > Batch Processing > Fuse Dataset.

    Depending on the export type, inputs are different and therefore will
    distribute inputs differently.

    Parameters
    ----------
    project_path : str
        Path of the XML on which to do the fusion.
    input_dict : dict
        Dictionary containing all the required informations for angles,
        channels, illuminations, tiles and timepoints.
    result_path : str, optional
        Path to store the resulting fused image, by default None.
    downsampling : int, optional
        Downsampling value to use during fusion, by default 1.
    interpolation : str, optional
        Interpolation to use during fusion, by default "[Linear Interpolation]".
    pixel_type : str, optional
        Pixel type to use during fusion, by default "[16-bit unsigned integer]".
    export : str, optional
        Format of the output fused image, by default "HDF5".
    """

    file_info = pathtools.parse_path(project_path)
    if not result_path:
        result_path = file_info["path"]
        # if not os.path.exists(result_path):
        #     os.makedirs(result_path)

    options_dict = parse_options(input_dict)

    options = (
        "select=["
        + project_path
        + "] "
        + "process_angle="
        + options_dict["angle_text"]
        + "process_channel="
        + options_dict["channel_text"]
        + "process_illumination="
        + options_dict["illumination_text"]
        + "process_tile="
        + options_dict["tile_text"]
        + "process_timepoint="
        + options_dict["timepoint_text"]
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
            + "filename_addition=[" + file_info["basename"] + "]"
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
    return


def parse_options(input_dict):
    output_dict = {}

    if "process_channel" in input_dict:
        output_dict["channel_text"], output_dict["channel_select"] = (
            "[Single channel (Select from List)] ",
            "processing_channel=[channel "
            + str(input_dict["process_channel"] - 1)
            + "] ",
        )
    else:
        output_dict["channel_text"], output_dict["channel_select"] = (
            "[All channels] ",
            "",
        )

    if "process_illumination" in input_dict:
        output_dict["illumination_text"], output_dict["illumination_select"] = (
            "[Single illumination (Select from List)] ",
            "processing_illumination=[illumination "
            + str(input_dict["process_illumination"])
            + "] ",
        )
    else:
        output_dict["illumination_text"], output_dict["illumination_select"] = (
            "[All illuminations] ",
            "",
        )

    if "process_tile" in input_dict:
        output_dict["tile_text"], output_dict["tile_select"] = (
            "[Single tile (Select from List)] ",
            "processing_tile=[tile " + str(input_dict["process_tile"]) + "] ",
        )
    else:
        output_dict["tile_text"], output_dict["tile_select"] = ("[All tiles] ", "")

    if "process_timepoint" in input_dict:
        output_dict["timepoint_text"], output_dict["timepoint_select"] = (
            "[Single timepoint (Select from List)] ",
            "processing_timepoint=[timepoint "
            + str(input_dict["process_timepoint"])
            + "] ",
        )
    else:
        output_dict["timepoint_text"], output_dict["timepoint_select"] = (
            "[All Timepoints] ",
            "",
        )

    if "process_angle" in input_dict:
        output_dict["angle_text"], output_dict["angle_select"] = (
            "[Single angle (Select from List)] ",
            "processing_angle=[angle " + str(input_dict["process_angle"]) + "] ",
        )
    else:
        output_dict["angle_text"], output_dict["angle_select"] = ("[All angles] ", "")

    log.debug(output_dict)
    return output_dict
