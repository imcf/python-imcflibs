import pytest

from imcflibs.imagej.bdv import ProcessingOptions


def test_defaults():
    """Test the default options by calling all fomatters on a "raw" object."""
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
        "how_to_treat_tiles=group "
        "how_to_treat_timepoints=group "
    )
    use_acitt = (
        "channels=[Average Channels] "
        "illuminations=[Average Illuminations] "
        "tiles=[Average Tiles] "
        "timepoints=[Average Timepoints] "
    )

    proc_opts = ProcessingOptions()

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_how_to_treat() == how_to_treat
    assert proc_opts.fmt_use_acitt() == use_acitt


def test__treat_tc_ti__ref_c2():
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
        "tiles=[Average Tiles] "
        "timepoints=[Average Timepoints] "
    )

    proc_opts = ProcessingOptions()
    proc_opts.treat_tiles("compare")
    proc_opts.treat_timepoints("[treat individually]")
    proc_opts.reference_channel(2)

    assert proc_opts.fmt_acitt_options() == acitt_options
    assert proc_opts.fmt_acitt_selectors() == acitt_selectors
    assert proc_opts.fmt_use_acitt() == use_acitt
    assert proc_opts.fmt_how_to_treat() == how_to_treat
