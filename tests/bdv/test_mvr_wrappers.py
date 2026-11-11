"""Tests for the MVR / BigStitcher command wrappers in the BDV module.

The expected strings use the dialog keys and choices of multiview-reconstruction
9.0.11 and BigStitcher 3.0.8.
"""

import logging

import pytest

from imcflibs.imagej import bdv

XML = "/data/project/dataset.xml"
PROCESS_ALL = (
    "process_angle=[All angles] "
    + "process_channel=[All channels] "
    + "process_illumination=[All illuminations] "
    + "process_tile=[All tiles] "
    + "process_timepoint=[All Timepoints] "
)


def norm(text):
    """Collapse runs of white space (ImageJ ignores them in macro options)."""
    return " ".join(text.split())


def last_call(caplog):
    """Return the logged (mock) `IJ.run` call, white space collapsed."""
    return norm(caplog.messages[-1])


def ij_run(cmd, options):
    """Format a (mock) `IJ.run` call as logged by `imcf-fiji-mocks`."""
    return norm("IJ.run(cmd=[%s], params=[%s])" % (cmd, options))


def test_timepoint_selection_is_capitalised():
    """The dialogs name timepoints "Timepoint", other dimensions lower-case."""
    opts = bdv.ProcessingOptions()
    opts.process_timepoint(2)
    opts.process_channel(1)
    assert "process_timepoint=[Single Timepoint (Select from List)]" in opts.fmt_acitt_options()
    assert "process_channel=[Single channel (Select from List)]" in opts.fmt_acitt_options()
    assert norm(opts.fmt_acitt_selectors()) == (
        "processing_channel=[channel 1] processing_timepoint=[Timepoint 2]"
    )


def test_timepoint_grouping_choices():
    """BigStitcher's grouping choices are spelled "TimePoint(s)"."""
    opts = bdv.ProcessingOptions()
    opts.treat_timepoints("group")
    assert "timepoints=[Average TimePoints]" in opts.fmt_use_acitt()
    opts.reference_timepoint(0)
    assert "timepoints=[use TimePoint 0]" in opts.fmt_use_acitt()


def test_fmt_ransac_options_defaults():
    """Default RANSAC options: MVR defaults, iterations with their count."""
    assert bdv.fmt_ransac_options() == (
        "allowed_error_for_ransac=5 ransac_iterations=[Normal (10,000)] "
    )


def test_fmt_ransac_options_all():
    """Inliers, inlier ratio and maximal trust (advanced RANSAC dialog)."""
    assert bdv.fmt_ransac_options(min_inliers=3, min_inlier_ratio=0.1, max_trust=4) == (
        "allowed_error_for_ransac=5 ransac_iterations=[Normal (10,000)] "
        + "minmal_number_of_inliers=3 "
        + "advanced_ransac_options filter_ransac "
        + "minimal_inlier_ratio=0.1 "
        + "maximal_trust=4 "
    )


def test_optimize_and_apply_shifts(caplog):
    """Fix groups, strategy and pre-align of the stitching optimization."""
    caplog.set_level(logging.WARNING)
    opts = bdv.ProcessingOptions()
    opts.treat_channels("compare")
    bdv.optimize_and_apply_shifts(
        XML,
        processing_opts=opts,
        relative_error=5.0,
        absolute_error=7.0,
        fix_groups=["0-0", "0-0,"],
        backup_xml=False,
    )
    expected = (
        "select=[" + XML + "] "
        + PROCESS_ALL
        + " "
        + "relative=5.0 "
        + "absolute=7.0 "
        + "global_optimization_strategy=[Two-Round using Metadata to align "
        + "unconnected Tiles and iterative dropping of bad links] "
        + "show_expert_grouping_options "
        + "illuminations=[Average Illuminations] "
        + "how_to_treat_angles=[treat individually] "
        + "how_to_treat_channels=compare "
        + "how_to_treat_illuminations=group "
        + "how_to_treat_tiles=compare "
        + "how_to_treat_timepoints=[treat individually] "
        + "fix_group_0-0 fix_group_0-0, "
        + "pre-align "
    )
    assert last_call(caplog) == ij_run("Optimize globally and apply shifts ...", expected)


