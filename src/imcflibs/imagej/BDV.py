"""BigDataViewer related functions, mostly convenience wrappers. with simplified calls"""

from ij import IJ


def run_defineMVD(
    project_filename,
    cziPath,
    dataset_save_path,
    method="Automatic Loader (Bioformats based)",
    timepoints_per_partition=1,
    loadMethod="Re-save as multiresolution HDF5",
):
    """
    Run the Define Multi-View Dataset command

    Parameters
    ----------
    project_filename : str
        Name of the project (finishes with .xml)
    cziPath : str
        path to the first czi
    dataset_save_path : str
        output path for the .xml
    method : str, optional
        Image loader method, by default "Automatic Loader (Bioformats based)"
    timepoints_per_partition : int, optional
        split the output by timepoints. Use 0 for no split, by default 1
    loadMethod : str, optional
        Allows this function to either re-save the images or simply create a merged xml. Use "Load raw data" to avoid re-saving, by default "Re-save as multiresolution HDF5" will resave the input data
    """
    IJ.run(
        "Define Multi-View Dataset",
        "define_dataset=["
        + method
        + "]"
        + "project_filename=["
        + project_filename
        + "] "
        + "path=["
        + cziPath
        + "] "
        + "exclude=10 bioformats_series_are?=Angles "
        + "move_tiles_to_grid_(per_angle)?=[Do not move Tiles to Grid (use Metadata if available)] "
        + "how_to_load_images=["
        + loadMethod
        + "] "
        + "dataset_save_path=["
        + dataset_save_path
        + "] "
        + "check_stack_sizes apply_angle_rotation "
        + "subsampling_factors=[{ {1,1,1}, {2,2,1}, {4,4,2}, {8,8,4} }] "
        + "hdf5_chunk_sizes=[{ {32,16,8}, {16,16,16}, {16,16,16}, {16,16,16} }] "
        + "timepoints_per_partition="
        + str(timepoints_per_partition)
        + " "
        + "setups_per_partition=0 "
        + "use_deflate_compression "
        + "export_path=["
        + dataset_save_path
        + "]",
    )
    return


def run_detectInterestPoints(
    project_path,
    process_timepoint="All Timepoints",
    sigma=1.8,
    threshold=0.008,
    maximum_number=3000,
):
    """
    run the detect interest points command for registration

    Parameters
    ----------
    project_path : str
        Path to the .xml project
    process_timepoint : str, optional
        Specify which timepoint should be processed, by default "All Timepoints"
    sigma : float, optional
        Minimum sigma for interest points detection, by default 1.8
    threshold : float, optional
        Threshold value for the interest point detection, by default 0.008
    maximum_number : int, optional
        maximum_number of interest points to use, by default 3000
    """

    IJ.run(
        "Detect Interest Points for Registration",
        "select=["
        + project_path
        + "] "
        + "process_angle=[All angles] "
        + "process_channel=[All channels] "
        + "process_illumination=[All illuminations] "
        + "process_tile=[All tiles] "
        + "process_timepoint=["
        + process_timepoint
        + "] "
        + "type_of_interest_point_detection=Difference-of-Gaussian "
        + "label_interest_points=beads "
        + "limit_amount_of_detections "
        + "group_tiles group_illuminations "
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
        + str(3000)
        + " "
        + "type_of_detections_to_use=Brightest "
        + "compute_on=[CPU (Java)]",
    )
    return


def run_registration(
    project_path,
    process_timepoint="All Timepoints",
):
    """
    run the spatial registration command

    Parameters
    ----------
    project_path : str
        Path to the .xml project
    process_timepoint : str, optional
        Specify which timepoint should be processed, by default "All Timepoints"
    """

    # register using interest points
    IJ.run(
        "Register Dataset based on Interest Points",
        "select=["
        + project_path
        + "] "
        + "process_angle=[All angles] "
        + "process_channel=[All channels] "
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
        + "fix_views=[Fix first view] "
        + "map_back_views=[Do not map back (use this if views are fixed)] "
        + "transformation=Affine "
        + "regularize_model "
        + "model_to_regularize_with=Rigid "
        + "lamba=0.10 "
        + "number_of_neighbors=3 "
        + "redundancy=3 "
        + "significance=2 "
        + "allowed_error_for_ransac=5 "
        + "ransac_iterations=Normal "
        + "interestpoint_grouping=[Group interest points (simply combine all in one virtual view)] "
        + "interest=5",
    )
    return


def run_fusion(
    temp_path,
    fused_xml_path,
    process_timepoint="All Timepoints",
    downsampling=1,
    ram_handling="Virtual",
    save_format="Save as new XML Project (HDF5)",
    additional_option="",
):
    """
    run the image fusion command

    Parameters
    ----------
    temp_path : str
        temporary folder output (scratch)
    fused_xml_path : str
        final xml output path
    process_timepoint : str, optional
        Specify which timepoint should be processed, by default "All Timepoints"
    downsampling : int, optional
        Downsampling factor to use during the fusion, by default 1 (no downsampling)
    ram_handling : str, optional
        Which type of ram_handling do you require, by default "Virtual". This is the conservative (not likely to fail even if only a low amount of RAM is available) and slow approach
    save_format : str, optional
        file format of the new image, by default "Save as new XML Project (HDF5)", this is matching the conservative and slow approach
    additional_option : str, optional=""
        Any additional options that should be added to the fusion command. Do not forget to finish each additional option with a space
    """

    IJ.run(
        "Fuse dataset ...",
        "select=["
        + temp_path
        + "] "
        + "process_angle=[All angles] "
        + "process_channel=[All channels] "
        + "process_illumination=["
        + process_timepoint
        + "] "
        + "process_tile=[All tiles] "
        + "process_timepoint=[All Timepoints] "
        + "bounding_box=[Currently Selected Views] "
        + "downsampling="
        + str(downsampling)
        + " "
        + "pixel_type=[16-bit unsigned integer] "
        + "interpolation=[Linear Interpolation] "
        + "image=["
        + ram_handling
        + "] "
        + "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] "
        + "blend "
        + additional_option
        + "produce=[Each timepoint & channel] "
        + "fused_image=["
        + save_format
        + "] "
        + "export_path=["
        + fused_xml_path
        + "]",
    )
    return
