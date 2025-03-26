"""Tests for the ProcessingOptions class from the imcflibs.imagej.bdv module."""

from imcflibs.imagej.bdv import ProcessingOptions


def test_defaults():
    """Test the default options by calling all formatters on a "raw" object."""
    acitt_options = (
        "process_angle=[All angles] "
        "process_channel=[All channels] "
        "process_illumination=[All illuminations] "
        "process_tile=[All tiles] "
        "process_timepoint=[All Timepoints] "
    )
    acitt_selectors = " "
    how_to_treat = (
        "how_to_treat_angles=[treat individually] "
        "how_to_treat_channels=group "
        "how_to_treat_illuminations=group "
        "how_to_treat_tiles=compare "
        "how_to_treat_timepoints=[treat individually] "
    )
    use_acitt = (
        "channels=[Average Channels] "
        "illuminations=[Average Illuminations] "
    )

    proc_opts = ProcessingOptions()

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_how_to_treat() == how_to_treat
    assert proc_opts.fmt_use_acitt() == use_acitt


def test__treat_tc_ti__ref_c1():
    """Test an example setting how to treat components using a reference channel."""
    # refers to "Example 1" from the BDV TODO list
    # FIXME: what are the actual inputs and the correct output string??
    acitt_options = (
        "process_angle=[All angles] "
        "process_channel=[All channels] "
        "process_illumination=[All illuminations] "
        "process_tile=[All tiles] "
        "process_timepoint=[All Timepoints] "
    )
    acitt_selectors = " "
    how_to_treat = (
        "how_to_treat_angles=[treat individually] "
        "how_to_treat_channels=group "
        "how_to_treat_illuminations=group "
        "how_to_treat_tiles=compare "
        "how_to_treat_timepoints=[treat individually] "
    )
    use_acitt = (
        "channels=[use Channel 1] "
        "illuminations=[Average Illuminations] "
    )

    proc_opts = ProcessingOptions()
    proc_opts.treat_tiles("compare")
    proc_opts.treat_timepoints("[treat individually]")
    proc_opts.reference_channel(1)

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_use_acitt() == use_acitt
    assert proc_opts.fmt_how_to_treat() == how_to_treat


def test__process_c1_treat_tg_ti_use_t3():
    """Test an example setting using a reference channel and a reference tile."""

    acitt_options = (
        "process_angle=[All angles] "
        "process_channel=[Single channel (Select from List)] "
        "process_illumination=[All illuminations] "
        "process_tile=[All tiles] "
        "process_timepoint=[All Timepoints] "
    )

    acitt_selectors = "processing_channel=[channel 1] "
    how_to_treat = (
        "how_to_treat_angles=[treat individually] "
        "how_to_treat_channels=group "
        "how_to_treat_illuminations=group "
        "how_to_treat_tiles=group "
        "how_to_treat_timepoints=[treat individually] "
    )
    use_acitt = (
        "channels=[Average Channels] "
        "illuminations=[Average Illuminations] "
        "tiles=[use Tile 3] "
    )

    proc_opts = ProcessingOptions()
    proc_opts.process_channel(1)
    # proc_opts.treat_timepoints("[treat individually]")
    proc_opts.treat_tiles("group")
    proc_opts.reference_tile(3)

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_use_acitt() == use_acitt
    assert proc_opts.fmt_how_to_treat() == how_to_treat