def test_interest_points_registration_translation(caplog):
    """Translation per view, no grouping, limited search radius, fixed view."""
    caplog.set_level(logging.WARNING)
    bdv.interest_points_registration(
        XML,
        transformation="Translation",
        regularize_with=None,
        group_tiles=False,
        group_illuminations=False,
        group_channels=False,
        point_selection="Only compare interest points that overlap between "
        + "views (according to current transformations)",
        redundancy=2,
        search_radius=120,
        ransac_options=bdv.fmt_ransac_options(min_inliers=3),
        strategy="Two-Round: Handle unconnected tiles, remove wrong links "
        + "STRICT (2.5x / 3.5px)",
        fix_views="Fix first view",
    )
    expected = (
        "select=[" + XML + "] "
        + PROCESS_ALL
        + " "
        + "registration_algorithm=[Precise descriptor-based (translation invariant)] "
        + "registration_over_time=[Match against one reference timepoint "
        + "(no global optimization)] "
        + "registration_in_between_views=[Only compare overlapping views "
        + "(according to current transformations)] "
        + "interest_point_inclusion=[Only compare interest points that overlap "
        + "between views (according to current transformations)] "
        + "interest_points=beads "
        + "reference=1 "
        + " "
        + "fix_views=[Fix first view] "
        + "map_back_views=[Do not map back (use this if views are fixed)] "
        + "transformation=Translation "
        + "number_of_neighbors=3 "
        + "redundancy=2 "
        + "significance=3 "
        + "limit_search_radius search_radius=120 "
        + "allowed_error_for_ransac=5 ransac_iterations=[Normal (10,000)] "
        + "minmal_number_of_inliers=3 "
        + "global_optimization_strategy=[Two-Round: Handle unconnected tiles, "
        + "remove wrong links STRICT (2.5x / 3.5px)] "
        + "pre-align"
    )
    assert last_call(caplog) == ij_run("Register Dataset based on Interest Points", expected)


def test_interest_points_registration_grouped_channels(caplog):
    """Channels grouped into one virtual view, Rigid regularised with Rigid."""
    caplog.set_level(logging.WARNING)
    bdv.interest_points_registration(
        XML,
        transformation="Rigid",
        regularize_with="Rigid",
        group_tiles=False,
        group_illuminations=False,
        pre_align=False,
    )
    call = last_call(caplog)
    assert "transformation=Rigid regularize_model model_to_regularize_with=Rigid lambda=0.1 " in call
    assert (
        "group_channels interestpoint_grouping=[Group interest points (simply "
        + "combine all in one virtual view)] interest=5 "
    ) in call
    assert "group_tiles" not in call
    assert "pre-align" not in call
    assert "limit_search_radius" not in call


def test_detect_interest_points_intensity_range(caplog):
    """Fixed intensity range, own downsampling and label, no grouping."""
    caplog.set_level(logging.WARNING)
    bdv.detect_interest_points(
        XML,
        threshold=0.1,
        maximum_number=20000,
        label="cells",
        downsample_xy=4,
        downsample_z=1,
        min_intensity=290,
        max_intensity=4000,
        group_tiles=False,
    )
    call = last_call(caplog)
    assert "label_interest_points=cells " in call
    assert "downsample_xy=4x downsample_z=1x " in call
    assert "set_minimal_and_maximal_intensity minimal_intensity=290 maximal_intensity=4000 " in call
    assert "group_tiles" not in call
    assert call.startswith("IJ.run(cmd=[Detect Interest Points for Registration]")


def test_fuse_dataset_tiff(caplog):
    """TIFF fusion with a bounding box, non-rigid and a file name prefix."""
    caplog.set_level(logging.WARNING)
    bdv.fuse_dataset(
        XML,
        result_path="/data/fused",
        downsampling=29,
        export="TIFF",
        bounding_box="My Bounding Box",
        preserve_original=False,
        non_rigid_label="beads_split",
        non_rigid_cpd=2,
        filename_addition="ds29",
    )
    expected = (
        "select=[" + XML + "] "
        + PROCESS_ALL
        + " "
        + "bounding_box=[My Bounding Box] "
        + "downsampling=29 "
        + "interpolation=[Linear Interpolation] "
        + "fusion_type=[Avg, Blending] "
        + "pixel_type=[16-bit unsigned integer] "
        + "interest_points_for_non_rigid=[beads_split] "
        + "non_rigid_advanced_parameters alpha=1.0 control_point_distance=2 "
        + "produce=[Each timepoint & channel] "
        + "fused_image=[Save as (compressed) TIFF stacks] "
        + "define_input=[Auto-load from input data (values shown below)] "
        + "output_file_directory=[/data/fused/.] "
        + "filename_addition=[ds29]"
    )
    assert last_call(caplog) == ij_run("Image Fusion", expected)


def test_export_choice():
    """Export choices of MVR 9.x; HDF5 is not available."""
    assert bdv.export_choice("N5") == "[N5]"
    assert bdv.export_choice("OME-ZARR") == "[OME-ZARR v3]"
    with pytest.raises(ValueError):
        bdv.export_choice("HDF5")


def test_fuse_dataset_default_tiff(caplog):
    """The default export is (uncompressed) TIFF named after the project."""
    caplog.set_level(logging.WARNING)
    bdv.fuse_dataset(XML, result_path="/data/fused")
    call = last_call(caplog)
    assert "fused_image=[Save as (compressed) TIFF stacks] " in call
    assert "filename_addition=[dataset]" in call
    assert "compression" not in call


def test_fuse_dataset_n5(caplog):
    """N5 export: always a BDV/BigStitcher XML and a pyramid, MVR defaults."""
    caplog.set_level(logging.WARNING)
    bdv.fuse_dataset(XML, result_path="/data/fused", export="N5", output_basename="out")
    call = last_call(caplog)
    assert "export=[N5] " in call
    assert "create_a_bdv/bigstitcher create_multi-resolution " in call
    assert "n5_dataset_path=[/data/fused/out.n5] " in call
    assert "xml_output_file=[/data/fused/out.xml] " in call
    assert "interest_points_for_non_rigid=[-= Disable Non-Rigid =-] " in call
    assert "preserve_original " in call
    # MVR's initial defaults are always passed (the dialogs keep the values of
    # the previous call); the pyramid levels are left to MVR
    assert "compression=[Zstandard] " in call
    assert (
        "show_advanced_block_size_options "
        + "block_size_x=128 block_size_y=128 block_size_z=64 "
        + "block_size_factor_x=2 block_size_factor_y=2 block_size_factor_z=2 "
    ) in call
    assert "subsampling_factors" not in call
    assert "sharding" not in call


def test_fuse_dataset_n5_options(caplog):
    """N5 export with compression, block sizes and pyramid levels."""
    caplog.set_level(logging.WARNING)
    bdv.fuse_dataset(
        XML,
        result_path="/data/fused",
        export="N5",
        compression="Raw (no compression)",
        block_size=[64, 64, 32],
        block_size_factor=[4, 4, 2],
        subsampling_factors="{ {1,1,1}, {2,2,1} }",
    )
    call = last_call(caplog)
    assert "compression=[Raw (no compression)] " in call
    assert (
        "show_advanced_block_size_options "
        + "block_size_x=64 block_size_y=64 block_size_z=32 "
        + "block_size_factor_x=4 block_size_factor_y=4 block_size_factor_z=2 "
    ) in call
    assert "subsampling_factors=[{ {1,1,1}, {2,2,1} }]" in call


def test_fuse_dataset_ome_zarr(caplog):
    """OME-ZARR v3: sharding and a single container unless switched off."""
    caplog.set_level(logging.WARNING)
    bdv.fuse_dataset(XML, result_path="/data/fused", export="OME-ZARR")
    call = last_call(caplog)
    assert "export=[OME-ZARR v3] " in call
    assert "zarr_dataset_path=[/data/fused/dataset_fused.zarr] " in call
    assert "store_channels enable_sharding " in call
    bdv.fuse_dataset(
        XML, result_path="/data/fused", export="OME-ZARR", sharding=False, single_container=False
    )
    call = last_call(caplog)
    assert "store_channels" not in call
    assert "enable_sharding" not in call


def test_fuse_dataset_hdf5():
    """HDF5 export is not available in MVR 9.x."""
    with pytest.raises(ValueError):
        bdv.fuse_dataset(XML, export="HDF5")


def test_fuse_dataset_unknown_export():
    """Unknown export formats are rejected."""
    with pytest.raises(ValueError):
        bdv.fuse_dataset(XML, export="PNG")
